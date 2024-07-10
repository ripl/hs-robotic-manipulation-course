class Point:
  """
  A class to represent a point in a 2D space.

  Examples:
  ---------
  >>> p1 = Point(10, 2)
  >>> p1
  Point(10, 2)
  >>> p2 = Point(3, 1)
  >>> p3 = p1.subtract(p2)
  >>> p3
  Point(7, 1)
  """
  quantity = 0
    
  def __init__(self, x, y):
    """
    Initializes a new Point instance with x and y coordinates.
    """
    self.x_coordinate = x
    self.y_coordinate = y
    Point.quantity += 1
    
  def subtract(self, other): 
    """
    Subtracts the coordinates of another Point from this Point.

    Returns a new Point instance.
    """
    return Point(self.x_coordinate - other.x_coordinate, self.y_coordinate - other.y_coordinate)
    
  def __repr__(self):
    """
     Returns a string representation of the Point instance.
    """
    return f"Point({self.x_coordinate}, {self.y_coordinate})"
