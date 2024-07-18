import json
import random
from robotics.robot.robot import Robot

class Player:
    """
    Represents a player in a TicTacToe instance.

    Examples:
    -----------

    >>> p1 = Player('x')
    >>> p2 = Player('o') 
    >>> p1
    Player 1 is "x"
    >>> p2
    Player 2 is "o"
    >>> p3 = Player('x')
    Warning: Cannot create more than two players.
    >>> p3 is None
    True
    """
    # cls variable
    player_count = 0

    def __new__(cls, piece, *args, **kwargs):
        if cls.player_count >= 2:
            print('Warning: Cannot create more than two players.')
            return None
        return super(Player, cls).__new__(cls)

    def __init__(self, piece):
        self.piece = piece
        Player.player_count += 1
        self.count = Player.player_count

    def __del__(self):
        Player.player_count -= 1

    def __repr__(self):
        return f'Player {self.count} is "{self.piece}"'

class Arm(Player):
    """
    Represents a Robotic arm in a TicTacToe instance.

    Examples:
    -----------

    >>> p1 = Player('x')
    >>> p2 = Arm('o') 
    >>> p1
    Player 1 is "x"
    >>> p2
    ArmPlayer 2 is "o"
    >>> p2.move_piece("A", 0)
    Moved piece from A to 0.
    """
    def __init__(self, piece, config_path='../config.json', positions_path='../actions.json'):
        """
        Create an Arm instance, inherit from the Player class.

        :param piece: The piece assigned to the Arm player (e.g., 'x' or 'o').
        :param config_path: Path to the configuration file for the robotic arm.
        :param positions_path: Path to the file containing actions or positions.
        """
        super().__init__(piece)

        # Load robot settings
        with open(config_path, 'r') as f:
            config = json.load(f)
            self.arm_config = config['arm']

        # Load game positions
        with open(positions_path, 'r') as f:
            self.positions = json.load(f)

        # Initialize the robotic arm with the loaded configuration
        self.arm = Robot(device_name=self.arm_config['device_name'], 
                         servo_ids=self.arm_config['servo_ids'],
                         velocity_limit=self.arm_config['velocity_limit'],
                         max_position_limit=self.arm_config['max_position_limit'],
                         min_position_limit=self.arm_config['min_position_limit'])

        # Move the arm to the home start position
        self.arm.set_and_wait_goal_pos(self.arm_config['home_pos'])

        # NOTE: This list will represent the available "start" pieces.
        self.pieces = ["A", "B", "C", "D", "E", "F"]

        self.used_pieces = []

    def __repr__(self):
        return f'ArmPlayer {self.count} is "{self.piece}"'
    
    def move_piece(self, start, end):
        """
        Move a piece from start to end position on the physical board.

        This method will use the robotic arm to pick up a piece from the 
        specified start position and place it at the specified end position.

        :param start: The start position on the physical board.
        :param end: The end position on the physical board.
        """
        valid_poses = ['hover', 'pre-grasp', 'grasp', 'post-grasp']

        for pose in valid_poses:
            self.arm.set_and_wait_goal_pos(self.positions[start][pose])

        for pose in reversed(valid_poses):
            self.arm.set_and_wait_goal_pos(self.positions[end][pose])

        self.arm.set_and_wait_goal_pos(self.arm_config["home_pos"])

    def clean_board(self, curr_board):
        """
        Reset the board by moving pieces back to their start positions.

        This method finds the pieces that belong to the robotic arm on the 
        board and moves them back to their designated start positions.

        :param curr_board: The current state of the board to be reset.
        """
        for space in range(len(curr_board)):
            if curr_board[space] == self.piece:
                self.move_piece(str(space), self.used_pieces.pop())


class SmartArm(Arm):
    """
    Represents a Robotic Arm which can play on the board on its own.

    >>> p1 = Player('x')
    >>> p2 = Arm('o') 
    >>> p1
    Player 1 is "x"
    >>> p2
    SmartArmPlayer 2 is "o"
    """

    def __init__(self, piece, lvl = 0):
        """
        Create a Robotic Arm instance that can interact with the physical board autonomously.
        
        :param piece: The piece the robotic arm will play with.
        :param lvl: The level of autonomy or intelligence of the robotic arm. Default is 0.
        """
        super().__init__(piece)
        
        if lvl == 0:
            self.play = self.novice
        elif lvl == 1:
            self.play = self.pro
        else:
            self.play = self.expert

    def __repr__(self):
        return f'SmartArmPlayer {self.count} is "{self.piece}"'
    
    def novice(self, game):
        """
        Randomly place a piece on the board.
        """
        pass

    def pro(self, game):
        """
        Either place a piece to win, to block the opponent, or randomly.
        """
        pass

    def expert(self, game):
        """
        Always play the optimal move
        """
        pass    