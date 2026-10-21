# robotics/simulation

Vision-guided grasping for the real 6-DOF arm. A small MLP trained on MuJoCo data predicts where to grasp a piece near the gripper. `SimRobot` then uses MuJoCo **for kinematics only** (no physics stepping) to solve IK and drive the real servos.

## Pipeline

### 1. Generate data (`generate_data.py`, `DatasetGenerator`)
- Loads `low_cost_robot_6dof/train_scene.xml` (robot, `o_piece` and 8 `distractor_*` bodies, `gripper_cam` camera, `ee_site`).
- For each sample: place the piece on a board square, hover the gripper near it, render once from `gripper_cam`, and detect the piece's bounding box with `SimVision`.
- `generate_grid_labels(hover_pos)` tries a simulated grasp at every cell of a 7×7 grid, 5 mm apart, centred on the hover position. It skips cells farther than `max_grasp_radius` from the piece. Each cell is labelled 1 if the piece lifts, else 0.
- Writes `dataset/images/NNNNN.png` and `dataset/labels/NNNNN.json`. The label JSON holds `square_idx`, `piece_pos`, `piece_yaw`, `hover_pos`, `labels` (7×7), `grid_spacing`, `vision_piece_bbox`, and per-reason failure counts.
- CLI: `--n_samples`, `--start_idx`, `--output_dir`, `--model_path`, `--debug_viewer` (off by default; needs a display). The real settings are in the `__main__` block, not the class defaults.
- Run from `robotics/simulation/` with `robotics/` importable. On a headless server, also set `MUJOCO_GL=egl` (NVIDIA) or `osmesa`:
  `MUJOCO_GL=egl PYTHONPATH=.. python generate_data.py --n_samples 500 --start_idx 0 --output_dir dataset`.
  It takes about 10 s per sample. Run shards in parallel with different `--start_idx` values into the same `--output_dir`. Each shard seeds NumPy from `start_idx`, so shards are reproducible and differ from each other.
- Each label also records `img_size`, which training uses to scale the bbox (sim renders 640×360).

### 2. Train (`train_precision_mlp.py`)
- `run_training.sh` wraps both stages. It sets `MUJOCO_GL` (default `egl`), `PYTHONPATH` and `OMP_NUM_THREADS=1`, can generate data in parallel shards (`--generate N --shards K`), then trains with hyperparameters passed as flags (`--lr`, `--batch-size`, `--epochs`, …). Run `./run_training.sh --help` for the full list. Every training hyperparameter is also a `train_precision_mlp.py` argument, and each one defaults to the value the script used before it took arguments. If you change `--hidden_dim`, update `GraspMLP(...)` in `vision.py` to match.
- `GraspDataset` reads `dataset/labels/*.json`. Samples with no detected bbox are skipped, because `vision.py` doesn't run the model without one. Each sample's input is 14 values: a one-hot of the square index (9) + the bounding box `(x, y, w, h)` divided by image width/height (4) + a "bbox missing" flag (1).
- `GraspMLP(grid_size=7)`: 14 → 256 → 256 → 49 logits, reshaped to 7×7. Trained with `BCEWithLogitsLoss` and AdamW, with early stopping.
- Checkpoints are saved to `models/model_<timestamp>_<epoch>.pt`, relative to the folder you run it from. The model actually used is copied to `robotics/model.pt`.

