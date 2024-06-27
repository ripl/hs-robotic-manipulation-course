def add_3_mul_4(num):
    """
    Add 3 to the num, then multiply by 4.

    >>> add_3_mul_4(2.0)
    20.0
    """
    num = num + 3
    num = num * 4
    return num

def calc_area(length=1, width=1):
    """
    Compute the area of a rectangle.

    >>> calc_area()
    1

    >>> calc_area(3)
    3

    >>> calc_area(12,3)
    36
    """
    return length * width