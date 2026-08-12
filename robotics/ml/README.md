# Teachable Machine Bridge

This folder contains a small local bridge for the Teachable Machine robotics activity.

The browser runs a hosted Teachable Machine image model. The Python server receives stable predictions and maps them to a fixed pickup-and-bin action sequence.

The model URL must be the parent model URL, for example:

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

Start in dry-run mode:

```bash
python robotics/ml/teachable_machine_bridge.py
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

The recorder appends `pickup`, `red_bin`, and `blue_bin` poses to `robotics/actions.json` and makes a timestamped backup before saving. It refuses to overwrite existing sorting poses unless you pass `--overwrite`.

Validate the serial port, mapping, and every required pose without moving the arm:

```bash
python robotics/ml/teachable_machine_bridge.py --preflight
```

Physical execution is disabled unless you explicitly pass:

```bash
python robotics/ml/teachable_machine_bridge.py --execute
```

Use `--execute` only after preflight, dry-run, and a clear-workspace check. The bridge accepts one red/blue sort and then latches; it re-arms only after a stable `empty` prediction or an explicit **Re-arm Sorting** click in the browser.

This is color classification, not object localization. The object must be placed in the one fixed recorded pickup location.
