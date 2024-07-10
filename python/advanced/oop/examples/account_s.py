class BankAccount:
    """
    A class to represent a basic bank account.

    Examples:
    ---------
    >>> acc1 = BankAccount("John Doe", 1000)
    >>> acc1
    BankAccount(John Doe, 1000)
    >>> acc1.account_name()
    'John Doe'
    >>> acc1.balance()
    1000
    >>> acc1.deposit(500)
    1500
    >>> acc1.withdraw(200)
    1300
    >>> acc2 = BankAccount("Jane Doe", 500)
    >>> acc2
    BankAccount(Jane Doe, 500)
    >>> acc1.transfer(acc2, 300)
    Transferred 300 to Jane Doe
    >>> acc1.balance()
    1000
    >>> acc2.balance()
    800
    >>> acc1.transfer(acc2, 2000)
    Insufficient funds for transfer.
    >>> acc1.convert_to("EUR")
    900.0
    >>> acc1.convert_to("MXN")
    18100.0
    >>> acc1.convert_to("GBP")
    Invalid currency. Must be 'USD', 'EUR', or 'MXN'.
    """
    
    conversion_rates = {
        "USD": 1.0,    # American Dollar
        "EUR": 0.9,    # Euro
        "MXN": 18.1    # Mexican Peso
    }

    def __init__(self, name, initial_deposit=0):
        """
        Create a BankAccount instance with a name and initial deposit.
        """
        self.__name = name
        self.__balance = initial_deposit

    def account_name(self):
        """
        Return the name of the account holder.
        """
        return self.__name

    def balance(self):
        """
        Return the current balance of the account.
        """
        return self.__balance

    def withdraw(self, amount):
        """
        Withdraw a specified amount from the account.
        """
        self.__balance -= amount
        return self.__balance

    def deposit(self, amount):
        """
        Deposit a specified amount into the account.
        """
        self.__balance += amount
        return self.__balance

    def transfer(self, other, amount):
        """
        Transfer a specified amount to another BankAccount.
        """
        if self.__balance >= amount:
            self.withdraw(amount)
            other.deposit(amount)
            print(f"Transferred {amount} to {other.account_name()}")
        else:
            print("Insufficient funds for transfer.")

    def convert_to(self, currency):
        """
        Convert the account balance to the specified currency.
        """
        if currency not in BankAccount.conversion_rates:
            print("Invalid currency. Must be 'USD', 'EUR', or 'MXN'.")
            return None
        return self.__balance * BankAccount.conversion_rates[currency]

    def __repr__(self):
        """
        Return a string representation of the BankAccount instance.
        """
        return f"BankAccount({self.__name}, {self.__balance})"
