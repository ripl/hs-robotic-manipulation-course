# Graphics and Pygame

Pygame moves students from text-only programs to event loops, drawing, and interactive graphical state.

## Learning Goals

- Create a Pygame window.
- Understand the game loop.
- Read input events.
- Draw shapes and text.
- Track and update visual state.

## Game Loop

Most Pygame programs follow this structure:

```python
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("purple")

    # Update and draw the current game state here.

    pygame.display.flip()
    clock.tick(60)
```

## Coordinate System

Pygame coordinates start at the top-left corner.

- `x` increases to the right.
- `y` increases downward.
- Positions and sizes are measured in pixels.

## Drawing Shapes

```python
pygame.draw.line(screen, (255, 0, 0), (20, 30), (200, 30), 5)
pygame.draw.rect(screen, (0, 255, 0), (60, 60, 120, 60), 2)
pygame.draw.circle(screen, (0, 0, 255), (200, 150), 40, 0)
pygame.draw.polygon(screen, (255, 0, 0), [(100, 100), (150, 200), (200, 100)], 0)
```

## Creative Task

Students create a new file called `creative.py`, copy the Pygame template, and draw a recognizable image using shapes and colors.

## Next Activity

Use [Pop the Balloon](pop-the-balloon.md) after students understand the event loop and drawing basics. It adds mouse input, collision checks, scorekeeping, and an optional class-based extension.

## Graphics Sequence

| Module | Main interaction | Concepts |
| --- | --- | --- |
| [Pop the Balloon](pop-the-balloon.md) | Mouse clicks | Collision checks, random placement, scorekeeping |
| [Race for the Treasure](race-for-the-treasure.md) | Keyboard movement | Sprites, rectangles, two-player input |
| [Attack of the Clones](attack-of-the-clones.md) | Keyboard movement and enemy/collectible logic | Sprite-game structure, game state, extension design |
| [Tic-Tac-Toe GUI](tic-tac-toe-gui.md) | Keyboard square selection | Rendering board state, image assets, turn messages |
| [Connect Four](connect-four.md) | Mouse column selection | Board grids, token animation, computer strategy, minimax |

## Repository Materials

- Pygame basics: <https://github.com/ripl/hs-robotic-manipulation-course/blob/main/python/graphics/BASICS.md>
- Pygame examples: <https://github.com/ripl/hs-robotic-manipulation-course/tree/main/python/graphics>
- Connect Four code: <https://github.com/ripl/hs-robotic-manipulation-course/tree/main/python/2025_ARM>
