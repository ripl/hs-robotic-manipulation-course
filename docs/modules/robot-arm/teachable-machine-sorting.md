# Teachable Machine Object Sorting

<div class="module-summary" markdown>
**Goal:** Students train an image classifier and use it to choose robot-arm actions.

**Duration:** 2-4 class hours for the first demo; longer if students record new robot actions.

**Prerequisites:** Camera setup, basic robot safety, and at least one recorded robot action.
</div>

## Overview

In this module, students use Google Teachable Machine as the perception system for the robot. The model does not learn motor control. Instead, it classifies what the camera sees, and the robot program maps that class to an action.

```text
camera image
  -> Teachable Machine classifier
  -> class label and confidence
  -> Python bridge
  -> mapped robot action
```

The safest first task is object sorting. Students can train the model to recognize red and blue objects, then map each class to a different bin action.

## What Students Build

Students build a simple closed-loop AI system:

- A trained image classifier.
- A local browser page that runs the classifier.
- A Python bridge that receives stable predictions.
- A class-to-action mapping.
- Optional robot movement after the dry-run test is reliable.

## Recommended Classes

Use explicit negative classes. They make the robot much safer.

| Class | Meaning | Robot action |
| --- | --- | --- |
| `red object` | A red object is centered in the camera view. | Sort to red bin. |
| `blue object` | A blue object is centered in the camera view. | Sort to blue bin. |
| `empty` | No object is visible. | Do nothing. |
| `unknown` | Bad lighting, hand in frame, mixed objects, unclear view. | Do nothing. |

## Student Workflow

1. Go to <https://teachablemachine.withgoogle.com/>.
2. Create an **Image Project**.
3. Add the classes listed above.
4. Collect examples for each class using the same camera position and lighting that the robot will use.
5. Train the model.
6. Test the model in Teachable Machine.
7. Export the model files for offline use, or copy the hosted model URL.
8. Start the local bridge:

```bash
cd hs-robotic-manipulation-course
python robotics/ml/teachable_machine_bridge.py --open-browser
```

9. Open:

```text
http://127.0.0.1:8765/
```

10. Select the exported model files or paste the model URL, then start the camera.
11. Confirm predictions are stable before enabling **Send stable predictions to Python**.

## Dry-Run First

The bridge starts in dry-run mode. It prints what the robot would do, but it does not move the robot.

Example:

```text
[dry_run] red object (0.93) -> {"action": "sort_red"}
```

Students should see reliable dry-run predictions before any physical execution is enabled.

## Action Mapping

The class-to-action mapping lives in:

```text
robotics/ml/teachable_machine_actions.json
```

Example:

```json
{
  "red object": {
    "sequence": [
      {"action": "pickup", "pose": "hover"},
      {"action": "pickup", "pose": "pre-grasp"},
      {"action": "pickup", "pose": "grasp"},
      {"action": "pickup", "pose": "post-grasp"},
      {"action": "red_bin", "pose": "post-grasp"},
      {"action": "red_bin", "pose": "grasp"},
      {"action": "red_bin", "pose": "pre-grasp"},
      {"action": "red_bin", "pose": "hover"}
    ]
  },
  "empty": {"action": null},
  "unknown": {"action": null}
}
```

Class names must match the labels in Teachable Machine.

## Record the Fixed Sorting Poses

This is a fixed-location demo, not object localization. Before physical execution, fix the camera, pickup position, red bin, and blue bin in place. Then record poses on this specific arm:

```bash
python robotics/ml/record_sorting_poses.py
```

The script first records a safe home/rest position, then appends `pickup`, `red_bin`, and `blue_bin` to `robotics/actions.json`; each location has `hover`, `pre-grasp`, `grasp`, and `post-grasp` poses. It marks the profile calibrated, creates timestamped backups before writing, and refuses to replace existing sorting poses unless `--overwrite` is given.

For the pickup position, record the arm moving from open/above the object to closed/lifted. For each bin, record the reverse placement path: above/closed, at drop height/closed, at drop height/open, then above/open.

## Safety Gates

The demo page only sends a prediction when:

- the top class is above the confidence threshold,
- the same class has stayed on top for several frames,
- sending is enabled by the user,
- enough time has passed since the previous send.

The Python bridge repeats the confidence and stable-frame checks server-side, serializes motion requests, and starts in dry-run mode. Physical movement requires the instructor to start it with `--execute`.

After one red or blue command, the bridge latches and suppresses repeat sorting. It re-arms after a stable `empty` prediction or an explicit **Re-arm Sorting** button click.

## Optional Robot Execution

Only after dry-run testing:

```bash
python robotics/ml/teachable_machine_bridge.py --preflight
python robotics/ml/teachable_machine_bridge.py --execute
```

`--preflight` checks the serial-device path, the mapping, and all referenced poses without moving the arm. Physical execution uses the existing `robotics/actions.json` pose format. Every recorded location should include:

```text
hover
pre-grasp
grasp
post-grasp
```

Use physical execution only after checking the workspace, unplugging hazards, and confirming students know how to disconnect power.

If a motion does not settle within the configured timeout, the bridge faults, attempts to disable torque, and requires a restart. Never treat the browser controls as an emergency stop; keep the physical power disconnect reachable.

## Moving to another computer

The preferred handoff is the native `RobotSorter` artifact for Windows, macOS, or Linux. Launch it, select the detected serial adapter in **Robot Setup**, run preflight, and test in dry-run mode. Docker is not required and can complicate direct USB access. Each physical arm/layout still needs its own recorded pickup and bin poses.

## Reflection Questions

- What examples helped the model generalize?
- What examples confused the model?
- Why do `empty` and `unknown` classes matter?
- Why do we require stable predictions instead of acting on every frame?
- Is this system learning robot motion, perception, or decision making?
