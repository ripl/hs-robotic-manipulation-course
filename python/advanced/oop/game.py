class Player:
    """
    Prepresents a player in a TicTacToe instance.

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
    pass



class TicTacToe:
    """
    
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

        # attributes to determine whose turn
        self.switch_players = False


    def __repr__(self):
        """
        Draw the current state of the TicTacToe board. 
        """
        pass

    def handle_move(self, piece, row, col):
        """
        Handle updates to the state of the TicTacToe board.
        """
        pass

    def update(self):
        """
        Update the current turn of the player in the game.
        """
        pass

    def curr_player_wins(self):
        """
        Checks to see if the current player has a winning triple.
        """
        horizontal_triples = [(0,1,2), (3,4,5), (6,7,8)]
        vertical_triples = [(0,3,6), (1,4,7), (2,5,8)]
        diagonal_triples = [(0,4,8), (2,4,6)]

    def determine_draw(self):
        """
        Determine if there are no moves left on the board, resulting in a draw.
        """