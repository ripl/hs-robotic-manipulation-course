import mujoco
import numpy as np

class SimulatedRobot:
    def __init__(self, m, d) -> None:
        """
        :param m: mujoco model
        :param d: mujoco data
        """
        self.m = m
        self.d = d

    def _pos2pwm(self, pos: np.ndarray) -> np.ndarray:
        """
        :param pos: numpy array of joint positions in range [-pi, pi]
        :return: numpy array of pwm values in range [0, 4096]
        """
        return (pos / 3.14 + 1.) * 4096

    def _pwm2pos(self, pwm: np.ndarray) -> np.ndarray:
        """
        :param pwm: numpy array of pwm values in range [0, 4096]
        :return: numpy array of joint positions in range [-pi, pi]
        """
        return (pwm / 2048 - 1) * 3.14

    def _pwm2norm(self, x: np.ndarray) -> np.ndarray:
        """
        :param x: numpy array of pwm values in range [0, 4096]
        :return: numpy array of values in range [0, 1]
        """
        return x / 4096

    def _norm2pwm(self, x: np.ndarray) -> np.ndarray:
        """
        :param x: numpy array of values in range [0, 1]
        :return: numpy array of pwm values in range [0, 4096]
        """
        return x * 4096

    def read_position(self) -> np.ndarray:
        """
        :return: numpy array of current joint positions in range [0, 4096]
        """
        return self.d.qpos[:6]

    def read_velocity(self):
        """
        Reads the joint velocities of the robot.
        :return: list of joint velocities,
        """
        return self.d.qvel

    def read_ee_pos(self, joint_name='end_effector'):
        """
        :param joint_name: name of the end effector joint
        :return: numpy array of end effector position
        """
        joint_id = self.m.body(joint_name).id
        return self.d.geom_xpos[joint_id]

    def inverse_kinematics(self, ee_target_pos, joint_name='end_effector'):
        """
        :param ee_target_pos: numpy array of target end effector position
        :param joint_name: name of the end effector joint
        """
        joint_id = self.m.body(joint_name).id
        # get the current end effector position
        ee_pos = self.d.geom_xpos[joint_id]
        # compute the jacobian
        jac = np.zeros((3, self.m.nv))
        mujoco.mj_jacBodyCom(self.m, self.d, jac, None, joint_id)
        # compute target joint velocities
        qpos = self.read_position()
        qdot = np.dot(np.linalg.pinv(jac[:, :5]), ee_target_pos - ee_pos)
        # apply the joint velocities
        q_target_pos = qpos + qdot * 0.2
        return q_target_pos

    def ik_new(self, ee_target_pos, site_name='ee_site',
                        damping=1e-4, max_iters=500, tol=1e-4, step_scale=0.5,
                        far_dist=0.3, near_dist=0.12, base_body='base_link', target_yaw=None):
        """
        Hierarchical IK with base-relative, distance-adaptive orientation priority.
        alpha is computed once from how far the target is from the arm's base,
        not from the shrinking solve error.
        target_yaw: world-frame claw heading (rad). None points the claw away from the base.
        """
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

        q = self.read_position().copy()

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

    def set_target_pos(self, target_pos):
        self.d.ctrl = target_pos
