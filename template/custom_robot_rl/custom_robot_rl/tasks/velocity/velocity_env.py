"""Direct RL env: velocity tracking on flat ground for any legged URDF.

Mirrors Isaac Lab's Anymal-C direct example, with robot specifics pulled from robot_cfg.py so you never edit this
file to swap robots. If you do need to change observations/rewards, this is the only file to touch.
"""
from __future__ import annotations

import torch
import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation
from isaaclab.envs import DirectRLEnv
from isaaclab.sensors import ContactSensor
from isaaclab.utils.math import quat_apply_inverse

from .velocity_env_cfg import CustomVelocityFlatEnvCfg


class CustomVelocityEnv(DirectRLEnv):
    cfg: CustomVelocityFlatEnvCfg

    def __init__(self, cfg: CustomVelocityFlatEnvCfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)
        self._actions = torch.zeros(self.num_envs, self.cfg.action_space, device=self.device)
        self._prev_actions = torch.zeros_like(self._actions)
        self._commands = torch.zeros(self.num_envs, 3, device=self.device)
        self._joint_ids, _ = self._robot.find_joints(self.cfg.leg_joint_names)
        self._base_id, _ = self._contact_sensor.find_bodies(self.cfg.base_link_name)
        self._feet_ids, _ = self._contact_sensor.find_bodies(".*_foot")          # EDIT if your feet are named differently
        self._undesired_ids, _ = self._contact_sensor.find_bodies(".*_thigh|.*_calf")  # EDIT
        self._episode_sums = {k: torch.zeros(self.num_envs, device=self.device) for k in [
            "track_lin_vel", "track_ang_vel", "lin_vel_z", "ang_vel_xy", "joint_torque", "joint_accel",
            "action_rate", "feet_air_time", "undesired_contact", "flat_orientation"]}

    def _setup_scene(self):
        self._robot = Articulation(self.cfg.robot)
        self.scene.articulations["robot"] = self._robot
        self._contact_sensor = ContactSensor(self.cfg.contact_sensor)
        self.scene.sensors["contact_sensor"] = self._contact_sensor
        self.cfg.terrain.num_envs = self.scene.cfg.num_envs
        self.cfg.terrain.env_spacing = self.scene.cfg.env_spacing
        self._terrain = self.cfg.terrain.class_type(self.cfg.terrain)
        self.scene.clone_environments(copy_from_source=False)
        self.scene.filter_collisions(global_prim_paths=[self.cfg.terrain.prim_path])
        light = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
        light.func("/World/Light", light)

    def _pre_physics_step(self, actions: torch.Tensor):
        self._actions = actions.clone()
        self._processed_actions = self.cfg.action_scale * self._actions + self._robot.data.default_joint_pos[:, self._joint_ids]

    def _apply_action(self):
        self._robot.set_joint_position_target(self._processed_actions, joint_ids=self._joint_ids)

    def _get_observations(self) -> dict:
        self._prev_actions = self._actions.clone()
        r = self._robot.data
        obs = torch.cat([
            r.root_lin_vel_b, r.root_ang_vel_b, r.projected_gravity_b, self._commands,
            (r.joint_pos - r.default_joint_pos)[:, self._joint_ids], r.joint_vel[:, self._joint_ids], self._actions,
        ], dim=-1)
        return {"policy": obs}

    def _get_rewards(self) -> torch.Tensor:
        r = self._robot.data; c = self.cfg
        lin_err = torch.sum(torch.square(self._commands[:, :2] - r.root_lin_vel_b[:, :2]), dim=1)
        ang_err = torch.square(self._commands[:, 2] - r.root_ang_vel_b[:, 2])
        first_contact = self._contact_sensor.compute_first_contact(self.step_dt)[:, self._feet_ids]
        last_air = self._contact_sensor.data.last_air_time[:, self._feet_ids]
        air_time = torch.sum((last_air - 0.5) * first_contact, dim=1) * (torch.norm(self._commands[:, :2], dim=1) > 0.1)
        net_f = self._contact_sensor.data.net_forces_w_history
        undesired = torch.sum((torch.max(torch.norm(net_f[:, :, self._undesired_ids], dim=-1), dim=1)[0] > 1.0), dim=1)
        terms = {
            "track_lin_vel": torch.exp(-lin_err / 0.25) * c.rew_track_lin_vel,
            "track_ang_vel": torch.exp(-ang_err / 0.25) * c.rew_track_ang_vel,
            "lin_vel_z": torch.square(r.root_lin_vel_b[:, 2]) * c.rew_lin_vel_z,
            "ang_vel_xy": torch.sum(torch.square(r.root_ang_vel_b[:, :2]), dim=1) * c.rew_ang_vel_xy,
            "joint_torque": torch.sum(torch.square(r.applied_torque[:, self._joint_ids]), dim=1) * c.rew_joint_torque,
            "joint_accel": torch.sum(torch.square(r.joint_acc[:, self._joint_ids]), dim=1) * c.rew_joint_accel,
            "action_rate": torch.sum(torch.square(self._actions - self._prev_actions), dim=1) * c.rew_action_rate,
            "feet_air_time": air_time * c.rew_feet_air_time,
            "undesired_contact": undesired * c.rew_undesired_contact,
            "flat_orientation": torch.sum(torch.square(r.projected_gravity_b[:, :2]), dim=1) * c.rew_flat_orientation,
        }
        reward = torch.sum(torch.stack(list(terms.values())), dim=0) * self.step_dt
        for k, v in terms.items(): self._episode_sums[k] += v
        return reward

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        time_out = self.episode_length_buf >= self.max_episode_length - 1
        net_f = self._contact_sensor.data.net_forces_w_history
        died = torch.any(torch.max(torch.norm(net_f[:, :, self._base_id], dim=-1), dim=1)[0] > 1.0, dim=1)
        return died, time_out

    def _reset_idx(self, env_ids: torch.Tensor | None):
        if env_ids is None or len(env_ids) == self.num_envs:
            env_ids = self._robot._ALL_INDICES
        self._robot.reset(env_ids)
        super()._reset_idx(env_ids)
        self._actions[env_ids] = 0.0; self._prev_actions[env_ids] = 0.0
        c = self.cfg
        self._commands[env_ids, 0].uniform_(*c.lin_vel_x_range)
        self._commands[env_ids, 1].uniform_(*c.lin_vel_y_range)
        self._commands[env_ids, 2].uniform_(*c.ang_vel_z_range)
        jp = self._robot.data.default_joint_pos[env_ids]; jv = self._robot.data.default_joint_vel[env_ids]
        root = self._robot.data.default_root_state[env_ids].clone()
        root[:, :3] += self._terrain.env_origins[env_ids]
        self._robot.write_root_pose_to_sim(root[:, :7], env_ids)
        self._robot.write_root_velocity_to_sim(root[:, 7:], env_ids)
        self._robot.write_joint_state_to_sim(jp, jv, None, env_ids)
        extras = {}
        for k in self._episode_sums:
            extras["Episode_Reward/" + k] = torch.mean(self._episode_sums[k][env_ids]) / self.max_episode_length_s
            self._episode_sums[k][env_ids] = 0.0
        self.extras["log"] = extras
