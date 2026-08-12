import unittest
from unittest import mock

from robotics.robot.robot import Robot


class RobotMotionSafetyTests(unittest.TestCase):
    def test_wait_timeout_disables_torque(self):
        robot = Robot.__new__(Robot)
        robot.set_goal_pos = mock.Mock()
        robot.read_velocity = mock.Mock(return_value=[5, 5, 5, 5, 5, 5])
        robot._disable_torque = mock.Mock()

        with self.assertRaises(TimeoutError):
            robot.set_and_wait_goal_pos([0] * 6, timeout=0.01)

        robot._disable_torque.assert_called_once()
