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

        :param game: The current game instance.
        """
        pass

    def pro(self, game):
        """
        Either place a piece to win, to block the opponent, or randomly.

        :param game: The current game instance.
        """
        winning_triples = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # horizontal
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # vertical
            (0, 4, 8), (2, 4, 6)              # diagonal
        ]
        pass

    def minimax(self, game, depth, is_maximizing):
        """
        Implement the minimax algorithm to determine the best move for the AI.

        :param game: The current game instance.
        :param depth: The current depth in the game tree.
        :param is_maximizing: A boolean indicating if the current player is the maximizing player.
        :return: The optimal move score for the current board state.
        """
        # Evaluate the current state of the game
        score = self.evaluate_board(game)
        if score is not None:
            return score

        if is_maximizing:
            best_score = float('-inf')
            for pos in range(9):
                if game.is_valid_move(pos):
                    game.place_piece(pos, self.piece)
                    best_score = max(best_score, self.minimax(game, depth + 1, False))
                    game.remove_piece(pos)
            return best_score
        else:
            best_score = float('inf')
            opponent_piece = game.p1.piece if self.piece == game.p2.piece else game.p2.piece
            for pos in range(9):
                if game.is_valid_move(pos):
                    game.place_piece(pos, opponent_piece)
                    best_score = min(best_score, self.minimax(game, depth + 1, True))
                    game.remove_piece(pos)
            return best_score

    def evaluate_board(self, game):
        """
        Evaluate the board state and return a score if the game has ended.

        :param game: The current game instance.
        :return: A score representing the board evaluation (1 for win, -1 for loss, 0 for draw, None if the game is ongoing).
        """
        winner = game.check_winner()
        if winner == self.piece:
            return 1
        elif winner == (game.p1.piece if self.piece == game.p2.piece else game.p2.piece):
            return -1
        elif game.is_draw():
            return 0
        return None

    def expert(self, game):
        """
        Determine the best move for the SmartArm using the minimax algorithm.

        :param game: The current game instance.
        """
        best_score = float('-inf')
        best_move = None
        for pos in range(9):
            if game.is_valid_move(pos):
                game.place_piece(pos, self.piece)
                move_score = self.minimax(game, 0, False)
                game.remove_piece(pos)
                if move_score > best_score:
                    best_score = move_score
                    best_move = pos

        if best_move is not None:
            game.place_piece(best_move)