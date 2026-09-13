"""Env config: counts, timing, command ranges, reward weights. Robot-specific stuff is in robot_cfg.py."""
from isaaclab.envs import DirectRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import ContactSensorCfg
from isaaclab.sim import SimulationCfg
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.utils import configclass

from custom_robot_rl.robot_cfg import ROBOT_CFG, LEG_JOINTS, BASE_LINK


@configclass
class CustomVelocityFlatEnvCfg(DirectRLEnvCfg):
    # timing
    episode_length_s = 20.0
    decimation = 4                       # policy at 50 Hz with dt=0.005
    action_scale = 0.25
    action_space = 12                    # = number of actuated joints; adjust
    observation_space = 48               # 3+3+3+3 + 12+12+12 for a 12-DoF quadruped; adjust
    state_space = 0

    sim: SimulationCfg = SimulationCfg(dt=1 / 200, render_interval=decimation)
    terrain = TerrainImporterCfg(prim_path="/World/ground", terrain_type="plane", collision_group=-1)
    scene: InteractiveSceneCfg = InteractiveSceneCfg(num_envs=1024, env_spacing=4.0, replicate_physics=True)

    robot = ROBOT_CFG.replace(prim_path="/World/envs/env_.*/Robot")
    contact_sensor = ContactSensorCfg(prim_path="/World/envs/env_.*/Robot/.*", history_length=3, track_air_time=True)
    base_link_name = BASE_LINK
    leg_joint_names = LEG_JOINTS

    # command ranges (m/s, rad/s)
    lin_vel_x_range = (-1.0, 1.0)
    lin_vel_y_range = (-0.5, 0.5)
    ang_vel_z_range = (-1.0, 1.0)

    # reward weights (per second). Tracking must dominate early.
    rew_track_lin_vel = 1.0
    rew_track_ang_vel = 0.5
    rew_lin_vel_z = -2.0
    rew_ang_vel_xy = -0.05
    rew_joint_torque = -2.5e-5
    rew_joint_accel = -2.5e-7
    rew_action_rate = -0.01
    rew_feet_air_time = 0.5
    rew_undesired_contact = -1.0
    rew_flat_orientation = -2.5
