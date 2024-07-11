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

    def __init__(self, piece):
        pass

    def __repr__(self):
        pass


class TicTacToe:
    """
    Represents a TicTacToe game instance.

    Example 1:
    -----------

    >>> p1 = Player('x')
    >>> p2 = Player('o')
    >>> board = ['x', 'o', None, 'x', None, None, None, None, None ]
    >>> game = TicTacToe(p1, p2, board)
    Your move, Player 2
    x | o |  
    ---------
    x |   |  
    ---------
      |   |  
    >>> game.place_piece(2, 0)
    Your move, Player 1
    x | o |  
    ---------
    x |   |  
    ---------
    o |   |  
    >>> game.curr_player_wins()
    False
    >>> game.place_piece(2, 0)
    Space is occupied!
    Your move, Player 1
    x | o |  
    ---------
    x |   |  
    ---------
    o |   |  
    >>> game.place_piece(3, 1)
    Invalid space!
    Your move, Player 1
    x | o |  
    ---------
    x |   |  
    ---------
    o |   |  
    >>> game.place_piece(1, 1)
    Your move, Player 2
    x | o |  
    ---------
    x | x |  
    ---------
    o |   |  
    >>> game.place_piece(2, 1)
    Your move, Player 1
    x | o |  
    ---------
    x | x |  
    ---------
    o | o |  
    >>> game.place_piece(2, 2)
    Player 1 Wins!
    x | o |  
    ---------
    x | x |  
    ---------
    o | o | x 
    >>> game.get_winner()
    'x'
    """
    def __init__(self, player1, player2, board=None):
        """
        Create an instance of TicTacToe.
        
        :param player1: The first player.
        :param player2: The second player.
        :param board: Optional initial board state.
        """
        self.p1 = player1
        self.p2 = player2
        
        if board is None:
            self.board = [None] * 9
            # Player 1 is always first
            self.curr_turn = player1.piece
        else:
            self.board = board
            # Determine which Players turn it is
            x_count = board.count('x')
            o_count = board.count('o')

            if x_count > o_count:
                self.curr_turn = player2.piece
            else:
                self.curr_turn = player1.piece

        # Record the current state of the board.
        self.history = [self.board.copy()]
                
        # Display board and current player's turn.
        print(self)

    def current_player(self):
        """
        Return the current player's piece.
        
        :returns: The piece of the current player.
        """
        pass
        
    def __repr__(self):
        """
        Draw the current state of the TicTacToe board.
        
        :returns: The string representation of the board.
        """
        board_str = ''
        
        # Build the board string here. Hint: Use format strings!
        
        return board_str

    def is_valid_move(self, row, col):
        """
        Determine if the given coordinates are a valid move.
        
        :param row: The row of the move.
        :param col: The column of the move.
        :returns: True if the move is valid, False otherwise.
        """
        pass

    def place_piece(self, row, col):
       """
        Handle updates to the state of the TicTacToe board.
        
        :param row: The row to place the piece.
        :param col: The column to place the piece.
        """
        pass

    def update(self):
        """
        Update the current turn of the player in the game ('x' or 'o').
        """
        pass

    def curr_player_wins(self):
        """
        Checks to see if the current player has a winning triple.
        
        :returns: True if the current player has won, False otherwise.
        """
        winning_triples = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # horizontal
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # vertical
            (0, 4, 8), (2, 4, 6)              # diagonal
        ]
        pass

    def get_winner(self):
        """
        Return the winner if there is one.
        
        :returns: The piece of the winner, or None if there is no winner.
        """
        pass

    def determine_draw(self):
        """
        Determine if there are no moves left on the board, resulting in a draw.
        
        :returns: True if the game is a draw, False otherwise.
        """
        pass

    def reset_game(self):
        """
        Reset the game to its initial state (an empty board).
        """
        pass
    
    def step_back(self):
        """
        Revert to the previous state of the game. 
        Hint: Use, self.history
        """
        pass
