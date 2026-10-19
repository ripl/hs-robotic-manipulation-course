import mujoco
import numpy as np
import time
from typing import Union
from robotics.robot.robot import Robot
from robotics.game.players import Arm
from robotics.simulation.grid_util import GRASP_YAW, GRIPPER_OPEN_SIM

class SimRobot(Arm):
    def __init__(self, 
                 piece,
                 config_path='../config.json',
                 positions_path='../actions.json',
                 model_path='model.pt',
                 vision=None,
                 confirm=False,
                ) -> None:
        super().__init__(piece=piece, config_path=config_path, positions_path=positions_path)

        self.vision = vision
        self.confirm = confirm  # wait for Enter before each IK move on the real arm

        # MuJoCo model used ONLY for kinematics -- never stepped as a physics sim
        self.m = mujoco.MjModel.from_xml_path(model_path)
        self.d = mujoco.MjData(self.m)

        self.joint_signs = np.array([1, -1, 1, 1, -1, -1], dtype=float)

    def real_to_sim(self, q_real):
        q_sim = (q_real / 2048 - 1) * 3.14
        q_sim = q_sim * self.joint_signs
        return q_sim

    def sim_to_real(self, q_sim):
        q_real = 2048 * (1 + q_sim/(3.14 * self.joint_signs))

        #if not np.all(q_real >= 0):
            #raise ValueError(f"Negative value to servo found! {q_real}")

        return q_real

    def sync_mujoco_to_real(self):
        """Push real encoder readings into the MuJoCo model, then run
        forward kinematics so site_xpos/Jacobians reflect the real arm's
        actual current pose."""
        q_real = self.arm.read_position()
        q_sim = self.real_to_sim(q_real)
        self.d.qpos[:6] = q_sim
        mujoco.mj_forward(self.m, self.d)  # kinematics only -- no mj_step, no physics
        return q_real

    def get_best_spot(self, timeout=5.0):
        if self.vision is None:
            return (3, 3)

        deadline = time.time() + timeout
        while self.vision.last_grid_spot is None and time.time() < deadline:
            time.sleep(0.05)
        spot = self.vision.last_grid_spot
        if spot is None:
            raise RuntimeError("Grasp model produced no grid spot -- is a blue piece in view?")
        print("grid spot:", spot)
        return spot

    def move_piece_precise(self, start, end):
        """
        Move a piece from start to end position on the physical board.

        From the hover pos, the arm will adjust itself to better pick
        up the piece.

        :param start: The start position on the physical board.
        :param end: The end position on the physical board.
        """
        if self.vision is None:
            print("No vision, using bare move_piece() call")
            super().move_piece(start, end)
            return

        self.arm.set_and_wait_goal_pos(self.positions[start]['hover'])
        time.sleep(2.0)

        # Drop any spot computed while the arm was still moving; get_best_spot()
        # waits for one from the hover view
        self.vision.last_grid_spot = None

        self.attempt_grasp_real(start)

        self.arm.set_and_wait_goal_pos(self.arm_config['home_pos'])

        

    def ik_new(self, ee_target_pos, site_name='ee_site',
                        damping=1e-4, max_iters=500, tol=1e-4, step_scale=0.5,
                        far_dist=0.3, near_dist=0.12, base_body='base_link', target_yaw=None):
        """
        Hierarchical IK with base-relative, distance-adaptive orientation priority.
        alpha is computed once from how far the target is from the arm's base,
        not from the shrinking solve error.
        target_yaw: world-frame claw heading (rad). None points the claw away from the base.
        """
        ee_target_pos = np.asarray(ee_target_pos)
        q_real_initial = self.sync_mujoco_to_real()

        site_id = self.m.site(site_name).id
        base_id = self.m.body(base_body).id
        n = 6

        # --- reach distance: fixed for this target, computed from the base ---
        base_pos = self.d.xpos[base_id]
        reach_dist = np.linalg.norm(ee_target_pos[:2] - base_pos[:2])  # planar reach

        alpha = np.clip((reach_dist - near_dist) / (far_dist - near_dist), 0.0, 1.0)
        # NOTE: inverted vs before — alpha now means "far from base -> soft orientation"
        # so alpha here = 0 near base (strict), 1 far from base (soft). Flip below if
        # you want strict-orientation only far away instead; see note underneath.
        alpha = 1.0 - alpha  # alpha=1 near base (strict), alpha=0 far from base (soft)


        # inside a modified debug call, or by instrumenting ik_new temporarily:
        print("alpha:", alpha)
        print("reach_dist:", reach_dist)

        if target_yaw is not None:
            desired_yaw = target_yaw
        else:
            desired_yaw = np.arctan2(ee_target_pos[1] - base_pos[1], ee_target_pos[0] - base_pos[0])
        yaw_quat = np.zeros(4)
        mujoco.mju_axisAngle2Quat(yaw_quat, np.array([0, 0, 1]), desired_yaw)
        flip_quat = np.array([0, 1, 0, 0])
        ee_target_quat = np.zeros(4)
        mujoco.mju_mulQuat(ee_target_quat, yaw_quat, flip_quat)

        qpos0 = self.d.qpos.copy()
        qvel0 = self.d.qvel.copy()

        q = self.d.qpos[:6].copy()

        max_step_per_iter = 0.05  # rad, per joint, per iteration — matches earlier singularity discussion
        for _ in range(max_iters):
            self.d.qpos[:n] = q[:n]
            mujoco.mj_kinematics(self.m, self.d)

            ee_pos = self.d.site_xpos[site_id]
            ee_mat = self.d.site_xmat[site_id].reshape(3, 3)
            ee_quat = np.zeros(4)
            mujoco.mju_mat2Quat(ee_quat, ee_mat.flatten())

            jacp = np.zeros((3, self.m.nv))
            jacr = np.zeros((3, self.m.nv))
            mujoco.mj_jacSite(self.m, self.d, jacp, jacr, site_id)
            Jp = jacp[:, :n]
            Jr = jacr[:, :n]

            neg_ee_quat = np.zeros(4)
            mujoco.mju_negQuat(neg_ee_quat, ee_quat)
            quat_err = np.zeros(4)
            mujoco.mju_mulQuat(quat_err, ee_target_quat, neg_ee_quat)
            if quat_err[0] < 0:
                quat_err = -quat_err
            rot_err = np.zeros(3)
            mujoco.mju_quat2Vel(rot_err, quat_err, 1.0)

            pos_err = ee_target_pos - ee_pos

            if np.linalg.norm(pos_err) < tol and np.linalg.norm(rot_err) < tol:
                break

            JrJrt = Jr @ Jr.T
            Jr_pinv = Jr.T @ np.linalg.solve(JrJrt + damping * np.eye(3), np.eye(3))
            qdot_rot = Jr_pinv @ rot_err

            N_strict = np.eye(n) - Jr_pinv @ Jr
            N = alpha * N_strict + (1 - alpha) * np.eye(n)

            JpJpt = Jp @ Jp.T
            Jp_pinv = Jp.T @ np.linalg.solve(JpJpt + damping * np.eye(3), np.eye(3))
            qdot_pos = N @ (Jp_pinv @ pos_err)

            qdot = alpha * qdot_rot + qdot_pos

            delta = qdot * step_scale
            delta = np.clip(delta, -max_step_per_iter, max_step_per_iter)
            q[:n] = q[:n] + delta

            q[:n] = np.clip(q[:n], self.m.jnt_range[:n, 0], self.m.jnt_range[:n, 1])

        self.d.qpos[:] = qpos0
        self.d.qvel[:] = qvel0
        mujoco.mj_forward(self.m, self.d)

        return q

    def move_to_target_smooth_real(self, q_target_sim, max_vel=None, dt=0.02):
        """q_target_sim: target joint angles in sim-space radians (as returned by ik_new)."""
        q_target_real = self.sim_to_real(q_target_sim[:6])
        final_goal = q_target_real.astype(int)
        print(final_goal)
        self.arm.set_and_wait_goal_pos(final_goal)

        """
        if max_vel is None:
            max_vel = np.array([1.0, 0.8, 1.0, 1.2, 1.2, 2.0])

        q_start_real = self.arm.read_position()
        q_start_sim = self.real_to_sim(q_start_real)

        delta = np.abs(q_target_sim[:6] - q_start_sim[:6])
        per_joint_time = delta / max_vel
        duration = max(per_joint_time.max(), 0.3)
        n_steps = max(int(duration / dt), 1)

        for step in range(1, n_steps + 1):
            alpha = step / n_steps
            alpha_smooth = 3 * alpha**2 - 2 * alpha**3
            q_interp_sim = q_start_sim[:6] + alpha_smooth * (q_target_sim[:6] - q_start_sim[:6])
            q_interp_real = self.sim_to_real(q_interp_sim)  # convert back before sending to servos

            final_goal = q_interp_real.astype(int)
            print(final_goal)
            time.sleep(dt)
        """

    def get_current_ee_pos(self):
        """Current end-effector position in world/base frame, from real encoders via FK."""
        self.sync_mujoco_to_real()
        site_id = self.m.site('ee_site').id
        return self.d.site_xpos[site_id].copy()

    def get_target_xy(self, grid_size=7, grid_spacing=0.005, threshold=0.5):
        """
        Runs the grasp-grid model on the current camera view, selects the best
        cell, and converts it to a world-frame (x, y) target -- consistent with
        how targets were computed during dataset generation.
        """
        row_idx, col_idx = self.get_best_spot()

        # this is the arm's CURRENT hovering position -- the same role hover_pos
        # played during dataset generation, since the grid offsets are always
        # relative to wherever the arm was hovering when the image was taken
        hover_pos = self.get_current_ee_pos()

        center = grid_size // 2
        dx = (row_idx - center) * grid_spacing
        dy = (col_idx - center) * grid_spacing # negate the y-axis offset
        # dy potentially backwards

        target_xy = hover_pos[:2] + np.array([dx, dy])

        return target_xy

    def attempt_grasp_real(self, start, grasp_height=0.02):
        """
        Grasp the piece under the arm (which must be at positions[start]['hover']),
        then lift by returning to that recorded hover pose with the gripper closed.
        """
        time.sleep(1.0)
        target_xy = self.get_target_xy(grid_size=7, grid_spacing=0.005, threshold=0.5)

        grasp_target = np.array([target_xy[0], target_xy[1], 0.02])  # grasp_height=0.02
        print("grasp_target:", grasp_target)

        q_grasp = self.ik_new(grasp_target, max_iters=500, target_yaw=GRASP_YAW)
        print("IK solution (sim-space):", q_grasp)
        print("delta from current pose:", q_grasp[:6] - self.d.qpos[:6])

        q_real_grasp = self.sim_to_real(q_grasp[:6])
        print("converted to real ticks:", q_real_grasp)

        q_current_real = self.arm.read_position()
        print("current real ticks:", q_current_real)
        print("tick delta:", q_real_grasp - q_current_real)

        grasp_target = np.array([target_xy[0], target_xy[1], grasp_height])

        # Same claw heading and opening as the sim grasp attempts (generate_data.py)
        q = self.ik_new(grasp_target, max_iters=500, damping=1e-2, target_yaw=GRASP_YAW)
        q[5] = GRIPPER_OPEN_SIM  # partly open (2400 ticks)
        self.move_checked(q, grasp_target, "descend to grasp (gripper open)")
        time.sleep(0.3)  # let servos settle -- no mj_step equivalent, just wait

        q[5] = 0.1  # close (careful: check real ctrlrange/servo limits match sim, per earlier bug)
        self.move_checked(q, grasp_target, "close gripper")
        time.sleep(0.3)

        # Lift by going back to the recorded hover pose: it's known to be reachable,
        # unlike an IK target straight above the grasp (8 cm up hit joint limits / failed to converge).
        # Keep the gripper at the same closed command so the piece isn't dropped.
        lift_pose = list(self.positions[start]['hover'])
        lift_pose[5] = int(self.sim_to_real(q[:6])[5])
        if self.confirm:
            print(f"\n[lift to '{start}' hover] goal ticks: {lift_pose}")
            input("  Press Enter to move (Ctrl+C to abort)... ")
        self.arm.set_and_wait_goal_pos(lift_pose)
        time.sleep(0.3)

    def move_checked(self, q_sim, ee_target_pos, label, pos_tol=0.005, site_name='ee_site'):
        """
        Check an IK solution before sending it to the real arm, then move.
        Refuses if the solved end-effector is more than pos_tol (m) from the target,
        or if an arm joint is outside the servo limits (set_goal_pos would silently clip it).
        With self.confirm, prints the move and waits for Enter.
        """
        # Forward kinematics on the solution, without disturbing the synced model state
        qpos0 = self.d.qpos.copy()
        self.d.qpos[:6] = q_sim[:6]
        mujoco.mj_kinematics(self.m, self.d)
        ee_pos = self.d.site_xpos[self.m.site(site_name).id].copy()
        self.d.qpos[:] = qpos0
        mujoco.mj_forward(self.m, self.d)

        pos_err = np.linalg.norm(ee_pos - ee_target_pos)
        if pos_err > pos_tol:
            raise RuntimeError(f"[{label}] IK did not converge: {pos_err * 1000:.1f} mm from target {ee_target_pos}")

        q_real = self.sim_to_real(q_sim[:6]).astype(int)
        # Joint 5 (gripper) is left out: closing past the limit on purpose is how it grips
        lo = np.array(self.arm.min_position_limit[:5])
        hi = np.array(self.arm.max_position_limit[:5])
        out = np.where((q_real[:5] < lo) | (q_real[:5] > hi))[0]
        if out.size:
            raise RuntimeError(f"[{label}] joints {out.tolist()} outside servo limits: "
                               f"ticks {q_real[:5].tolist()}, min {lo.tolist()}, max {hi.tolist()}")

        if self.confirm:
            q_now = self.arm.read_position()
            print(f"\n[{label}] target {np.round(ee_target_pos, 4)}, IK error {pos_err * 1000:.1f} mm")
            print("  goal ticks:", q_real.tolist())
            print("  tick delta:", (q_real - q_now).tolist())
            input("  Press Enter to move (Ctrl+C to abort)... ")

        self.move_to_target_smooth_real(q_sim, dt=0.02)
