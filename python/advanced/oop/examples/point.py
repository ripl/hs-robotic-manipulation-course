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
  >>> p2.x_coordinate
  1
  >>> p2.y_coordinate
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
  6.32
  >>> p4 = p2 + p3
  >>> p4
  Point(0, 0)
  """
  quantity = 0 # class attribute
    
  def __init__(self, x, y):
    """
    Initializes a new Point instance with x and y coordinates.
    """
    self.x_coordinate = x
    self.y_coordinate = y
    Point.quantity += 1 # access using the class Name
    
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
  
  def __add__(self, other):
    return Point(self.x_coordinate + other.x_coordinate, self.y_coordinate + other.y_coordinate)

  def distance(self, other):
    """
    Return the distance between two Point instances.

    Task: 
      Try to implement this method!

    Notes:
      The distance formula between points is √((x2 - x1)^2 + (y2 - y1)^2)
    """
    distance = sqrt((other.x_coordinate - self.x_coordinate)** 2 + (other.y_coordinate - self.y_coordinate)** 2)
    return round(distance, 2)

  @classmethod # Decorator
  def get_count(cls):
    """
    Returns the number of Point instances created.
    """
    return cls.quantity
