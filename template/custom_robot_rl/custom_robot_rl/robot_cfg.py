"""EDIT ME. Everything robot-specific lives here.

Isaac Lab 2.3.x API: isaaclab.assets.ArticulationCfg + sim_utils.UrdfFileCfg import the URDF to USD on first spawn.
"""
import os
import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
URDF_PATH = os.path.join(ASSETS_DIR, "my_robot.urdf")   # <- your file. Run urdf_lint.py on it first.

# Joint-name regexes. Check with: grep '<joint name' my_robot.urdf
LEG_JOINTS = [".*_hip_joint", ".*_thigh_joint", ".*_calf_joint"]   # Unitree-style naming as example
BASE_LINK = "base"

# Datasheet numbers. These three lines cause most "jerks but never walks" failures.
EFFORT_LIMIT = 23.5    # N*m
VELOCITY_LIMIT = 30.0  # rad/s
STIFFNESS = 25.0       # Kp
DAMPING = 0.5          # Kd

DEFAULT_JOINT_POS = {   # standing pose; must not intersect the ground
    ".*_hip_joint": 0.0,
    ".*_thigh_joint": 0.8,
    ".*_calf_joint": -1.5,
}
INIT_HEIGHT = 0.42      # m, base above ground at reset. Too low = clipping through floor = NaN.

ROBOT_CFG = ArticulationCfg(
    spawn=sim_utils.UrdfFileCfg(
        asset_path=URDF_PATH,
        fix_base=False,
        merge_fixed_joints=True,
        make_instanceable=True,          # required for thousands of envs
        joint_drive=sim_utils.UrdfConverterCfg.JointDriveCfg(
            gains=sim_utils.UrdfConverterCfg.JointDriveCfg.PDGainsCfg(stiffness=STIFFNESS, damping=DAMPING),
            target_type="position",
        ),
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False, retain_accelerations=False, linear_damping=0.0, angular_damping=0.0,
            max_linear_velocity=100.0, max_angular_velocity=100.0, max_depenetration_velocity=1.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False, solver_position_iteration_count=4, solver_velocity_iteration_count=0,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(pos=(0.0, 0.0, INIT_HEIGHT), joint_pos=DEFAULT_JOINT_POS, joint_vel={".*": 0.0}),
    soft_joint_pos_limit_factor=0.9,
    actuators={
        "legs": ImplicitActuatorCfg(
            joint_names_expr=LEG_JOINTS,
            effort_limit_sim=EFFORT_LIMIT, velocity_limit_sim=VELOCITY_LIMIT,
            stiffness=STIFFNESS, damping=DAMPING,
        ),
    },
)
