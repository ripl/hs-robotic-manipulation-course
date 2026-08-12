import argparse
import json
import os
import re
import sys
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parents[2]
ML_DIR = Path(__file__).resolve().parent
DEFAULT_MAPPING_PATH = ML_DIR / "teachable_machine_actions.json"
DEFAULT_CONFIG_PATH = BASE_DIR / "robotics" / "config.json"
DEFAULT_ACTIONS_PATH = BASE_DIR / "robotics" / "actions.json"
POSE_SEQUENCE = ["hover", "pre-grasp", "grasp", "post-grasp"]
REQUIRED_ARM_FIELDS = [
    "device_name",
    "servo_ids",
    "velocity_limit",
    "max_position_limit",
    "min_position_limit",
    "position_p_gain",
    "position_i_gain",
    "home_pos",
]
REQUIRED_LABELS = ["red object", "blue object", "empty", "unknown"]


class PreflightError(ValueError):
    """Raised when a bridge configuration is unsafe or incomplete."""


def load_json(path):
    with Path(path).open() as file:
        return json.load(file)


def device_exists(device_name):
    """Check a serial-device name without assuming a particular operating system."""
    if Path(device_name).exists():
        return True

    # Windows serial ports are names such as COM3, not filesystem paths.
    if re.fullmatch(r"COM\\d+", str(device_name), flags=re.IGNORECASE):
        try:
            from serial.tools import list_ports
        except ImportError:
            return False
        return any(port.device.lower() == device_name.lower() for port in list_ports.comports())
    return False


