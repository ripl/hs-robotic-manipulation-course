from operator import add, mul, neg

def subtract(a, b):
    """
    Compute the difference between a and b.
    """
    return add(a, neg(b)) # a - b

def square(n):
    """
    Compute the square of n.
    """
    return mul(n, n) # n ** 2, n * n

def percent_difference(x, y):
    """
    Compute the percent difference between x and y.
    """
    difference = subtract(x, y)
    percent = difference / x * 100
    return percent

    
def main():
    print()
    print(12, 'squared is', square(12))
    print('5 - 4 is', subtract(5, 4))
    print('50 is', percent_difference(50, 40), '% greater than 40')
    print()

if __name__ == '__main__':
    main()
