import importlib.util
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from unittest import mock
from types import SimpleNamespace
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
            "sorting_calibrated": True,
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
            min_stable_frames=3,
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
        self.assertEqual(runner.run("empty", 0.99, stable_frames=2)["mode"], "rejected")
        self.assertTrue(runner.run("empty", 0.99, stable_frames=3)["rearmed"])
        self.assertEqual(runner.run("blue object", 0.99, stable_frames=3)["mode"], "dry_run")

    def test_preflight_rejects_missing_pose(self):
        actions = valid_actions()
        del actions["red_bin"]["grasp"]
        self.actions_path.write_text(json.dumps(actions))
        with self.assertRaisesRegex(BRIDGE.PreflightError, 'red_bin.*grasp'):
            self.runner().preflight(check_device=False)

    def test_server_enforces_confidence_and_stability(self):
        runner = self.runner()
        self.assertEqual(runner.run("red object", 0.84, stable_frames=10)["mode"], "rejected")
        self.assertEqual(runner.run("red object", 0.99, stable_frames=2)["mode"], "rejected")
        self.assertTrue(runner.armed)

    def test_busy_runner_rejects_rearm_and_second_motion(self):
        runner = self.runner()
        runner._motion_lock.acquire()
        try:
            self.assertEqual(runner.rearm()["mode"], "busy")
            self.assertEqual(runner.run("red object", 0.99, stable_frames=3)["mode"], "busy")
        finally:
            runner._motion_lock.release()

    def test_preflight_rejects_pose_outside_joint_limits(self):
        actions = valid_actions()
        actions["red_bin"]["grasp"] = [5000] * 6
        self.actions_path.write_text(json.dumps(actions))
        with self.assertRaisesRegex(BRIDGE.PreflightError, "outside configured limits"):
            self.runner().preflight(check_device=False)

    def test_windows_com_port_is_detected_without_filesystem_lookup(self):
        with mock.patch.object(
            BRIDGE,
            "list_serial_ports",
            return_value=[{"device": "COM3", "description": "USB", "manufacturer": None, "vid": None, "pid": None}],
        ):
            self.assertTrue(BRIDGE.device_exists("com3"))

    def test_http_health_and_prediction_validation(self):
        runner = self.runner()
        args = SimpleNamespace(
            execute=False,
            empty_rearm_frames=3,
            min_confidence=0.85,
            min_stable_frames=3,
            mapping=self.mapping_path,
            actions=self.actions_path,
            config=self.config_path,
        )
        server = BRIDGE.ThreadingHTTPServer(("127.0.0.1", 0), BRIDGE.make_handler(runner, args))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{server.server_port}"
        try:
            response = urllib.request.urlopen(base_url + "/health")
            health = json.loads(response.read())
            self.assertFalse(health["execute"])
            self.assertIsNone(response.headers.get("Access-Control-Allow-Origin"))
            request = urllib.request.Request(
                base_url + "/prediction",
                data=json.dumps({"className": "red object", "probability": 2, "stableFrames": 3}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(request)
            self.assertEqual(error.exception.code, 400)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
