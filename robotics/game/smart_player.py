import json
import random
from robotics.robot.robot import Robot
from players import Player

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
            self.arm_config = config["arm1"]
            self.arm_config = config["arm2"]

        # Load game positions
        with open(positions_path, 'r') as f:
            self.positions = json.load(f)

        if piece =='x':

        # Initialize the robotic arm with the loaded configuration
            self.arm = Robot(device_name=self.arm_config_1['device_name'], 
                            servo_ids=self.arm_config_1['servo_ids'],
                            velocity_limit=self.arm_config_1['velocity_limit'],
                            max_position_limit=self.arm_config_1['max_position_limit'],
                            min_position_limit=self.arm_config_1['min_position_limit'],
                            position_p_gain=self.arm_config_1['position_p_gain'],
                            position_i_gain=self.arm_config_1['position_i_gain'],)
        elif piece == "o":
            self.arm = Robot(device_name=self.arm_config_2['device_name'], 
                            servo_ids=self.arm_config_2['servo_ids'],
                            velocity_limit=self.arm_config_2['velocity_limit'],
                            max_position_limit=self.arm_config_2['max_position_limit'],
                            min_position_limit=self.arm_config_2['min_position_limit'],
                            position_p_gain=self.arm_config_2['position_p_gain'],
                            position_i_gain=self.arm_config_2['position_i_gain'],)

        # Move the arm to the home start position
        self.arm.set_and_wait_goal_pos([2048, 1800, 1850, 1100, 2048, 2048])

        # NOTE: This list will represent the available "start" pieces.
        self.pieces = ["A", "B", "C", "D", "E"]

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
    Inherits from the Arm class.

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
        possible_moves = self.get_possible_moves(game)

        random_move = random.choice(possible_moves)

        game.place_piece(random_move)

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

        possible_moves = self.get_possible_moves(game)

        if game.p1 is self:
            opp_piece = game.p2.piece
        else:
            opp_piece = game.p1.piece

        for move in possible_moves:
            self.pseudo_place_piece(game, move, self.piece)
            win = game.current_player_wins()
            self.pseudo_undo(game, move)
            if win:
                game.place_piece(move)
                return
        
        for move in possible_moves:
            game.update()
            self.pseudo_place_piece(game, move, opp_piece)
            block = game.current_player_wins()
            self.pseudo_undo(game, move)
            if block:
                game.place_piece(move)
                return
            
        self.novice(game)
       

    def minimax(self, is_max_turn, maximizer_mark, game, depth):
        """
        Implement the minimax algorithm to determine the best move for the AI.

        :param is_max_turn: A boolean indicating if the current player is the maximizing player.
        :param maximizer_mark: The mark of the maximizing player ('x' or 'o').
        :param game: The current game instance.
        :param depth: The depth of the current call.
        :return: The optimal move score for the current board state.
        """
        if game.get_winner() is not None and game.get_winner() != self.piece:
            return 10 - depth
        elif game.get_winner() == self.piece:
            return depth - 10
        elif game.determine_draw():
            return 0
        
        depth += 1

        scores = []
        for pos in self.get_possible_moves(game):
            self.pseudo_place_piece(game, pos, maximizer_mark)
            scores.append(self.minimax(not is_max_turn, game.curr_turn, game, depth))
            self.pseudo_undo(game, pos)

        return max(scores) if is_max_turn else min(scores)

    def expert(self, game):
        """
        Determine the best move for the AI using the minimax algorithm.

        :param game: The current game instance.
        """
        best_score = float('-inf')
        best_move = None
        possible_moves = self.get_possible_moves(game)
        random.shuffle(possible_moves)
        for pos in possible_moves:
            self.pseudo_place_piece(game, pos, self.piece)
            score = self.minimax(False, game.curr_turn, game, 0)
            self.pseudo_undo(game, pos)
            if score > best_score:
                best_score = score
                best_move = pos
        game.place_piece(best_move)

    def pseudo_place_piece(self, game, pos, piece):
        """
        Place a piece on the board.

        :param game: The current game instance.
        :param pos: The position on the board.
        :param piece: The piece to place ('x' or 'o').
        """
        game.board[pos] = piece
        game.update()

    def pseudo_undo(self, game, pos):
        """
        Undo a move by clearing the board position.

        :param game: The current game instance.
        :param pos: The position on the board to clear.
        """
        game.board[pos] = None
        game.update()

    def get_possible_moves(self, game):
        """
        Get a list of possible moves.

        :param game: The current game instance.
        :return: A list of possible moves (board positions that are None).
        """
        return [indx for indx, space in enumerate(game.board) if space is None]
