import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


BRIDGE_PATH = Path(__file__).resolve().parents[1] / "teachable_machine_bridge.py"
SPEC = importlib.util.spec_from_file_location("teachable_machine_bridge", BRIDGE_PATH)
BRIDGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BRIDGE)


def valid_actions():
    pose = [2048, 1800, 1600, 1200, 2048, 2200]
    return {
        location: {name: pose for name in BRIDGE.POSE_SEQUENCE}
        for location in ("pickup", "red_bin", "blue_bin")
    }


def valid_mapping():
    def sequence(destination):
        return [
            {"action": "pickup", "pose": "hover"},
            {"action": "pickup", "pose": "pre-grasp"},
            {"action": "pickup", "pose": "grasp"},
            {"action": "pickup", "pose": "post-grasp"},
            {"action": destination, "pose": "post-grasp"},
            {"action": destination, "pose": "grasp"},
            {"action": destination, "pose": "pre-grasp"},
            {"action": destination, "pose": "hover"},
        ]

    return {
        "red object": {"sequence": sequence("red_bin")},
        "blue object": {"sequence": sequence("blue_bin")},
        "empty": {"action": None},
        "unknown": {"action": None},
    }


def valid_config():
    return {
        "arm": {
            "device_name": "/does/not/matter/in/tests",
            "servo_ids": [1, 2, 3, 4, 5, 6],
            "velocity_limit": [20] * 6,
            "max_position_limit": [4096] * 6,
            "min_position_limit": [0] * 6,
            "position_p_gain": [640] * 6,
            "position_i_gain": [10] * 6,
            "home_pos": [2048] * 6,
        }
    }


class TeachableMachineBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.mapping_path = root / "mapping.json"
        self.config_path = root / "config.json"
        self.actions_path = root / "actions.json"
        self.mapping_path.write_text(json.dumps(valid_mapping()))
        self.config_path.write_text(json.dumps(valid_config()))
        self.actions_path.write_text(json.dumps(valid_actions()))

    def tearDown(self):
        self.temp_dir.cleanup()

    def runner(self, empty_rearm_frames=3):
        return BRIDGE.ActionRunner(
            self.mapping_path,
            self.config_path,
            self.actions_path,
            empty_rearm_frames=empty_rearm_frames,
        )

    def test_preflight_accepts_complete_sorting_configuration(self):
        result = self.runner().preflight(check_device=False)
        self.assertTrue(result["ok"])
        self.assertEqual(result["servo_count"], 6)

    def test_empty_and_unknown_never_move(self):
        runner = self.runner()
        for label in ("empty", "unknown"):
            result = runner.run(label, 0.99, stable_frames=10)
            self.assertEqual(result["mode"], "no_action")
            self.assertTrue(result["armed"])

    def test_sort_is_latched_until_stable_empty_rearms_it(self):
        runner = self.runner(empty_rearm_frames=3)
        self.assertEqual(runner.run("red object", 0.99, stable_frames=3)["mode"], "dry_run")
        self.assertEqual(runner.run("blue object", 0.99, stable_frames=3)["mode"], "suppressed")
        self.assertFalse(runner.run("empty", 0.99, stable_frames=2)["rearmed"])
        self.assertTrue(runner.run("empty", 0.99, stable_frames=3)["rearmed"])
        self.assertEqual(runner.run("blue object", 0.99, stable_frames=3)["mode"], "dry_run")

    def test_preflight_rejects_missing_pose(self):
        actions = valid_actions()
        del actions["red_bin"]["grasp"]
        self.actions_path.write_text(json.dumps(actions))
        with self.assertRaisesRegex(BRIDGE.PreflightError, 'red_bin.*grasp'):
            self.runner().preflight(check_device=False)


if __name__ == "__main__":
    unittest.main()
