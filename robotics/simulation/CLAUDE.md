# robotics/simulation

Vision-guided grasping for the real 6-DOF arm. A small MLP trained on MuJoCo data predicts where to grasp a piece near the gripper. `SimRobot` then uses MuJoCo **for kinematics only** (no physics stepping) to solve IK and drive the real servos.

## Pipeline

### 1. Generate data (`generate_data.py`, `DatasetGenerator`)
- Loads `low_cost_robot_6dof/train_scene.xml` (robot, `o_piece` and 8 `distractor_*` bodies, `gripper_cam` camera, `ee_site`).
- For each sample: place the piece on a board square, hover the gripper near it, render once from `gripper_cam`, and detect the piece's bounding box with `SimVision`.
- `generate_grid_labels(hover_pos)` tries a simulated grasp at every cell of a 7×7 grid, 5 mm apart, centred on the hover position. It skips cells farther than `max_grasp_radius` from the piece. Each cell is labelled 1 if the piece lifts, else 0.
- Writes `dataset/images/NNNNN.png` and `dataset/labels/NNNNN.json`. The label JSON holds `square_idx`, `piece_pos`, `piece_yaw`, `hover_pos`, `labels` (7×7), `grid_spacing`, `vision_piece_bbox`, and per-reason failure counts.
- CLI: `--n_samples`, `--start_idx`, `--output_dir`, `--model_path`. The real settings are in the `__main__` block, not the class defaults.

### 2. Train (`train_precision_mlp.py`)
- `GraspDataset` reads `dataset/labels/*.json`. Each sample's input is 14 values: a one-hot of the square index (9) + the bounding box `(x, y, w, h)` divided by image width/height (4) + a "bbox missing" flag (1).
- `GraspMLP(grid_size=7)`: 14 → 256 → 256 → 49 logits, reshaped to 7×7. Trained with `BCEWithLogitsLoss` and AdamW, with early stopping.
- Checkpoints are saved to `models/model_<timestamp>_<epoch>.pt`, relative to the folder you run it from. The model actually used is copied to `robotics/model.pt`.

### 3. Run on the real arm (`grasp_test.py` → `sim_robot.py` + `../vision.py`)
- `BoardVision(grasp_model_path=...)` runs the MLP in its camera thread on the blue piece closest to the image centre. `select_grasp_cell` (`grid_util.py`) picks the confidence-weighted centre of the best cluster of cells above 0.5 (falling back to the single best cell) and stores it as `vision.last_grid_spot = (row, col)`.
- `SimRobot.move_piece_precise(start, end)`: move to the recorded `hover` pose for `start`, then `attempt_grasp_real()`:
  - `get_target_xy()` reads the current hover pose from the real encoders (`sync_mujoco_to_real()` + forward kinematics) and adds the cell offset.
  - `ik_new()` is a damped IK solver that satisfies orientation first (gripper pointing down, rotated to face away from the base) and fits the position goal inside what's left. Close to the base, orientation is strictly enforced; far away it's relaxed.
  - `sim_to_real()` converts joint angles to servo ticks. The arm opens the gripper, descends to `grasp_height`, closes, and lifts by `lift_height`.

## Conventions

- **Grid:** 7×7, 5 mm spacing, centre cell `(3, 3)` = straight down from the hover position. `GraspMLP`, `DatasetGenerator`, `BoardVision` and `SimRobot.get_target_xy` must all agree. `model.pt` has a 49-value output layer, so changing the grid size means retraining.
- **Joint mapping:** `real_to_sim` maps ticks to radians as `(q_real/2048 - 1) * 3.14 * joint_signs`, with `joint_signs = [1, -1, 1, 1, -1, -1]`. `sim_to_real` is the inverse. Joint index 5 is the gripper, where sim `-1` = open and `0.1` = closed.
- **Recorded poses:** `../actions.json` holds, for each board cell (`'0'`–`'8'`) and supply slot (`'A'`–`'F'`), the poses `hover`, `pre-grasp`, `grasp` and `post-grasp` in servo ticks. Gripper ticks are about 2400 (open) at `hover`/`pre-grasp` and about 2120 (closed) at `grasp`/`post-grasp`.
- **Bounding-box size:** the bounding box is divided by image size. Training images are 640×360 (`DatasetGenerator.img_size`) and `vision.py` divides by 1920×1080. Both are 16:9, so the normalised values are comparable, but the sim and real camera framing must match for the model to transfer.
- `old_*.py` are earlier IK/vision experiments, kept for reference only.

## Grasp grid y-sign (open question)

The grasp MLP outputs a 7×7 grid of offsets from the arm's hover position, 5 mm per cell. The two sides that use this grid don't agree on the y direction:

- `generate_data.py` (`generate_grid_labels`) labels cell `(i, j)` with `dy = +(j - center) * grid_spacing`.
- `sim_robot.py` (`get_target_xy`) converts the chosen cell back with `dy = -(col_idx - center) * grid_spacing` ("negate the y-axis offset").

Both appear to be in the same world/base frame (MuJoCo site positions), so the arm may grasp at the mirror image in y of where the model predicted. It's unconfirmed whether the negation was added on purpose for the real arm. Settle this before training a new model, and keep the two in sync if either changes.

## Known gaps

- `move_piece_precise()` stops after the lift and never uses `end`. Placing the piece should reuse `Arm.move_piece()`'s reversed pose sequence for `end`.
- `grasp_test.py` resolves its paths relative to `simulation/` rather than `robotics/`, and adds the repo root to `sys.path` only after its `robotics.*` imports have already run.
- `vision.py` always passes square index `0` to the model.
- `BoardVision.frame_count` only goes up when `use_yolo=True`, so with YOLO off the grasp MLP runs on every frame, not every 3rd.
- Import styles are mixed: `generate_data.py` and `../vision.py` use `simulation.*` (needs `robotics/` on the import path), while `sim_robot.py` and `grasp_test.py` use `robotics.*` (needs the repo root).