### 3. Run on the real arm (`grasp_test.py` → `sim_robot.py` + `../vision.py`)
- `BoardVision(grasp_model_path=...)` collects every blue blob each frame (whether or not the board is visible) and picks the grasp target with `select_grasp_bbox()` (`grid_util.py`). It runs the MLP on that box every 3rd frame. `select_grasp_cell` (`grid_util.py`) picks the confidence-weighted centre of the best cluster of cells above 0.5 (falling back to the single best cell) and stores it as `vision.last_grid_spot = (row, col)`. If no blob passes the filter, `last_grid_spot` is set to `None`.
- `SimRobot.move_piece_precise(start, end)`: move to the recorded `hover` pose for `start`, clear `last_grid_spot`, then `attempt_grasp_real(start)`:
  - `get_best_spot()` waits up to 5 s for a fresh `last_grid_spot` and raises an error if none arrives.
  - `get_target_xy()` reads the current hover pose from the real encoders (`sync_mujoco_to_real()` + forward kinematics) and adds the cell offset.
  - `ik_new()` (`max_iters=500`; 100 left 6–10 mm of error) is a damped IK solver that satisfies orientation first (gripper pointing down, claw heading `target_yaw`) and fits the position goal inside what's left. Close to the base, orientation is strictly enforced; far away it's relaxed.
  - Each IK move goes through `move_checked()`. It refuses if forward kinematics on the solution is more than 5 mm from the target, or if any arm joint (0–4) is outside the servo limits in `../config.json`, because `Robot.set_goal_pos` would silently clip it. With `confirm=True` it prints the goal ticks and waits for Enter.
  - The arm opens the gripper to `GRIPPER_OPEN_TICKS` (2400) and descends to `grasp_height` (0.02 m), then closes. To lift, it returns to `positions[start]['hover']` with the gripper kept at the closed command. This is a recorded, known-reachable pose. An IK lift of 8 cm hit joint limits or failed to converge for some grid spots.
  - Then `move_piece_precise()` goes to `home_pos`.

### Running `grasp_test.py`
`python robotics/simulation/grasp_test.py`. It sets up `sys.path` itself and resolves `config.json`, `actions.json`, `model.pt` and the MJCF relative to `robotics/`. It uses `cam=0` and `confirm=True`, so every IK move pauses for Enter. There's no camera window (`main=False`), so check that `cam=0` really is the gripper camera.

## Conventions

- **Grid:** 7×7, 5 mm spacing, centre cell `(3, 3)` = straight down from the hover position. `GraspMLP`, `DatasetGenerator`, `BoardVision` and `SimRobot.get_target_xy` must all agree. `model.pt` has a 49-value output layer, so changing the grid size means retraining.
- **Joint mapping:** `real_to_sim` maps ticks to radians as `(q_real/2048 - 1) * 3.14 * joint_signs`, with `joint_signs = [1, -1, 1, 1, -1, -1]`. `sim_to_real` is the inverse. Joint index 5 is the gripper, where sim `0.1` = closed (clipped to the 2020-tick limit on the real arm), `-1` = fully open (2700), and `GRIPPER_OPEN_SIM` ≈ −0.54 = 2400 ticks.
- **Recorded poses:** `../actions.json` holds, for each board cell (`'0'`–`'8'`) and supply slot (`'A'`–`'F'`), the poses `hover`, `pre-grasp`, `grasp` and `post-grasp` in servo ticks. Gripper ticks are about 2400 (open) at `hover`/`pre-grasp` and about 2120 (closed) at `grasp`/`post-grasp`.
- **Bounding-box size:** the bounding box is divided by image size. Training images are 640×360 (`DatasetGenerator.img_size`), and `vision.py` takes the real size from each frame. Sim and real camera framing must match for the model to transfer.
- **Grasp-target filter:** `select_grasp_bbox()` is shared by `generate_data.py` (sim) and `vision.py` (real), so training and real bounding boxes are picked the same way. Its thresholds are fractions of the image (area 0.35–25%, aspect ratio ≤ 1.6, centre within 35% of the image diagonal), so they work at both resolutions. Change it in one place only.
- **Claw heading and opening (`grid_util.py`):** `GRASP_YAW = 0.0` is the world-frame claw heading passed as `ik_new(..., target_yaw=...)` in both `generate_data.py` (every IK call, through `ik_kwargs`) and `SimRobot.attempt_grasp_real`. With yaw 0 the wrist roll cancels the base rotation, so the claw stays square to the board, like the recorded hover poses (all within ±6° of 0°). With `target_yaw=None`, `ik_new` points the claw away from the base instead, about 90° off the recorded hovers, so the real arm turned the wrist about 90° on the way down and back on the way up. `GRIPPER_OPEN_TICKS = 2400` (`GRIPPER_OPEN_SIM` in radians) is the opening for the sim hover image, the sim grasp attempts and the real descent. Fully open (2700) swept neighbouring pieces. Change these in `grid_util.py` only.
- `old_*.py` are earlier IK/vision experiments, kept for reference only.

