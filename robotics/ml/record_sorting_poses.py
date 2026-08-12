"""Safely record the fixed pickup and bin poses for the sorting demo."""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
ML_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = BASE_DIR / "robotics" / "config.json"
DEFAULT_ACTIONS_PATH = BASE_DIR / "robotics" / "actions.json"
LOCATIONS = ["pickup", "red_bin", "blue_bin"]
POSES = ["hover", "pre-grasp", "grasp", "post-grasp"]


def load_json(path):
    with Path(path).open() as file:
        return json.load(file)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Record pickup, red-bin, and blue-bin poses without replacing existing actions."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--actions", type=Path, default=DEFAULT_ACTIONS_PATH)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing pickup/red_bin/blue_bin entries after making a backup.",
    )
    parser.add_argument(
        "--return-home",
        action="store_true",
        help="Move to rest_pos after recording. Off by default because it moves the arm.",
    )
    return parser.parse_args()


def backup_actions(actions_path):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = actions_path.with_name(f"{actions_path.stem}.{timestamp}.backup{actions_path.suffix}")
    shutil.copy2(actions_path, backup_path)
    return backup_path


def robot_from_config(config):
    sys.path.insert(0, str(BASE_DIR))
    from robotics.robot.robot import Robot

    arm = config["arm"]
    return Robot(
        device_name=arm["device_name"],
        baudrate=arm.get("baudrate", 1_000_000),
        servo_ids=arm["servo_ids"],
        velocity_limit=arm["velocity_limit"],
        max_position_limit=arm["max_position_limit"],
        min_position_limit=arm["min_position_limit"],
        position_p_gain=arm["position_p_gain"],
        position_i_gain=arm["position_i_gain"],
    )


def record_pose(robot, location, pose):
    print(f"\n{location} — {pose}")
    print("Torque will be disabled. Move the arm manually to the described pose.")
    input("When the workspace is clear, press Enter to disable torque. ")
    robot._disable_torque()
    input("Move the arm, then press Enter to save this six-servo position. ")
    position = [int(value) for value in robot.read_position()]
    print(f"Recorded: {position}")
    return position


def main():
    args = parse_args()
    config = load_json(args.config)
    if not isinstance(config, dict) or "arm" not in config:
        raise SystemExit(f'{args.config} must contain an "arm" object.')

    if args.actions.exists():
        actions = load_json(args.actions)
    else:
        actions = {}
    if not isinstance(actions, dict):
        raise SystemExit(f"{args.actions} must contain a JSON object.")

    existing = [location for location in LOCATIONS if location in actions]
    if existing and not args.overwrite:
        raise SystemExit(
            "Refusing to overwrite existing sorting locations: "
            f"{', '.join(existing)}. Re-run with --overwrite after checking them."
        )

    robot = None
    try:
        robot = robot_from_config(config)
        print("\nRecord the fixed physical layout without moving the camera, pickup spot, or bins.")
        recorded = {}
        for location in LOCATIONS:
            print(f"\n=== Recording {location} ===")
            recorded[location] = {pose: record_pose(robot, location, pose) for pose in POSES}

        if args.actions.exists():
            backup_path = backup_actions(args.actions)
            print(f"Backed up existing actions to {backup_path}")
        actions.update(recorded)
        args.actions.write_text(json.dumps(actions, indent=2) + "\n")
        print(f"Saved sorting poses to {args.actions}")
    finally:
        if robot is not None:
            try:
                if args.return_home and "rest_pos" in config["arm"]:
                    robot.set_and_wait_goal_pos(config["arm"]["rest_pos"])
            finally:
                robot._disable_torque()


if __name__ == "__main__":
    main()