class ActionRunner:
    def __init__(
        self,
        mapping_path,
        config_path,
        actions_path,
        execute=False,
        empty_rearm_frames=12,
    ):
        self.mapping_path = Path(mapping_path)
        self.config_path = Path(config_path)
        self.actions_path = Path(actions_path)
        self.execute = execute
        self.empty_rearm_frames = empty_rearm_frames
        self.mapping = load_json(self.mapping_path)
        self.robot = None
        self.arm_config = None
        self.actions = None
        self.armed = True
        self.last_sort_label = None

    def preflight(self, check_device=True):
        """Validate files and pose references without initializing or moving the robot."""
        try:
            config = load_json(self.config_path)
            actions = load_json(self.actions_path)
        except FileNotFoundError as error:
            raise PreflightError(f"Required file not found: {error.filename}") from error
        except json.JSONDecodeError as error:
            raise PreflightError(f"Invalid JSON: {error}") from error

        if not isinstance(config, dict) or not isinstance(config.get("arm"), dict):
            raise PreflightError(f'{self.config_path} must contain an "arm" object.')
        arm_config = config["arm"]
        missing_fields = [field for field in REQUIRED_ARM_FIELDS if field not in arm_config]
        if missing_fields:
            raise PreflightError(
                f'{self.config_path} arm configuration is missing: {", ".join(missing_fields)}.'
            )

        servo_ids = arm_config["servo_ids"]
        if not isinstance(servo_ids, list) or not servo_ids:
            raise PreflightError("arm.servo_ids must be a non-empty list.")
        joint_count = len(servo_ids)

        if check_device and not device_exists(arm_config["device_name"]):
            raise PreflightError(
                f'Serial device not found: {arm_config["device_name"]}. '
                "Check the USB cable, power, driver, and config.json device_name."
            )

        if not isinstance(actions, dict):
            raise PreflightError(f"{self.actions_path} must contain a JSON object.")
        if not isinstance(self.mapping, dict):
            raise PreflightError(f"{self.mapping_path} must contain a JSON object.")

        for label in REQUIRED_LABELS:
            if label not in self.mapping:
                raise PreflightError(f'{self.mapping_path} is missing required label "{label}".')

        for label, entry in self.mapping.items():
            if label.startswith("_"):
                continue
            self._validate_mapping_entry(label, entry, actions, joint_count)

        self.arm_config = arm_config
        self.actions = actions
        return {
            "ok": True,
            "mapping": str(self.mapping_path),
            "actions": str(self.actions_path),
            "device": arm_config["device_name"],
            "servo_count": joint_count,
            "labels": [label for label in self.mapping if not label.startswith("_")],
        }

    def _validate_mapping_entry(self, label, entry, actions, joint_count):
        if entry is None:
            return
        if isinstance(entry, str):
            entry = {"action": entry}
        if not isinstance(entry, dict):
            raise PreflightError(f'Mapping for "{label}" must be an object, string, or null.')

        action = entry.get("action")
        sequence = entry.get("sequence")
        if action is not None and sequence:
            raise PreflightError(f'Mapping for "{label}" cannot contain both action and sequence.')
        if action is None and not sequence:
            return

        if action is not None:
            self._validate_action(action, actions, joint_count)
        else:
            if not isinstance(sequence, list) or not sequence:
                raise PreflightError(f'Mapping sequence for "{label}" must be a non-empty list.')
            for index, step in enumerate(sequence):
                if not isinstance(step, dict):
                    raise PreflightError(f'Mapping step {index} for "{label}" must be an object.')
                action_name = step.get("action")
                pose = step.get("pose")
                if not isinstance(action_name, str) or not isinstance(pose, str):
                    raise PreflightError(
                        f'Mapping step {index} for "{label}" needs string action and pose fields.'
                    )
                self._validate_pose(action_name, pose, actions, joint_count)

        if label in {"empty", "unknown"}:
            raise PreflightError(f'"{label}" must be mapped to no action for safety.')

    def _validate_action(self, action_name, actions, joint_count):
        if not isinstance(action_name, str):
            raise PreflightError("Action names must be strings.")
        for pose in POSE_SEQUENCE:
            self._validate_pose(action_name, pose, actions, joint_count)

    def _validate_pose(self, action_name, pose, actions, joint_count):
        if action_name not in actions:
            raise PreflightError(f'Action "{action_name}" is not in {self.actions_path}.')
        action = actions[action_name]
        if not isinstance(action, dict) or pose not in action:
            raise PreflightError(f'Action "{action_name}" is missing pose "{pose}".')
        position = action[pose]
        if not isinstance(position, list) or len(position) != joint_count:
            raise PreflightError(
                f'Action "{action_name}" pose "{pose}" must contain {joint_count} joint values.'
            )
        if not all(isinstance(value, (int, float)) for value in position):
            raise PreflightError(f'Action "{action_name}" pose "{pose}" contains a non-numeric value.')

    def _ensure_robot(self):
        if self.robot is not None:
            return
        if self.arm_config is None or self.actions is None:
            self.preflight(check_device=True)

        sys.path.insert(0, str(BASE_DIR))
        from robotics.robot.robot import Robot

        self.robot = Robot(
            device_name=self.arm_config["device_name"],
            baudrate=self.arm_config.get("baudrate", 1_000_000),
            servo_ids=self.arm_config["servo_ids"],
            velocity_limit=self.arm_config["velocity_limit"],
            max_position_limit=self.arm_config["max_position_limit"],
            min_position_limit=self.arm_config["min_position_limit"],
            position_p_gain=self.arm_config["position_p_gain"],
            position_i_gain=self.arm_config["position_i_gain"],
        )
        self.robot.set_and_wait_goal_pos(self.arm_config["home_pos"])

    def close(self):
        if self.robot is None:
            return
        try:
            if self.arm_config and "rest_pos" in self.arm_config:
                self.robot.set_and_wait_goal_pos(self.arm_config["rest_pos"])
        finally:
            self.robot._disable_torque()
            self.robot = None

    def rearm(self, reason="operator"):
        self.armed = True
        self.last_sort_label = None
        return {"ok": True, "mode": "rearmed", "reason": reason, "armed": self.armed}

    def _mapping_for_label(self, label):
        entry = self.mapping.get(label)
        if entry is None:
            return {"action": None, "reason": "No mapped action for class label."}
        if isinstance(entry, str):
            return {"action": entry}
        if isinstance(entry, dict):
            return entry
        return {"action": None, "reason": "Mapping entry must be a string, object, or null."}

    def run(self, label, probability, stable_frames=0):
        entry = self._mapping_for_label(label)
        action = entry.get("action")
        sequence = entry.get("sequence")

        if action is None and not sequence:
            rearmed = False
            if label == "empty" and stable_frames >= self.empty_rearm_frames and not self.armed:
                self.rearm(reason="stable empty prediction")
                rearmed = True
            return {
                "ok": True,
                "mode": "no_action",
                "label": label,
                "probability": probability,
                "armed": self.armed,
                "rearmed": rearmed,
                "reason": entry.get("reason") or entry.get("description") or "Class is mapped to no action.",
            }

        if not self.armed:
            return {
                "ok": True,
                "mode": "suppressed",
                "label": label,
                "probability": probability,
                "armed": False,
                "reason": "Sorting is latched after the previous sort. Show stable empty or use Re-arm.",
            }

        # Latch before executing so an error cannot cause repeated movement requests.
        self.armed = False
        self.last_sort_label = label
        if not self.execute:
            return {
                "ok": True,
                "mode": "dry_run",
                "label": label,
                "probability": probability,
                "mapped": entry,
                "armed": False,
                "message": "Dry run only. Start bridge with --execute to move the robot.",
            }

        try:
            self._ensure_robot()
            if sequence:
                self._run_sequence(sequence)
            else:
                self._run_action(action)
            if self.arm_config and "home_pos" in self.arm_config:
                self.robot.set_and_wait_goal_pos(self.arm_config["home_pos"])
        except Exception:
            self.close()
            raise

        return {
            "ok": True,
            "mode": "executed",
            "label": label,
            "probability": probability,
            "mapped": entry,
            "armed": False,
        }

    def _run_action(self, action_name):
        for pose in POSE_SEQUENCE:
            self.robot.set_and_wait_goal_pos(self.actions[action_name][pose])
            time.sleep(0.25)

    def _run_sequence(self, sequence):
        for step in sequence:
            delay = float(step.get("delay", 0.25))
            self.robot.set_and_wait_goal_pos(self.actions[step["action"]][step["pose"]])
            time.sleep(delay)


