def divisible_by_k(n, k):
    """
    List all the numbers from 1 to n that are divisible by k. 
    Return the count of divisible number.s

    >>> a = divisible_by_k(10, 2)  # 2, 4, 6, 8, and 10 are divisible by 2
    2
    4
    6
    8
    10
    >>> a
    5
    >>> b = divisible_by_k(3, 1)  # 1, 2, and 3 are divisible by 1
    1
    2
    3
    >>> b
    3
    >>> c = divisible_by_k(6, 7)  # There are no integers up to 6 divisible by 7
    >>> c
    0
    """
    count = 0   # Keep track of the number of divisible i's by k
    i = 1

    while i <= n:
        if i % k == 0:
            print(i)
            count += 1

        i += 1
    return count