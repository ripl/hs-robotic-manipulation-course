from math import pi

def main():
    """
    Print some facts about a circle with radius 10.
    """
    radius = 10
    area = round(pi * (radius ** 2), 2) 
    circumfrence = 2 * pi * radius

    print('The area is', area)
    print('The circumfrence is', round(circumfrence,2))

if __name__ == '__main__':
    main()
