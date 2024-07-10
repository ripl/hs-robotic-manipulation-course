class BankAccount:
    """
    A class to represent a basic bank account.

    Examples:
    ---------
    >>> acc1 = BaseAccount("John Doe", 1000)
    >>> acc1
    BaseAccount(John Doe, 1000)
    >>> acc1.account_name()
    'John Doe'
    >>> acc1.balance()
    1000
    >>> acc1.deposit(500)
    1500
    >>> acc1.withdraw(200)
    1300
    >>> acc2 = BaseAccount("Jane Doe", 500)
    >>> acc2
    BaseAccount(Jane Doe, 500)
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
        self.__name = name
        self.__balance = initial_deposit

    def account_name(self):
        return self.__name

    def balance(self):
        return self.__balance

    def withdraw(self, amount):
        self.__balance -= amount
        return self.__balance

    def deposit(self, amount):
        self.__balance += amount
        return self.__balance

    def transfer(self, other, amount):
        if self.__balance >= amount:
            self.withdraw(amount)
            other.deposit(amount)
            print(f"Transferred {amount} to {other.account_name()}")
        else:
            print("Insufficient funds for transfer.")

    def convert_to(self, currency):
        if currency not in BaseAccount.conversion_rates:
            print("Invalid currency. Must be 'USD', 'EUR', or 'MXN'.")
            return None
        return self.__balance * BaseAccount.conversion_rates[currency]

    def __repr__(self):
        return f"BankAccount({self.__name}, {self.__balance})"
