# Custom-URDF RL template (Isaac Lab 2.3.x, Direct workflow)  — STATUS: unvalidated until run on a GPU box

Goal: from "I have a URDF" to "PPO is training a velocity-tracking policy" without touching Isaac Lab's source tree.
This is an external extension, the layout Isaac Lab's own `template` generator produces, trimmed to the parts you edit.

## Use
```bash
# inside the container
python3 /opt/fasttrack/tools/urdf_lint.py assets/my_robot.urdf        # fix every E* first
cd /workspace/user/custom_robot_rl && pip install -e .                 # registers the gym tasks
cd $ISAACLAB_PATH
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Custom-Velocity-Flat-v0 --headless --num_envs 512
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py  --task Custom-Velocity-Flat-v0 --num_envs 16
```

## What you edit (in order)
1. `custom_robot_rl/robot_cfg.py`: URDF path, joint name patterns, PD gains, effort limits, default pose. Everything
   that comes from your datasheet lives here. Nothing else in the template references joint names directly.
2. `custom_robot_rl/tasks/velocity/velocity_env_cfg.py`: env count, episode length, command ranges, reward weights.
3. `custom_robot_rl/tasks/velocity/velocity_env.py`: only if you need a different observation or reward structure.
4. `agents/rsl_rl_ppo_cfg.py`: PPO hyperparameters; defaults are the Anymal-C flat ones, a safe start for legged robots.

## Why the robot "只抽搐不前进" (jerks, no gait) after 5k iterations — checklist
- Effort limit too low for the mass: `urdf_lint` W2 or gains from the wrong actuator.
- Stiffness/damping: start with Kp = 20-40, Kd = 0.5-1.0 for 20-60 kg legged robots; scale with mass.
- `action_scale` 0.25-0.5 for position targets; 1.0 makes early exploration violent, policy learns to stand still.
- Reward: tracking_lin_vel weight >= 1.0 must dominate; penalties (torque, action rate) 1e-4 to 1e-2 or the policy freezes.
- Termination on base contact only; do not terminate on joint limits early in training.
