import random
from game import TicTacToe, Player


class TicTacToeSolver:
    """
    A solver class for TicTacToe with different difficulty levels.

    This solver is ChatGPT Produced.
    """

    def __init__(self, game):
        self.game = game

    def beginner_move(self):
        """
        Make a random move.
        """
        move = random.choice(self.game.get_available_moves())
        self.game.make_move(move, self.game.curr_turn)

    def intermediate_move(self):
        """
        Make a move to win if possible, otherwise block the opponent.
        """
        for move in self.game.get_available_moves():
            self.game.make_move(move, self.game.curr_turn)
            if self.game.curr_player_wins():
                return
            self.game.reset_move(move)

        opponent_piece = self.game.p1.piece if self.game.curr_turn == self.game.p2.piece else self.game.p2.piece
        for move in self.game.get_available_moves():
            self.game.make_move(move, opponent_piece)
            if self.game.curr_player_wins():
                self.game.reset_move(move)
                self.game.make_move(move, self.game.curr_turn)
                return
            self.game.reset_move(move)

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
                self.game.make_move(move, self.game.curr_turn)
                score = self.minimax(False)
                self.game.reset_move(move)
                best_score = max(score, best_score)
            return best_score
        else:
            opponent_piece = self.game.p1.piece if self.game.curr_turn == self.game.p2.piece else self.game.p2.piece
            best_score = float('inf')
            for move in self.game.get_available_moves():
                self.game.make_move(move, opponent_piece)
                score = self.minimax(True)
                self.game.reset_move(move)
                best_score = min(score, best_score)
            return best_score

    def expert_move(self):
        """
        Make the best possible move using the minimax algorithm.
        """
        best_score = -float('inf')
        best_move = None
        for move in self.game.get_available_moves():
            self.game.make_move(move, self.game.curr_turn)
            score = self.minimax(False)
            self.game.reset_move(move)
            if score > best_score:
                best_score = score
                best_move = move
        self.game.make_move(best_move, self.game.curr_turn)