def make_handler(runner, args):
    class BridgeHandler(SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            super().end_headers()

        def do_OPTIONS(self):
            self.send_response(204)
            self.end_headers()

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/health":
                self._send_json({
                    "ok": True,
                    "execute": args.execute,
                    "armed": runner.armed,
                    "empty_rearm_frames": args.empty_rearm_frames,
                    "mapping": str(args.mapping),
                    "actions": str(args.actions),
                })
                return
            if parsed.path in ["/", "/index.html"]:
                self._send_file(ML_DIR / "teachable_machine_demo.html", "text/html")
                return
            super().do_GET()

        def do_HEAD(self):
            parsed = urlparse(self.path)
            if parsed.path in ["/", "/index.html"]:
                self._send_file_headers(ML_DIR / "teachable_machine_demo.html", "text/html")
                return
            super().do_HEAD()

        def do_POST(self):
            parsed = urlparse(self.path)
            try:
                if parsed.path == "/rearm":
                    self._send_json(runner.rearm())
                    return
                if parsed.path != "/prediction":
                    self.send_error(404, "Unknown endpoint")
                    return

                content_length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                label = payload["className"]
                probability = float(payload["probability"])
                stable_frames = int(payload.get("stableFrames", 0))
                result = runner.run(label, probability, stable_frames)
                self._send_json(result)
                print(f'[{result["mode"]}] {label} ({probability:.2f}) -> {result.get("mapped", result.get("reason"))}')
            except Exception as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=400)
                print(f"[error] {exc}")

        def _send_json(self, data, status=200):
            body = json.dumps(data, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_file(self, path, content_type):
            body = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_file_headers(self, path, content_type):
            body_size = path.stat().st_size
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(body_size))
            self.end_headers()

    return BridgeHandler


def parse_args():
    parser = argparse.ArgumentParser(description="Local Teachable Machine to robot-action bridge.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--mapping", type=Path, default=DEFAULT_MAPPING_PATH)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--actions", type=Path, default=DEFAULT_ACTIONS_PATH)
    parser.add_argument("--execute", action="store_true", help="Physically move the robot. Off by default.")
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Validate config, serial device, mapping, and poses without initializing or moving the arm.",
    )
    parser.add_argument(
        "--skip-device-check",
        action="store_true",
        help="Skip serial-device presence checking during --preflight (useful for CI only).",
    )
    parser.add_argument(
        "--empty-rearm-frames",
        type=int,
        default=12,
        help="Stable empty frames required to re-arm after a sort.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.empty_rearm_frames < 1:
        raise SystemExit("--empty-rearm-frames must be at least 1.")

    runner = ActionRunner(
        args.mapping,
        args.config,
        args.actions,
        execute=args.execute,
        empty_rearm_frames=args.empty_rearm_frames,
    )
    if args.preflight or args.execute:
        try:
            result = runner.preflight(check_device=not args.skip_device_check)
        except PreflightError as error:
            raise SystemExit(f"Preflight failed: {error}") from error
        if args.preflight:
            print(json.dumps(result, indent=2))
            return

    os.chdir(ML_DIR)
    handler = make_handler(runner, args)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    mode = "EXECUTE" if args.execute else "DRY RUN"
    print(f"Teachable Machine bridge running in {mode} mode.", flush=True)
    print(f"Open http://{args.host}:{args.port}/", flush=True)
    print("Press Control-C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping bridge...")
    finally:
        runner.close()
        server.server_close()


if __name__ == "__main__":
    main()
