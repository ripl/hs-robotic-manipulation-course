class Animal:
    """
    A class to represent an animal.
    """
    def __init__(self, name, age):
        """
        Initialize an Animal instance with a name and age.
        """
        self.name = name
        self.age = age

    def speak(self):
        """
        Return a generic sound for an animal.
        """
        return "Some sound"

    def __repr__(self):
        """
        Return a string representation of the Animal instance.
        """
        return f"Animal({self.name}, {self.age})"


class Dog(Animal):
    """
    A class to represent a dog, inherited from Animal.
    """
    def __init__(self, name, age, breed):
        """
        Initialize a Dog instance with a name, age, and breed.
        """
        super().__init__(name, age)
        self.breed = breed

    def speak(self):
        """
        Return the sound a dog makes.
        """
        return "Woof"

    def __repr__(self):
        """
        Return a string representation of the Dog instance.
        """
        return f"Dog({self.name}, {self.age}, {self.breed})"


class Cat(Animal):
    """
    A class to represent a cat, inherited from Animal.
    """
    def __init__(self, name, age, color):
        """
        Initialize a Cat instance with a name, age, and color.
        """
        super().__init__(name, age)
        self.color = color

    def speak(self):
        """
        Return the sound a cat makes.
        """
        return "Meow"

    def __repr__(self):
        """
        Return a string representation of the Cat instance.
        """
        return f"Cat({self.name}, {self.age}, {self.color})"


# Example usage
if __name__ == "__main__":
    dog = Dog("Buddy", 3, "Golden Retriever")
    cat = Cat("Whiskers", 2, "Black")

    print(dog)  # Dog(Buddy, 3, Golden Retriever)
    print(cat)  # Cat(Whiskers, 2, Black)
    print(dog.speak())  # Woof
    print(cat.speak())  # Meow
