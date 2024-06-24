def main():
    """
    Calculate the tip amount based on the meal cost and the tip percentage.
    """
    dollars = dollars_to_float(input("How much was the meal? "))
    percent = percent_to_float(input("What percentage would you like to tip? "))
    tip = dollars * percent
    print(f"Leave ${tip:.2f}")


def dollars_to_float(d):
  """
  Convert a dollar amount from a string formatted as $##.## to a float.
  """
  # TODO


def percent_to_float(p):
  """
  Convert a percentage from a string formatted as ##% to a float.
  """
    # TODO


main()
