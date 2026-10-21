import argparse
import cv2
import json
import mujoco
import mujoco.viewer
import numpy as np
import os
from PIL import Image
import time
import tqdm
from simulation.interface import SimulatedRobot
from simulation.sim_vision import SimVision
from simulation.grid_util import select_grasp_bbox, GRASP_YAW, GRIPPER_OPEN_SIM

FAIL_NONE = 0        # successful lift
FAIL_NO_LIFT = 1     # unsuccessful lift
FAIL_PUSHED = 2       # pushed piece into board
FAIL_CONTACT = 3      # unwanted contact with obstacle, or an obstacle was moved
FAIL_SLIP = 4         # lifted, but the piece slid in or fell out of the claw while held
SKIPPED = -1          # never attempted (outside max_grasp_radius)

FAIL_NAMES = {FAIL_NONE: 'SUCCESS', FAIL_NO_LIFT: 'NO_LIFT', FAIL_PUSHED: 'PUSHED',
              FAIL_CONTACT: 'CONTACT', FAIL_SLIP: 'SLIP'}

class _TrialFailed(Exception):
    """Raised from inside a physics step to end a grasp attempt early."""
    def __init__(self, reason, detail):
        super().__init__(detail)
        self.reason = reason
        self.detail = detail

class DatasetGenerator:
    def __init__(self, model_path, output_dir='dataset',
                 square_half_size=0.023, hover_radius=0.023,
                 grid_size=7, grid_spacing=0.005, img_size=(640, 360),
                 max_grasp_radius=0.02, grasp_height=0.02,
                 lift_height=0.08, debug_viewer=False):
        # MuJoCo Setup
        self.m = mujoco.MjModel.from_xml_path(model_path)
        self.d = mujoco.MjData(self.m)
        self.robot = SimulatedRobot(self.m, self.d)

        self.distractor_body_ids = {self.m.body(f'distractor_{i}').id for i in range(8)}

        self.gripper_geom_names = [
            'elbow-to-wrist-motor-reference_v1_1',
            'joint5-pt1', 'joint5',
            'static_finger_pad', 'moving_finger_pad',
            'camera_retrofit', 'cs_mount',
            'gripper-moving-part-dumb_v2_1',
        ]

        # Everything that counts as "the robot" for contact checks: the base and every link below it
        base_id = self.m.body('base_link').id
        self.arm_body_ids = {b for b in range(self.m.nbody)
                             if b == base_id or self._is_descendant(b, base_id)}
        self.target_piece_id = self.m.body('o_piece').id
        # Body masks for the vectorised per-step contact check
        self._distractor_ids = np.array(sorted(self.distractor_body_ids))
        self._is_distractor = np.zeros(self.m.nbody, dtype=bool)
        self._is_distractor[self._distractor_ids] = True
        self._is_robot_or_target = np.zeros(self.m.nbody, dtype=bool)
        self._is_robot_or_target[list(self.arm_body_ids) + [self.target_piece_id]] = True
        self.finger_pad_geom_ids = {self.m.geom('static_finger_pad').id, self.m.geom('moving_finger_pad').id}
        self._trial_monitor = None  # per-step check, set only while a grasp attempt runs

        self.cam_id = self.m.camera('gripper_cam').id
        self.site_id = self.m.site('ee_site').id

        self.square_centers = self._compute_square_centers(square_pitch=0.045)

        # Directories
        self.output_dir = output_dir
        os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'labels'), exist_ok=True)

        # Class Setup
        self.square_half_size = square_half_size
        self.hover_radius = hover_radius
        self.grid_size = grid_size
        self.grid_spacing = grid_spacing
        self.img_size = img_size
        self.max_grasp_radius = max_grasp_radius
        self.grasp_height = grasp_height
        self.lift_height = lift_height

        # IK Params
        # target_yaw keeps the claw square to the board at every square, like the real hover poses
        self.ik_kwargs = dict(near_dist=0.12, far_dist=0.3, max_iters=500, target_yaw=GRASP_YAW)

        # Vision and Rendering
        self.vision = SimVision(main=False, use_yolo=False, external_source=True)
        self.renderer = mujoco.Renderer(self.m, height=img_size[1], width=img_size[0])
        self.debug_viewer = debug_viewer
        self.viewer = None
        if debug_viewer:
            self.viewer = mujoco.viewer.launch_passive(self.m, self.d)

    def generate_dataset(self, n_samples, start_idx=0):
        print(f"Generating data (samples {start_idx} to {start_idx + n_samples - 1})...")
        # Seed from start_idx: each shard is reproducible, and parallel shards differ
        np.random.seed(start_idx)

        for idx in tqdm.trange(start_idx, start_idx + n_samples):
            mujoco.mj_resetData(self.m, self.d)
            mujoco.mj_forward(self.m, self.d)

            # Trial Setup
            square_idx = idx % 9 # rotate between all 9 squares
            square_center = self.square_centers[square_idx]

            piece_pos, yaw = self.randomize_piece(square_idx=square_idx)
            hover_target, _ = self.randomize_hover(square_center)  # jitter around the square, not the piece
            self.place_obstacles(square_idx)

            mujoco.mj_forward(self.m, self.d)
            self._settle(200)
            piece_pos = self.d.body('o_piece').xpos.copy()  # overwrite with settled pos

            # Get Hover Image
            q = self._ik(hover_target)   # wrist roll cancelling the base now comes from target_yaw
            q[5] = GRIPPER_OPEN_SIM   # grasp attempts start from here, so open only partly

            self.move_to_target_smooth(q, min_duration=0.3)
            # Wait for the base to actually arrive before rendering: it lags 0.1-0.2 rad at the
            # end of the move and needs ~3 s to catch up (a fixed 300-step settle left 12-17 mm of error).
            # Joints 2-5 keep a small gravity sag, so they get a looser tolerance.
            self._settle_until_reached(q, max_steps=5000, pos_tol=np.array([0.002] + [0.025] * 5))

            # The grid stays centred on the IK target: grasp attempts sag the same way the hover does,
            # so target-relative offsets match where the claw really goes (centring on the measured
            # pose double-counted the sag, ~2 mm). The measured pose is saved for diagnostics.
            hover_pos = hover_target
            hover_measured = self.d.site_xpos[self.site_id].copy()

            # Render Exactly Once
            img = self.render_image()
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            piece_bbox = self.get_vision_piece_bbox(img_bgr)

            # Generate and Output Data
            labels, fail_reasons = self.generate_grid_labels(hover_pos)
            Image.fromarray(img).save(f'{self.output_dir}/images/{idx:05d}.png')
            meta = {
                'square_idx': int(square_idx),
                'piece_pos': piece_pos.tolist(),
                'piece_yaw': float(yaw),
                'hover_pos': hover_pos.tolist(),            # grid centre (IK target)
                'hover_measured': hover_measured.tolist(),  # where the end effector settled
                'labels': labels.tolist(),
                'grid_spacing': self.grid_spacing,
                'vision_piece_bbox': list(piece_bbox) if piece_bbox is not None else None,
                'img_size': list(self.img_size),  # (w, h) the bbox is in -- training normalises by this
                'max_grasp_radius': self.max_grasp_radius,
                'hover_radius': self.hover_radius,
                'fail_reason_counts': {
                    'no_lift': int((fail_reasons == FAIL_NO_LIFT).sum()),
                    'pushed': int((fail_reasons == FAIL_PUSHED).sum()),
                    'contact': int((fail_reasons == FAIL_CONTACT).sum()),
                    'slip': int((fail_reasons == FAIL_SLIP).sum()),
                    'success': int((fail_reasons == FAIL_NONE).sum()),
                },
            }

            with open(f'{self.output_dir}/labels/{idx:05d}.json', 'w') as f:
                json.dump(meta, f)

    def randomize_piece(self, square_idx):
        """Places piece at random (x, y) within the spawn square with a random yaw."""
        center = self.square_centers[square_idx]
        x = center[0] + np.random.uniform(-self.square_half_size, self.square_half_size)
        y = center[1] + np.random.uniform(-self.square_half_size, self.square_half_size)
        piece_pos = np.array([x, y, 0.0])

        yaw = np.random.uniform(0, 2 * np.pi)
        quat = np.zeros(4)
        mujoco.mju_axisAngle2Quat(quat, np.array([0, 0, 1]), yaw)

        jnt_id = self.m.joint('o_piece_joint').id
        qpos_addr = self.m.jnt_qposadr[jnt_id]
        self.d.qpos[qpos_addr:qpos_addr + 3] = piece_pos
        self.d.qpos[qpos_addr + 3:qpos_addr + 7] = quat

        return piece_pos, yaw

    def randomize_hover(self, center_pos):
        """Picks a random hover pose within hover_radius of the given center."""
        angle = np.random.uniform(0, 2 * np.pi)
        r = np.random.uniform(0, self.hover_radius)
        offset = np.array([r * np.cos(angle), r * np.sin(angle), 0.0])
        hover_pos = center_pos + offset + np.array([0, 0, 0.05])
        return hover_pos, offset[:2]

    def place_obstacles(self, square_idx):
        """Places a gray obstacle piece in every square except the target square"""
        other_squares = [i for i in range(9) if i != square_idx]
        for i, sq_idx in enumerate(other_squares):
            distractor_name = f'distractor_{i}'
            center = self.square_centers[sq_idx]
            x = center[0]
            y = center[1]
            yaw = np.random.uniform(0, 2 * np.pi)

            pos = np.array([x, y, 0.0])
            quat = np.zeros(4)
            mujoco.mju_axisAngle2Quat(quat, np.array([0, 0, 1]), yaw)

            jnt_id = self.m.joint(f'{distractor_name}_joint').id
            qpos_addr = self.m.jnt_qposadr[jnt_id]
            self.d.qpos[qpos_addr:qpos_addr+3] = pos
            self.d.qpos[qpos_addr+3:qpos_addr+7] = quat

    def get_vision_piece_bbox(self, frame, n_submits=2):
        """
        Returns (x, y, w, h) of the blue piece closest to the image center,
        or None if no blue piece was detected.
        """
        with self.vision._pieces_lock:
            self.vision._blue_pieces = []

        for _ in range(n_submits):
            self.vision.submit_frame(frame)
            self.vision.wait_for_processed()

        pieces = self.vision.get_blue_piece_positions()
        return select_grasp_bbox(pieces, *self.img_size)

    def render_image(self, camera_name='gripper_cam'):
        """Renders an image from the wrist camera."""
        self.renderer.update_scene(self.d, camera=camera_name)
        return self.renderer.render()

    def generate_grid_labels(self, hover_pos):
        labels = np.zeros((self.grid_size, self.grid_size), dtype=np.int8)
        fail_reasons = np.full((self.grid_size, self.grid_size), SKIPPED, dtype=np.int8)

        piece_pos = self.d.body('o_piece').xpos.copy()
        center = self.grid_size // 2

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                dx = (i - center) * self.grid_spacing
                dy = (j - center) * self.grid_spacing
                target_xy = hover_pos[:2] + np.array([dx, dy])

                dist_from_piece = np.linalg.norm(target_xy - piece_pos[:2])
                if dist_from_piece > self.max_grasp_radius:
                    continue

                success, reason, detail = self.attempt_grasp(target_xy, piece_pos, grasp_height=self.grasp_height)
                labels[i, j] = int(success)
                fail_reasons[i, j] = reason
                if self.debug_viewer:
                    print(f"  cell ({i},{j}) offset ({dx*1000:+.0f}, {dy*1000:+.0f}) mm: "
                          f"{FAIL_NAMES[reason]:8} {detail}")

        return labels, fail_reasons

    def attempt_grasp(self, target_xy, piece_pos, grasp_height=0.02, hold_steps=600,
                      slip_tol=0.004, distractor_move_tol=0.0015,
                      distractor_rot_tol=np.radians(5)) -> tuple[bool, int, str]:
        """
        Move to target_xy (at grasp_height), close gripper, lift, then hold.
        Returns (success, reason, detail). Fails as soon as the arm or the target piece
        touches a distractor, or any distractor moves (checked every physics step).
        Success needs the piece to stay put in the claw for the whole hold, not just
        be above the board at one instant.
        """
        qpos_snapshot = self.d.qpos.copy()
        qvel_snapshot = self.d.qvel.copy()
        ctrl_snapshot = self.d.ctrl.copy()

        def finish(success: bool, reason: int, detail: str = ''):
            self._trial_monitor = None
            self.d.qpos[:] = qpos_snapshot
            self.d.qvel[:] = qvel_snapshot
            self.d.ctrl[:] = ctrl_snapshot
            mujoco.mj_forward(self.m, self.d)
            return success, reason, detail

        hover_target = np.array([target_xy[0], target_xy[1], 0.05])
        grasp_target = np.array([target_xy[0], target_xy[1], grasp_height])
        original_piece_pos = piece_pos.copy()

        distractor_start = (self.d.xpos[self._distractor_ids].copy(), self.d.xquat[self._distractor_ids].copy())
        self._trial_monitor = lambda: self._check_distractors(distractor_start,
                                                              distractor_move_tol, distractor_rot_tol)
        try:
            # Move Laterally
            q = self._ik(hover_target, max_iters=500, damping=1e-2)
            q[5] = GRIPPER_OPEN_SIM
            self.move_to_target_smooth(q)
            self._settle_until_reached(q, max_steps=1000, pos_tol=0.025, vel_thresh=5e-3)

            # Descend with Dampening
            q = self._ik(grasp_target, max_iters=500, damping=1e-2)
            self.move_to_target_smooth(q)
            self._settle_until_reached(q, max_steps=1000, pos_tol=0.025, vel_thresh=5e-3)

            if self.check_pushed_into_board('o_piece', original_piece_pos, n_check_steps=30):
                return finish(False, FAIL_PUSHED, 'piece shoved along the board on descent')

            # Close Gripper
            self.close_gripper(closed_value=0.1, n_steps=500)

            # Lift with Dampening
            lift_target = grasp_target + np.array([0, 0, self.lift_height])
            q = self._ik(lift_target, max_iters=500, damping=1e-2)
            q[5] = 0.1
            self.move_to_target_smooth(q)

            piece_z = self.d.xpos[self.target_piece_id][2]
            if piece_z < piece_pos[2] + 0.03:
                return finish(False, FAIL_NO_LIFT, f'piece only {(piece_z - piece_pos[2]) * 1000:.0f} mm up after lift')

            # Hold: the piece must stay at the same height relative to the claw
            rel_start = piece_z - self.d.site_xpos[self.site_id][2]
            for step in range(hold_steps):
                self._step()
                rel = self.d.xpos[self.target_piece_id][2] - self.d.site_xpos[self.site_id][2]
                if abs(rel - rel_start) > slip_tol:
                    return finish(False, FAIL_SLIP,
                                  f'slid {abs(rel - rel_start) * 1000:.1f} mm in the claw after {step} hold steps')
            touching = self._finger_pads_touching_piece()
            if len(touching) < 2:
                return finish(False, FAIL_SLIP, f'held by {len(touching)} finger pad(s) at end of hold')

            return finish(True, FAIL_NONE, f'held steady for {hold_steps} steps')
        except _TrialFailed as e:
            return finish(False, e.reason, e.detail)

    def _check_distractors(self, start, move_tol, rot_tol):
        """Per-step trial monitor: fail if the robot or target piece touches a distractor,
        or if any distractor has moved since the attempt started. Vectorised -- it runs every step."""
        ncon = self.d.ncon
        if ncon:
            bodies = self.m.geom_bodyid[self.d.contact.geom[:ncon]]          # (ncon, 2)
            dist, robot = self._is_distractor[bodies], self._is_robot_or_target[bodies]
            hits = (dist[:, 0] & robot[:, 1]) | (dist[:, 1] & robot[:, 0])
            if hits.any():
                b1, b2 = bodies[np.argmax(hits)]
                hit, other = (b1, b2) if self._is_distractor[b1] else (b2, b1)
                who = 'target piece' if other == self.target_piece_id else self.m.body(other).name
                raise _TrialFailed(FAIL_CONTACT, f'{who} touched {self.m.body(hit).name}')

        pos0, quat0 = start
        moved = np.linalg.norm(self.d.xpos[self._distractor_ids] - pos0, axis=1)
        angle = 2 * np.arccos(np.clip(np.abs(np.sum(self.d.xquat[self._distractor_ids] * quat0, axis=1)), 0.0, 1.0))
        bad = (moved > move_tol) | (angle > rot_tol)
        if bad.any():
            k = np.argmax(bad)
            raise _TrialFailed(FAIL_CONTACT, f'{self.m.body(self._distractor_ids[k]).name} moved '
                                             f'{moved[k] * 1000:.1f} mm / {np.degrees(angle[k]):.1f} deg')

    def _finger_pads_touching_piece(self):
        """Finger pad geoms currently in contact with the target piece."""
        touching = set()
        for i in range(self.d.ncon):
            c = self.d.contact[i]
            for pad, other in ((c.geom1, c.geom2), (c.geom2, c.geom1)):
                if pad in self.finger_pad_geom_ids and self.m.geom_bodyid[other] == self.target_piece_id:
                    touching.add(pad)
        return touching

    def _is_descendant(self, body, ancestor):
        while body != 0:
            body = self.m.body_parentid[body]
            if body == ancestor:
                return True
        return False

    def check_pushed_into_board(self, piece_body_id, original_pos, n_check_steps=30,
                                displacement_thresh=0.003, sustained_frac=0.7):
        """
        Steps physics for n_check_steps and tracks how many of those steps show
        the piece meaningfully displaced from its original resting position
        (e.g., shoved sideways/into the board) rather than just briefly nudged.
        Returns True if displaced for a large fraction of the checked window.
        """
        displaced_count = 0
        for _ in range(n_check_steps):
            self._step()

            current_pos = self.d.body(piece_body_id).xpos.copy()
            planar_disp = np.linalg.norm(current_pos[:2] - original_pos[:2])
            if planar_disp > displacement_thresh:
                displaced_count += 1
        return (displaced_count / n_check_steps) > sustained_frac

    def move_to_target_smooth(self, q_target, max_vel=None, dt=None, min_duration=None):
        """
        Smoothly interpolate from current joint positions to q_target,
        synchronized so all joints arrive together.
        """
        if dt is None:
            dt = self.m.opt.timestep
        if max_vel is None:
            max_vel = np.array([1.0, 0.8, 1.0, 1.2, 1.2, 2.0])

        q_start = self.robot.read_position().copy()
        n = len(q_target[:6])

        delta = np.abs(q_target[:n] - q_start[:n])
        if min_duration is None:
            move_dist = np.linalg.norm(delta)
            min_duration = np.clip(move_dist * 0.5, 0.05, 2.0)

        per_joint_time = delta / max_vel[:n]
        duration = max(per_joint_time.max(), min_duration)
        n_steps = max(int(duration / dt), 1)

        for step in range(1, n_steps + 1):
            alpha = step / n_steps
            alpha_smooth = 3 * alpha**2 - 2 * alpha**3
            q_interp = q_start[:n] + alpha_smooth * (q_target[:n] - q_start[:n])

            self.robot.set_target_pos(q_interp)
            self._step()

    def close_gripper(self, closed_value=0.1, n_steps=200, vel_thresh=1e-3):
        """
        Moves the gripper joint to closed_value over the course of n_steps steps
        """
        current_ctrl = self.d.ctrl.copy()
        start_val = current_ctrl[5]
        for step in range(1, n_steps + 1):
            alpha = step / n_steps
            alpha_smooth = 3 * alpha**2 - 2 * alpha**3
            current_ctrl[5] = start_val + alpha_smooth * (closed_value - start_val)
            self.d.ctrl[:] = current_ctrl
            self._step()
            if np.linalg.norm(self.d.qvel) < vel_thresh:
                break

    def _ik(self, ee_target_pos, site_name='ee_site', **overrides):
        kwargs = {**self.ik_kwargs, **overrides}
        return self.robot.ik_new(ee_target_pos=ee_target_pos, site_name=site_name, **kwargs)

    def _compute_square_centers(self, square_pitch=0.045):
        centers = []
        for row in range(3):
            for col in range(3):
                x = 0.04338849 - col * square_pitch
                y = 0.15648749 + row * square_pitch
                centers.append(np.array([x, y, 0.0]))
        return centers

    def _settle(self, max_steps, vel_thresh=1e-3):
        """Waits until the norm of joint all velocities is below vel_thresh. """
        for _ in range(max_steps):
            step_start = time.time()
            self._step()
            if self.debug_viewer:
                time_until_next = self.m.opt.timestep - (time.time() - step_start)
                if time_until_next > 0:
                    time.sleep(time_until_next)
            if np.linalg.norm(self.d.qvel) < vel_thresh:
                break

    def _settle_until_reached(self, q_target, max_steps, pos_tol=0.02, vel_thresh=1e-3):
        """Steps until joints are settled close to q_target"""
        n = len(q_target[:6])

        for i in range(max_steps):
            self._step()

            pos_err = np.abs(self.robot.read_position()[:n] - q_target[:n])
            vel_ok = np.linalg.norm(self.d.qvel) < vel_thresh
            pos_ok = np.all(pos_err < pos_tol)
            if vel_ok and pos_ok:
                return

        if self.debug_viewer:
            print(f"TIMEOUT after {max_steps} steps. pos_err={pos_err}, "
                f"qvel_norm={np.linalg.norm(self.d.qvel):.5f}")

    def _step(self):
        """One physics step. During a grasp attempt, the trial monitor runs after every step."""
        mujoco.mj_step(self.m, self.d)
        if self._trial_monitor is not None:
            self._trial_monitor()
        self._viewer_sync()

    def _viewer_sync(self):
        if self.viewer is not None and self.viewer.is_running():
            self.viewer.sync()

def parse_args():
    parser = argparse.ArgumentParser(description="Generate grasp-grid training data.")
    parser.add_argument('--start_idx', type=int, default=0,
                         help="Sample index to start generating from (for resuming or sharding across parallel runs).")
    parser.add_argument('--n_samples', type=int, default=2000,
                         help="Number of samples to generate, starting at --start_idx.")
    parser.add_argument('--output_dir', type=str, default='dataset',
                         help="Directory to write images/ and labels/ into.")
    parser.add_argument('--model_path', type=str,
                         default='low_cost_robot_6dof/train_scene.xml',
                         help="Path to the MJCF scene file.")
    parser.add_argument('--debug_viewer', action='store_true',
                         help="Open the MuJoCo viewer (needs a display -- leave off on headless servers).")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    gen = DatasetGenerator(args.model_path, output_dir=args.output_dir,
                                square_half_size=0.008, hover_radius=0.005, grid_size=7,
                                grid_spacing=0.005, max_grasp_radius=0.03,
                                grasp_height=0.025, lift_height=0.08,
                                debug_viewer=args.debug_viewer)

    gen.generate_dataset(n_samples=args.n_samples, start_idx=args.start_idx)
