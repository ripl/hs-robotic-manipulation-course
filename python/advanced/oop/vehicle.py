class Car:
    """
    A class to represent a car.

    Examples:
    ---------
    >>> my_car = Car('Toyota', 'Corolla')
    >>> my_car.make
    'Toyota'
    >>> my_car.model
    'Corolla'
    >>> my_car.color
    'No color yet. You need to paint me.'
    >>> my_car.wheels
    4
    >>> my_car.gas
    30
    >>> my_car.size
    'Tiny'
    >>> my_car.paint('red')
    'Toyota Corolla is now red'
    >>> my_car.color
    'red'
    >>> my_car.drive()
    'Toyota Corolla goes vroom!'
    >>> my_car.gas
    20
    >>> my_car.pop_tire()
    >>> my_car.wheels
    3
    >>> my_car.drive()
    'Cannot drive!'
    >>> my_car.fill_gas()
    'Gas level: 40'
    >>> my_car.gas
    40
    >>> my_car.wheels = 4
    >>> my_car.drive()
    'Toyota Corolla goes vroom!'
    >>> my_car.gas
    30
    >>> my_truck = Car('Ford', 'F-150', 'Large')
    >>> my_truck.size
    'Large'
    """
    num_wheels = 4
    gas = 30
    headlights = 2
    size = 'Tiny'

    def __init__(self, make, model, size=None):
        self.make = make
        self.model = model
        self.color = 'No color yet. You need to paint me.'
        self.wheels = Car.num_wheels
        self.gas = Car.gas

        if size is None:
            self.size = Car.size
        else:
            self.size = size

    def paint(self, color):
        pass

    def drive(self):
        pass

    def pop_tire(self):
        pass

    def fill_gas(self):
        pass
