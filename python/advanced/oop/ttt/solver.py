import random
from game import Arm

class SmartArm(Arm):
    """
    A solver class for TicTacToe with different difficulty levels.
    """

    def __init__(self, piece, game, lvl, config_path='../config.json', positions_path='../actions.json'):
        """
        Initialize the SmartArm instance.

        :param piece: The piece assigned to the SmartArm player (e.g., 'x' or 'o').
        :param game: The TicTacToe game instance.
        :param lvl: The difficulty level (e.g., 'beginner', 'intermediate', 'expert').
        :param config_path: Path to the configuration file for the robotic arm.
        :param positions_path: Path to the file containing actions or positions.
        """
        super().__init__(piece, config_path, positions_path)
        self.game = game
        self.lvl = lvl

    def make_move(self):
        """
        Make a move based on the specified difficulty level.
        """
        if self.lvl == 'beginner':
            self.beginner_move()
        elif self.lvl == 'intermediate':
            self.intermediate_move()
        elif self.lvl == 'expert':
            self.expert_move()
        else:
            raise ValueError("Invalid difficulty level. Choose 'beginner', 'intermediate', or 'expert'.")

    def beginner_move(self):
        """
        Make a random move.
        """
        move = random.choice(self.game.get_available_moves())
        self.game.place_piece(move)

    def intermediate_move(self):
        """
        Make a move to win if possible, otherwise block the opponent.
        """
        # Try to win
        for move in self.game.get_available_moves():
            self.game.place_piece(move)
            if self.game.curr_player_wins():
                return
            self.game.undo()

        # Block opponent
        opponent_piece = self.game.p1.piece if self.game.curr_turn == self.game.p2.piece else self.game.p2.piece
        for move in self.game.get_available_moves():
            self.game.place_piece(move)
            if self.game.curr_player_wins():
                self.game.undo()
                self.game.place_piece(move)
                return
            self.game.undo()

        # If no winning or blocking move, choose random
        self.beginner_move()

    def minimax(self, is_maximizing):
        """
        Minimax algorithm for optimal move calculation.
        """
        if self.game.curr_player_wins():
            return 1 if not is_maximizing else -1
        if self.game.determine_draw():
            return 0

        if is_maximizing:
            best_score = -float('inf')
            for move in self.game.get_available_moves():
                self.game.place_piece(move)
                score = self.minimax(False)
                self.game.undo()
                best_score = max(score, best_score)
            return best_score
        else:
            opponent_piece = self.game.p1.piece if self.game.curr_turn == self.game.p2.piece else self.game.p2.piece
            best_score = float('inf')
            for move in self.game.get_available_moves():
                self.game.place_piece(move)
                score = self.minimax(True)
                self.game.undo()
                best_score = min(score, best_score)
            return best_score

    def expert_move(self):
        """
        Make the best possible move using the minimax algorithm.
        """
        best_score = -float('inf')
        best_move = None
        for move in self.game.get_available_moves():
            self.game.place_piece(move)
            score = self.minimax(False)
            self.game.undo()
            if score > best_score:
                best_score = score
                best_move = move
        self.game.place_piece(best_move)
