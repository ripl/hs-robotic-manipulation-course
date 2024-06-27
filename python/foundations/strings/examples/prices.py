def main():
    """
    Prompt the user for the number of items in their cart then calculate the 
    total price of items in a cart based on user input.

    Example:
    --------
    How many items are in the cart? 3
    Enter the price of item 1: 5.99
    Enter the price of item 2: 3.50
    Enter the price of item 3: 12.00
    The total price of all items is: 21.49
    """
    num_items = int(input('How many items are in the cart? '))
    total_price = 0

    for item in range(num_items):
        price = float(input(f'Enter the price of item {item + 1}'))
        total_price += price
    
    print(f'The total price of all the items is {total_price:.2f}')      

if __name__ == '__main__':
    main()
