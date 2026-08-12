# Teachable Machine Bridge

This folder contains the portable local application for the Teachable Machine robotics activity.

The browser runs either a hosted model, an exported model selected from disk, or a model bundled into a native release. The Python server independently validates stable predictions and maps them to a fixed pickup-and-bin action sequence.

## Easiest setup on another computer

Use the native `RobotSorter` build for that operating system. It includes Python, the browser libraries, and the application dependencies. The recipient only needs the robot's USB driver when their operating system does not already provide it.

1. Connect robot power, the Dynamixel USB adapter, and the camera.
2. Launch `RobotSorter`; it opens the local control page.
3. Under **Robot Setup**, refresh devices and select the adapter.
4. Run the safe preflight.
5. Import the three exported Teachable Machine files, or paste a hosted URL.
6. Verify dry-run classifications before using an execute-mode launch.

The app stores editable packaged configuration in the user's application-data directory. Source checkouts continue to use `robotics/config.json` and `robotics/actions.json`.

For a hosted model, the URL must be the parent model URL, for example:

```text
https://teachablemachine.withgoogle.com/models/MODEL_ID/
```

Do not paste a URL ending in `model.json`; the page appends `model.json` and `metadata.json` itself.

The model labels must be exactly:

```text
red object
blue object
empty
unknown
```

Start from source in dry-run mode and open the browser automatically:

```bash
python robotics/ml/teachable_machine_bridge.py --open-browser
```

Open:

```text
http://127.0.0.1:8765/
```

Dry-run mode prints the action that would run. It does not move the robot.

Before physical use, record this arm's fixed poses. Keep the pickup area, bins, and camera fixed while recording:

```bash
python robotics/ml/record_sorting_poses.py
```

The recorder captures a safe home/rest position and appends `pickup`, `red_bin`, and `blue_bin` poses to `robotics/actions.json`. It marks the profile calibrated and makes timestamped configuration/action backups before saving. It refuses to overwrite existing sorting poses unless you pass `--overwrite`.

Validate the serial port, mapping, and every required pose without moving the arm:

```bash
python robotics/ml/teachable_machine_bridge.py --preflight
```

Physical execution is disabled unless you explicitly pass `--execute`. Preflight is automatic in execute mode, and the page also exposes a non-moving preflight button:

```bash
python robotics/ml/teachable_machine_bridge.py --execute
```

Use `--execute` only after preflight, dry-run, and a clear-workspace check. The bridge accepts one red/blue sort and then latches; it re-arms only after a stable `empty` prediction or an explicit **Re-arm Sorting** click in the browser.

Server-side safety defaults are confidence `0.85`, 10 stable frames, and a 15-second motion timeout. Browser inputs cannot weaken these values. A timeout faults the session and attempts to disable torque; restart only after inspecting the arm. The physical power disconnect remains the emergency stop.

## Build native applications

Build on each target operating system; PyInstaller does not cross-compile:

```bash
./scripts/build-robot-sorter.sh
```

On Windows PowerShell:

```powershell
./scripts/build-robot-sorter.ps1
```

Outputs are written to `dist/`. `RobotSorter` runs the classifier bridge and `RobotPoseRecorder` records the fixed pickup/bin poses. Tagged releases named `robot-sorter-v*` build Windows, macOS, and Linux artifacts in GitHub Actions.

To make a release fully offline, put `model.json`, `metadata.json`, and the exported `.bin` weights file in `robotics/ml/assets/model/` before building. TensorFlow.js and the Teachable Machine image library are already vendored for offline use.

This is color classification, not object localization. The object must be placed in the one fixed recorded pickup location.
