import gymnasium as gym
from . import agents

gym.register(
    id="Custom-Velocity-Flat-v0",
    entry_point=f"{__name__}.velocity_env:CustomVelocityEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.velocity_env_cfg:CustomVelocityFlatEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:CustomVelocityPPORunnerCfg",
    },
)
