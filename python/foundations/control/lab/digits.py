####################################
# Part A: Has Digit
# ##################################
def has_digit(n, k):
    """
    Returns whether k is a digit in n.

    Hint: while loop, // or %

    >>> has_digit(10, 1)
    True
    >>> has_digit(12, 7)
    False
    """
    while n > 0:
        digit = n % 10
        if digit == k:
            return True
        n //= 10
    return False

####################################
# Part B: Unique Digits
# ##################################
def unique_digits(n):
    """
    Return the number of unique digits in positive integer n.

    Hint: Use has_digit()

    >>> unique_digits(8675309) # All are unique
    7
    >>> unique_digits(13173131) # 1, 3, and 7
    3
    >>> unique_digits(101) # 0 and 1
    2
    """
    count = 0
    for digit in range(10):
        if has_digit(n, digit):
            count += 1
    return count

####################################
# Part C: Ordered Digits
# ##################################
def ordered_digits(x):
    """
    Return True if the (base 10) digits of X>0 are in non-decreasing
    order, and False otherwise.

    >>> ordered_digits(5)
    True
    >>> ordered_digits(11)
    True
    >>> ordered_digits(127)
    True
    >>> ordered_digits(1357)
    True
    >>> ordered_digits(21)
    False
    """
    pass

####################################
# Part D: Sum Digits
# ##################################
def sum_digits(y):
    """
    Sum all the digits of y.

    >>> sum_digits(10) # 1 + 0 = 1
    1
    >>> sum_digits(4224) # 4 + 2 + 2 + 4 = 12
    12
    >>> sum_digits(1234567890)
    45
    """
    sum = 0
    while n > 0:
        digit = n % 10
        
        sum += digit

        n //= 10
    return sum

