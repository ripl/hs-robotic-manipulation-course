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
        qdot = np.dot(np.linalg.pinv(jac[:, :6]), ee_target_pos - ee_pos)
        # apply the joint velocities
        q_target_pos = qpos + qdot * 0.2
        return q_target_pos
    
    def ik_new(self, ee_target_pos, site_name='ee_site',
                        damping=1e-4, w_pos=1.0, w_rot=0.01):
        """
        :param ee_target_pos: numpy array of target end effector position (world/base frame)
        :param site_name: name of the end effector site
        :param damping: damping coefficient (lambda^2) for DLS
        :param w_pos: weight on position error
        :param w_rot: weight on orientation error (lower = less fighting with joint1)
        """
        site_id = self.m.site(site_name).id
        ee_pos = self.d.site_xpos[site_id]
        ee_mat = self.d.site_xmat[site_id].reshape(3, 3)
        ee_quat = np.zeros(4)
        mujoco.mju_mat2Quat(ee_quat, ee_mat.flatten())

        jacp = np.zeros((3, self.m.nv))
        jacr = np.zeros((3, self.m.nv))
        mujoco.mj_jacSite(self.m, self.d, jacp, jacr, site_id)

        qpos = self.read_position()

        # --- compute target orientation dynamically so it doesn't fight joint1 ---
        desired_yaw = np.arctan2(ee_target_pos[1], ee_target_pos[0])
        yaw_quat = np.zeros(4)
        mujoco.mju_axisAngle2Quat(yaw_quat, np.array([0, 0, 1]), desired_yaw)

        flip_quat = np.array([0, 1, 0, 0])  # point straight down ("grip from above")

        ee_target_quat = np.zeros(4)
        mujoco.mju_mulQuat(ee_target_quat, yaw_quat, flip_quat)

        # --- position error ---
        pos_err = ee_target_pos - ee_pos

        # --- orientation error as a rotation vector ---
        neg_ee_quat = np.zeros(4)
        mujoco.mju_negQuat(neg_ee_quat, ee_quat)
        quat_err = np.zeros(4)
        mujoco.mju_mulQuat(quat_err, ee_target_quat, neg_ee_quat)

        # keep quaternion on the short-arc side to avoid rot_err wrapping the long way
        if quat_err[0] < 0:
            quat_err = -quat_err

        rot_err = np.zeros(3)
        mujoco.mju_quat2Vel(rot_err, quat_err, 1.0)

        # --- weighted, stacked error and Jacobian ---
        err = np.concatenate([w_pos * pos_err, w_rot * rot_err])
        J = np.concatenate([w_pos * jacp[:, :6], w_rot * jacr[:, :6]], axis=0)

        # --- damped least squares ---
        JJt = J @ J.T
        lambda_sq_I = damping * np.eye(JJt.shape[0])
        qdot = J.T @ np.linalg.solve(JJt + lambda_sq_I, err)

        q_target_pos = qpos + qdot * 1.0
        return q_target_pos

    def set_target_pos(self, target_pos):
        self.d.ctrl = target_pos
