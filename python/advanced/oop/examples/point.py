from math import sqrt

class Point:
  """
  A class to represent a point in a 2D space.

  Examples:
  ---------
  >>> p1 = Point(0, 0)
  >>> p1
  Point(0, 0)
  >>> p2 = Point(1, 3)
  >>> p2.x
  1
  >>> p2.y
  3
  >>> p3 = p1.subtract(p2)
  >>> p3
  Point(-1, -3)
  >>> p4 = p3
  >>> p4
  Point(-1, -3)
  >>> Point.get_count()
  3
  >>> p2.distance(p3)
  6.71
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
  
  def distance(self, other):
    """
    Return the distance between two Point instances.

    Task: 
      Try to implement this method!

    Notes:
      The distance formula between points is √((x2 - x1)^2 + (y2 - y1)^2)
    """
    pass

  @classmethod
  def get_count(cls):
    """
    Returns the number of Point instances created.
    """
    return cls.quantity
