class Point:
    """
    Represents a 2D point.
    """
    def __init__(self, x, y):
        """
        Creates a Point object.
        """
        self.x_coordinate = x
        self.y_coordinate = y


    def __repr__(self):
        """
        String representation of the Point object.
        """
        return f"Point({self.x_coordinate}, {self.y_coordinate})"   
