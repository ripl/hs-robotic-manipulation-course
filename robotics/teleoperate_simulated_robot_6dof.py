from pathlib import Path
import sys
import threading
import time

import mujoco.viewer
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ROBOTICS = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROBOTICS) not in sys.path:
    sys.path.insert(0, str(ROBOTICS))

from robot.robot import Robot
from simulation.interface import SimulatedRobot

# Per-joint sign mapping from leader hardware to MuJoCo model joints.
# Joint 3 is kept positive so elbow direction matches the real robot.
JOINT_SIGNS = np.array([1, -1, 1, 1, -1, -1], dtype=float)


def read_leader_position():
    global target_pos
    while True:
        target_pos = np.array(leader.read_position())
        target_pos = (target_pos / 2048 - 1) * 3.14
        target_pos = target_pos * JOINT_SIGNS


leader = Robot('/dev/ttyACM0', servo_ids=[1, 2, 3, 4, 5, 6])

scene_path = Path(__file__).resolve().parent / "simulation" / "low_cost_robot_6dof" / "scene.xml"
m = mujoco.MjModel.from_xml_path(str(scene_path))
d = mujoco.MjData(m)

r = SimulatedRobot(m, d)

target_pos = np.zeros(6)

# Start the thread for reading leader position.
leader_thread = threading.Thread(target=read_leader_position, daemon=True)
leader_thread.start()

with mujoco.viewer.launch_passive(m, d) as viewer:
    while viewer.is_running():
        # Use the latest target_pos.
        step_start = time.time()
        target_pos_local = target_pos.copy()

        r.set_target_pos(target_pos_local)
        mujoco.mj_step(m, d)
        viewer.sync()

        # Rudimentary time keeping, will drift relative to wall clock.
        time_until_next_step = m.opt.timestep - (time.time() - step_start)
        if time_until_next_step > 0:
            time.sleep(time_until_next_step)