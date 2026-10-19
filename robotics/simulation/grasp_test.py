import sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))  # repo root, for robotics.*
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..')))        # robotics/, for `from vision import`

import json, time
from robotics.simulation.sim_robot import SimRobot
from robotics.game.players import Arm
from robotics.utils.track_piece import track_piece_ml
from vision import BoardVision

def main():
    config_path = 'config.json'
    positions_path = 'actions.json'
    grasp_model_path = 'model.pt' # PyTorch weights, for BoardVision
    mjcf_path = 'simulation/low_cost_robot_6dof/train_scene.xml' # MuJoCo XML, for MJRobot's kinematics

    base_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isabs(config_path):
        config_path = os.path.abspath(os.path.join(base_dir, config_path))
    if not os.path.isabs(positions_path):
        positions_path = os.path.abspath(os.path.join(base_dir, positions_path))
    if not os.path.isabs(grasp_model_path):
        grasp_model_path = os.path.abspath(os.path.join(base_dir, grasp_model_path))
    if not os.path.isabs(mjcf_path):
        mjcf_path = os.path.abspath(os.path.join(base_dir, mjcf_path))

    with open(config_path, 'r') as f:
        config = json.load(f)
        arm_config = config['arm']

    vision = BoardVision(main=False, cam=0, use_yolo=False, grasp_model_path=grasp_model_path)

    arm = SimRobot(piece='o', config_path=config_path, positions_path=positions_path,
                  vision=vision, model_path=mjcf_path)
    arm.move_piece_precise(start='2', end='A')

main()
