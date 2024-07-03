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

def new_dict(input_dict):
    """
    Takes a dictionary and returns a new dictionary where 5 is added to each value.
    
    Args:
    input_dict (dict): A dictionary with integer values.

    Returns:
    dict: A new dictionary with each value increased by 5.
    
    Examples:
    >>> new_dict({"item1": 2, "item2": 7, "item3": 20})
    {'item1': 7, 'item2': 12, 'item3': 25}
    """
    pass

def check_same_values(input_dict):
    """
    Checks if all values in the dictionary are the same.

    Args:
    input_dict (dict): A dictionary with values.

    Returns:
    bool: True if all values are the same, False otherwise.
    
    Examples:
    >>> check_same_values({'item1': 'apple', 'item2': 'apple', 'item3': 'apple'})
    True
    >>> check_same_values({'item1': 'apple', 'item2': 'apple', 'item3': 'orange'})
    False
    """
    pass

def combine_dicts(input_dicts):
    """
    Combines a list of dictionaries into a single dictionary by summing the amounts of the same items.
    
    Args:
    input_dicts (list): A list of dictionaries with 'item' and 'amount' keys.

    Returns:
    dict: A combined dictionary with summed amounts for each item.
    
    Examples:
    >>> combine_dicts([{'item': 'item1', 'amount': 400}, {'item': 'item2', 'amount': 300}, {'item': 'item1', 'amount': 750}])
    {'item1': 1150, 'item2': 300}
    """
    pass


