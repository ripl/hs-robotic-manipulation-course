# Pygame Basics

Pygame is a set of Python modules designed for writing video games. It provides functionalities like creating graphics, handling input, and playing sounds, making it an excellent choice for beginners to learn game development and graphical programming. 

To install pygame onto your machine, run these commands at the terminal within the root folder:

```bash
# Create a virtual environment in the project root
python3 -m venv env

# Add the project to the PYTHONPATH in the virtual environment
echo 'export PYTHONPATH="$PYTHONPATH:/absolute/path/to/hs-robotic-manipulation-course"' >> env/bin/activate

# Activate the virtual environment
source env/bin/activate

# Install the dependencies (you only need to run this command once)
pip install -r requirements.txt

# To deactivate the virtual environment (only when you are within the virtual environment)
deactivate
```
## Game Loop

Pygame operates by continuously updating the game's `state` within a loop, monitoring various `events`. When events such as updating a variable or pressing keys on the keyboard occur, these actions trigger specific responses. The game is then `drawn` (re-rendered) on the screen to reflect the new state.

![Game Loop](https://eng.libretexts.org/@api/deki/files/12879/GWPFigure5.png?revision=1 )

The code segment that acts as the game loop is:

```python
running = True
while running:
    # Poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the game state (add your game logic here)

    # Fill the screen with a color to wipe away anything from the last frame
    screen.fill("purple")

    # Render the updated game state here

    # Redraw the new game state
    pygame.display.flip()

    # Limit FPS to 60
    clock.tick(60)
```

## Coordinate System

Pygame's coordinate system is based on pixels and follows the Cartesian coordinate system with some key differences. 

Here's a breakdown:

- The **origin (0, 0)** is located at the **top-left corner** of the screen.
- The **x-axis** increases as you move to the **right**.
- The **y-axis** increases as you move **downwards**.

## Colors

In Pygame, colors are defined using RGB (Red, Green, Blue) values. Each component (red, green, and blue) can have a value from 0 to 255, where 0 means no color and 255 
means full color. 

Here's how to create some basic colors:

```python
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
```

## Drawing Shapes

Pygame provides several functions for drawing shapes on a surface. The documentation for drawing shapes can be found here: https://www.pygame.org/docs/ref/draw.html

Below are examples of how to use these functions within a basic Pygame game loop.

```python
# Draw a red line
pygame.draw.line(screen, (255, 0, 0), (20, 30), (200, 30), 5)

# Draw a green rectangle
pygame.draw.rect(screen, (0, 255, 0), (60, 60, 120, 60), 2)

# Draw a blue circle
pygame.draw.circle(screen, (0, 0, 255), (200, 150), 40, 0)

# Draw a white ellipse inside a rectangle
pygame.draw.ellipse(screen, (255, 255, 255), (100, 100, 200, 100), 3)

# Draw a white ellipse inside a rectangle
pygame.draw.ellipse(screen, (255, 255, 255), (100, 100, 200, 100), 3)

# Draw a polygon with four vertices
pygame.draw.polygon(screen, (255, 0, 0), [(100, 100), (150, 200), (200, 100), (250, 200)], 0)

```

## Text

Pygame also allows you to render text on the screen using fonts. 

Here's how you can do it:

```python
# Define a font
font = pygame.font.Font(None, 74)  # None for default font, 74 is the size

# Get the list of available system fonts
available_fonts = pygame.font.get_fonts()

# Render the text
text = font.render('Hello, Pygame!', True, (255, 255, 255))
screen.blit(text, (300, 300))
```

### Creative Task

For the closing activity, use what you've learned to draw an image of your choice. This could be a simple house, a car, a tree, 
or any other recognizable object. Avoid abstract art and focus on creating a clear and identifiable image. 

Create a new file called `creative.py` and paste of copy of the template provided to you. Render your image in this file.

Here's an example of how to draw a simple house:

```python
# Draw a house
pygame.draw.rect(screen, (139, 69, 19), (150, 200, 100, 100))  # House base
pygame.draw.polygon(screen, (255, 0, 0), [(150, 200), (200, 150), (250, 200)])  # Roof
pygame.draw.rect(screen, (0, 0, 255), (180, 250, 40, 50))  # Door
pygame.draw.rect(screen, (0, 255, 0), (160, 220, 30, 30))  # Window 1
pygame.draw.rect(screen, (0, 255, 0), (210, 220, 30, 30))  # Window 2
```

**NOTE:** I expect you to draw something more spectactular than a simple house or lazy drawing.
