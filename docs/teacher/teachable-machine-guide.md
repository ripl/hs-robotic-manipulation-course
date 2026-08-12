# Teachable Machine Teacher Guide

This guide supports the [Teachable Machine Object Sorting](../modules/robot-arm/teachable-machine-sorting.md) module.

## Recommended First Task

Use object sorting, not free-form manipulation.

The first successful version should be:

```text
red object    -> print/sort_red
blue object   -> print/sort_blue
empty         -> do nothing
unknown       -> do nothing
```

Do not start by letting predictions move the physical arm. Start with the dry-run bridge.

## Materials

- A laptop with webcam access.
- Stable table lighting.
- Two visually distinct objects: one red and one blue.
- A clear camera position.
- The course repository.
- Internet access for Teachable Machine and the TensorFlow.js libraries.
- Optional: robotic arm with recorded actions.

## Before Class

1. Start the docs site if you want students to follow the page:

```bash
cd hs-robotic-manipulation-course
source .docs-venv/bin/activate
mkdocs serve
```

2. Confirm the bridge starts in dry-run mode:

```bash
python robotics/ml/teachable_machine_bridge.py
```

3. Open:

```text
http://127.0.0.1:8765/
```

4. Confirm the page loads.
5. Stop the bridge with `Control-C`.

## Data Collection Guidance

Students should collect varied but relevant examples:

- Move the object around the region where the robot will see it.
- Include slight rotation changes.
- Include different hand-off positions if hands may enter the frame.
- Keep the camera angle the same as deployment.
- Add `empty` examples from the real workspace.
- Add `unknown` examples: hands, two objects at once, bad framing, blurry views.

Avoid:

- Training with one perfect image per class.
- Changing the camera position after training.
- Training only on held-up objects if deployment uses table objects.
- Letting background color become the actual class signal.

## Classroom Sequence

1. Explain the system:

```text
perception -> decision -> action
```

2. Students train Teachable Machine models.
3. Students test in Teachable Machine and revise data.
4. Instructor starts the dry-run bridge:

```bash
python robotics/ml/teachable_machine_bridge.py
```

5. Students paste the model URL into the bridge page.
6. Students observe predictions without sending.
7. Students enable sending and watch Python print mapped actions.
8. Students edit `robotics/ml/teachable_machine_actions.json` if labels differ.
9. The instructor records fixed `pickup`, `red_bin`, and `blue_bin` poses:

```bash
python robotics/ml/record_sorting_poses.py
```

10. Run the non-moving validation:

```bash
python robotics/ml/teachable_machine_bridge.py --preflight
```

11. Only after reliable dry-run behavior and preflight, connect to recorded robot actions.

## Physical Execution Checklist

Before `--execute`:

- `python robotics/ml/teachable_machine_bridge.py --preflight` passes.
- The dry-run printout is reliable.
- `empty` and `unknown` do nothing.
- The confidence threshold is at least `0.85`.
- Stable frames are at least `10`.
- The robot workspace is clear.
- The arm has a known power disconnect procedure.
- A single instructor controls the terminal.
- Students are not near the arm during motion.
- The pickup location, camera, and bins are fixed in place.

Then:

```bash
python robotics/ml/teachable_machine_bridge.py --execute
```

## Failure Modes To Teach

| Failure | Likely cause | Fix |
| --- | --- | --- |
| Model is overconfident on empty table | No `empty` class or too few empty examples | Add empty examples from deployment view. |
| Model confuses colors | Lighting or objects too similar | Improve lighting or use more distinct objects. |
| Model recognizes the background | Training data varied object less than background | Move objects/background during collection. |
| Robot repeats actions too often | Bridge not re-armed correctly or sending left enabled | The bridge now latches after a sort; show stable `empty` or press **Re-arm Sorting**. |
| Robot moves on a bad view | No `unknown` class or threshold too low | Add unknown examples and increase threshold. |

## What To Emphasize

Teachable Machine is useful because it lets students quickly build a perception model. The engineering lesson is the full system around it: data collection, validation, thresholds, safety gates, and mapping predictions to actions.