## Grasp grid y-sign (needs checking on the real arm)

The grasp MLP outputs a 7×7 grid of offsets from the arm's hover position, 5 mm per cell. Both sides now use the same sign:

- `generate_data.py` (`generate_grid_labels`) labels cell `(i, j)` with `dx = (i - center) * grid_spacing`, `dy = +(j - center) * grid_spacing`.
- `sim_robot.py` (`get_target_xy`) converts the chosen cell back with the same `+dy`. An earlier `-dy` was removed, and the code still has a "dy potentially backwards" comment.

That's consistent in the sim frame, but it hasn't been tested on the real arm. If real grasps consistently land at the mirror image in y, check this first. To test, put the piece clearly to one side of the hover point and check that the printed grid spot and `grasp_target` move the same way. Keep the two in sync if either changes.

## Known gaps

- `move_piece_precise()` never uses `end`. After the lift it goes to `home_pos`, whose gripper value (2700) is **open**, so the piece is dropped at home. Placing the piece should reuse `Arm.move_piece()`'s reversed pose sequence for `end` (`post-grasp` → `grasp` → `pre-grasp` releases it → `hover`).
- The lift from the grasp pose to the hover pose is a joint-space move, not a straight vertical lift. With `GRASP_YAW` the wrist roll changes by at most ~200 ticks between hover and grasp (it was 950–1180 before), but the path still isn't straight up, so the piece may be dragged slightly before it clears the board. If that knocks pieces over, add a short IK lift first (3–5 cm passed `move_checked` for every spot tested), then go to hover.
- `select_grasp_bbox()` thresholds are untuned starting guesses. Fit them to the `vision_piece_bbox` values in a regenerated dataset and check them against real gripper-camera frames that contain distractors.
- `vision.py` always passes square index `0` to the model.
- `attempt_grasp_real` grasps at z = 0.02 m, but `generate_data.py` labels at `grasp_height=0.025`.
- Import styles are mixed: `generate_data.py` and `../vision.py` use `simulation.*` (needs `robotics/` on the import path), while `sim_robot.py`, `grasp_test.py` and `../game/players.py` use `robotics.*` (needs the repo root). `grasp_test.py` adds both.
- **Sim arm accuracy (`low_cost_robot.xml`, `generate_data.py`).** The arm bodies have `gravcomp="1"`, since the real servos hold their pose and the weak sim actuators (kp 25/10) otherwise sagged 2–10 mm. A `<contact><exclude body1="base_link" body2="joint1"/>` is needed because `base_link` is welded to the world, so MuJoCo doesn't filter that parent–child pair. Without it, mesh friction made the base take about 3 s to finish turning. The hover waits in `_settle_until_reached` (now about 0.27 s) before rendering, and grasp-attempt IK uses `max_iters=500` (100 left up to 33 mm of IK error). Result: the settled hover is within 0.1 mm of its target for squares 0–5. **Far row (6–8) is still 2–4 mm off in xy and 4–5 mm low.** That's the IK's own error: about 25 cm out at 5 cm height with the claw pointing down is the edge of the arm's reach. Far-row labels are less precise, by about half a grid cell. The grid stays centred on the IK target (`hover_pos`); `hover_measured` is saved for diagnostics. Centring on the measured pose would double-count any remaining error.
