def mapAB(dictionary):
    """
    Modify and return the given dictionary as follows: 
    If both keys 'a' and 'b' are present, append their string values together and store the result under the key 'ab'.

    Examples:
    >>> mapAB({"a": "Hi", "b": "There"})
    {'a': 'Hi', 'ab': 'HiThere', 'b': 'There'}
    
    >>> mapAB({"a": "Hi"})
    {'a': 'Hi'}
    
    >>> mapAB({"b": "There"})
    {'b': 'There'}
    """
    pass


def topping3(dictionary):
    """
    Given a dictionary of food keys and topping values, modify and return the dictionary as follows:
    If the key "potato" has a value, set that as the value for the key "fries".
    If the key "salad" has a value, set that as the value for the key "spinach".

    Examples:
    >>> topping3({"potato": "ketchup"})
    {'potato': 'ketchup', 'fries': 'ketchup'}
    
    >>> topping3({"potato": "butter"})
    {'potato': 'butter', 'fries': 'butter'}
    
    >>> topping3({"salad": "oil", "potato": "ketchup"})
    {'salad': 'oil', 'spinach': 'oil', 'potato': 'ketchup', 'fries': 'ketchup'}
    """
    pass


def find_grades(grades, students):
    """
    grades is a dictionary mapping student names (str) to grades (str).
    students is a list of student names.
    Returns a list containing the grades for students (in the same order).

    Examples:
    >>> d = {'Ana': 'B', 'Matt': 'C', 'John': 'B', 'Katy': 'A'}
    >>> find_grades(d, ['Matt', 'Katy'])
    ['C', 'A']
    
    >>> find_grades(d, ['Ana', 'John'])
    ['B', 'B']
    
    >>> find_grades(d, ['John', 'Ana', 'Katy'])
    ['B', 'B', 'A']
    """
    pass


def count_words(input_string):
    """
    Given a string, return a dictionary where the keys are words and the values are the counts of those words.

    Examples:
    >>> count_words("apple banana apple cherry banana apple")
    {'apple': 3, 'banana': 2, 'cherry': 1}
    
    >>> count_words("a b a a b c")
    {'a': 3, 'b': 2, 'c': 1}
    
    >>> count_words("")
    {}
    """
    pass
