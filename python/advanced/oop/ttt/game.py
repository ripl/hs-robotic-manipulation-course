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

    Examples:
    -----------

    >>> p1 = Player('x')
    >>> p2 = Player('o')
    >>> game = TicTacToe(p1, p2)
    >>> game.place_piece(0, 0)  # Player 1 places 'x' at (0, 0)
    x |   |  
    ---------
      |   |  
    ---------
      |   |  
    >>> game.place_piece(0, 1)  # Player 2 places 'o' at (0, 1)
    x | o |  
    ---------
      |   |  
    ---------
      |   |  
    >>> game.place_piece(1, 0)  # Player 1 places 'x' at (1, 0)
    x | o |  
    ---------
    x |   |  
    ---------
      |   |  
    >>> game.place_piece(1, 1)  # Player 2 places 'o' at (1, 1)
    x | o |  
    ---------
    x | o |  
    ---------
      |   |  
    >>> game.place_piece(2, 0)  # Player 1 places 'x' at (2, 0)
    x | o |  
    ---------
    x | o |  
    ---------
    x |   |  
    >>> game.place_piece(2, 2)  # Player 2 places 'o' at (2, 2)
    x | o |  
    ---------
    x | o |  
    ---------
    x |   | o
    Player o wins!
    """
    def __init__(self, player1, player2):
        """
        Create an instance of TicTacToe
        """
        self.board = [None] * 9
        
        # Player 1 is always first
        self.curr_turn = player1.piece
        self.p1 = player1
        self.p2 = player2

    def __repr__(self):
        """
        Draw the current state of the TicTacToe board. 
        """
        def format_piece(piece):
            return piece if piece is not None else ' '

        board_str = "\n".join([
            f"{format_piece(self.board[0])} | {format_piece(self.board[1])} | {format_piece(self.board[2])}",
            "---------",
            f"{format_piece(self.board[3])} | {format_piece(self.board[4])} | {format_piece(self.board[5])}",
            "---------",
            f"{format_piece(self.board[6])} | {format_piece(self.board[7])} | {format_piece(self.board[8])}"
        ])
        return board_str

    def place_piece(self, row, col):
        """
        Handle updates to the state of the TicTacToe board.

        Possible outputs:
            1) This spot is already taken. Please choose another spot.
            2) Player x wins!
            3) Player o wins!
            4) This game is a draw!
        """
        pass

    def update(self):
        """
        Update the current turn of the player in the game.

        Hint: You will need self.curr_turn and self.p1, self.p2 objects
        """
        pass

    def curr_player_wins(self):
        """
        Checks to see if the current player has a winning triple.
        """
        horizontal_triples = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
        vertical_triples = [(0, 3, 6), (1, 4, 7), (2, 5, 8)]
        diagonal_triples = [(0, 4, 8), (2, 4, 6)]
        pass

    def determine_draw(self):
        """
        Determine if there are no moves left on the board, resulting in a draw.
        """
        pass
