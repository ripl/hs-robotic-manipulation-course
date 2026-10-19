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

FAIL_NONE = 0        # successful lift
FAIL_NO_LIFT = 1     # unsuccessful lift
FAIL_PUSHED = 2       # pushed piece into board
FAIL_CONTACT = 3      # unwanted contact with obstacle
SKIPPED = -1          # never attempted (outside max_grasp_radius)

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
        self.ik_kwargs = dict(near_dist=0.12, far_dist=0.3, max_iters=500)

        # Vision and Rendering
        self.vision = SimVision(main=False, use_yolo=False, external_source=True)
        self.renderer = mujoco.Renderer(self.m, height=img_size[1], width=img_size[0])
        self.debug_viewer = debug_viewer
        self.viewer = None
        if debug_viewer:
            self.viewer = mujoco.viewer.launch_passive(self.m, self.d)

    def generate_dataset(self, n_samples, start_idx=0):
        print(f"Generating data (samples {start_idx} to {start_idx + n_samples - 1})...")

        for idx in tqdm.trange(start_idx, start_idx + n_samples):
            mujoco.mj_resetData(self.m, self.d)
            mujoco.mj_forward(self.m, self.d)

            # Trial Setup
            square_idx = idx % 9 # rotate between all 9 squares
            square_idx = 7
            square_center = self.square_centers[square_idx]

            piece_pos, yaw = self.randomize_piece(square_idx=square_idx)
            hover_pos, _ = self.randomize_hover(square_center)  # jitter around the square, not the piece
            self.place_obstacles(square_idx)

            mujoco.mj_forward(self.m, self.d)
            self._settle(200)
            piece_pos = self.d.body('o_piece').xpos.copy()  # overwrite with settled pos

            # Get Hover Image
            q = self._ik(hover_pos)
            q[5] = -1
            q[4] = -q[0]

            self.move_to_target_smooth(q, min_duration=0.3)
            self._settle(300)

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
                'hover_pos': hover_pos.tolist(),
                'labels': labels.tolist(),
                'grid_spacing': self.grid_spacing,
                'vision_piece_bbox': list(piece_bbox) if piece_bbox is not None else None,
                'max_grasp_radius': self.max_grasp_radius,
                'hover_radius': self.hover_radius,
                'fail_reason_counts': {
                    'no_lift': int((fail_reasons == FAIL_NO_LIFT).sum()),
                    'pushed': int((fail_reasons == FAIL_PUSHED).sum()),
                    'contact': int((fail_reasons == FAIL_CONTACT).sum()),
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
        if not pieces:
            return None

        cx, cy = self.img_size[0] / 2, self.img_size[1] / 2
        return min(pieces, key=lambda p: np.linalg.norm([cx - p[0], cy - p[1]]))

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

                success, reason = self.attempt_grasp(target_xy, piece_pos, grasp_height=self.grasp_height)
                labels[i, j] = int(success)
                fail_reasons[i, j] = reason

        return labels, fail_reasons

    def attempt_grasp(self, target_xy, piece_pos, grasp_height=0.02, n_settle_steps=100) -> tuple[bool, int]:
        """
        Move to target_xy (at grasp_height), close gripper, lift slightly,
        check if piece moved with the gripper (success) or stayed/dropped (fail).
        """
        qpos_snapshot = self.d.qpos.copy()
        qvel_snapshot = self.d.qvel.copy()

        def finish(success: bool, reason: int):
            self.d.qpos[:] = qpos_snapshot
            self.d.qvel[:] = qvel_snapshot
            mujoco.mj_forward(self.m, self.d)
            return success, reason

        hover_target = np.array([target_xy[0], target_xy[1], 0.05])
        grasp_target = np.array([target_xy[0], target_xy[1], grasp_height])
        original_piece_pos = piece_pos.copy()
        target_piece_body_id = self.m.body('o_piece').id

        # Move Laterally
        q = self._ik(hover_target, max_iters=100, damping=1e-2)
        q[5] = -0.45
        self.move_to_target_smooth(q)
        self._settle_until_reached(q, max_steps=1000, pos_tol=0.025, vel_thresh=5e-3)

        # Descend with Dampening
        q = self._ik(grasp_target, max_iters=100, damping=1e-2)
        self.move_to_target_smooth(q)
        self._settle_until_reached(q, max_steps=1000, pos_tol=0.025, vel_thresh=5e-3)

        if self.check_pushed_into_board('o_piece', original_piece_pos, n_check_steps=30):
            return finish(False, FAIL_PUSHED)
        if self.check_unwanted_contact(target_piece_body_id):
            return finish(False, FAIL_CONTACT)

        # Close Gripper
        self.close_gripper(closed_value=0.1, n_steps=500)
        if self.check_unwanted_contact(target_piece_body_id):
            return finish(False, FAIL_CONTACT)

        # Lift with Dampening
        lift_target = grasp_target + np.array([0, 0, self.lift_height])
        q = self._ik(lift_target, max_iters=100, damping=1e-2)
        q[5] = 0.1
        self.move_to_target_smooth(q)
        self._settle(n_settle_steps)

        piece_final_pos = self.d.body('o_piece').xpos.copy()
        lifted = piece_final_pos[2] > (piece_pos[2] + 0.03)
        if not lifted:
            return finish(False, FAIL_NO_LIFT)
        else:
            return finish(True, FAIL_NONE)

    def check_unwanted_contact(self, target_piece_body_id):
        """Returns true if the arm contacts any of the obstacle pieces."""
        for i in range(self.d.ncon):
            contact = self.d.contact[i]
            geom1_name = self.m.geom(contact.geom1).name
            geom2_name = self.m.geom(contact.geom2).name
            geom1_body = self.m.geom_bodyid[contact.geom1]
            geom2_body = self.m.geom_bodyid[contact.geom2]

            is_gripper_involved = geom1_name in self.gripper_geom_names or geom2_name in self.gripper_geom_names
            if not is_gripper_involved:
                continue

            other_body = geom2_body if geom1_name in self.gripper_geom_names else geom1_body
            if other_body != target_piece_body_id and other_body != 0:
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
            mujoco.mj_step(self.m, self.d)
            self._viewer_sync()

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
            mujoco.mj_step(self.m, self.d)
            self._viewer_sync()

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
            mujoco.mj_step(self.m, self.d)
            self._viewer_sync()
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
            mujoco.mj_step(self.m, self.d)
            self._viewer_sync()
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
            mujoco.mj_step(self.m, self.d)
            self._viewer_sync()

            pos_err = np.abs(self.robot.read_position()[:n] - q_target[:n])
            vel_ok = np.linalg.norm(self.d.qvel) < vel_thresh
            pos_ok = np.all(pos_err < pos_tol)
            if vel_ok and pos_ok:
                print(f"It took {i} iterations")
                break
        print(f"TIMEOUT after {max_steps} steps. pos_err={pos_err}, "
            f"qvel_norm={np.linalg.norm(self.d.qvel):.5f}")

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
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    gen = DatasetGenerator(args.model_path, output_dir=args.output_dir,
                                square_half_size=0.008, hover_radius=0.005, grid_size=7,
                                grid_spacing=0.005, max_grasp_radius=0.03,
                                grasp_height=0.025, lift_height=0.08,
                                debug_viewer=True)

    gen.generate_dataset(n_samples=args.n_samples, start_idx=args.start_idx)
