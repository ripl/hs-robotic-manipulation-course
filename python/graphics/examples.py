# Example file showing a basic pygame "game loop"
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Pygame Template")
clock = pygame.time.Clock()
running = True

# initialize colors
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (51,51,255)
LIGHT_GREY = pygame.Color("lightgrey")

font = pygame.font.Font(None, 74)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(WHITE)

    # RENDER YOUR GAME HERE
    pygame.draw.line(screen, BLUE, (20,30), (200,30), 5)

    pygame.draw.rect(screen, LIGHT_GREY, (60,60, 120, 60))

    pygame.draw.rect(screen, (255,0,0), (260,60, 120, 60),5)

    pygame.draw.circle(screen, (0,255,0), (200, 150), 40, 0)

    pygame.draw.ellipse(screen, BLACK, (100, 100, 200, 100), 3)

    move_x = 300

    pygame.draw.polygon(screen, (255, 0, 0), [(100 + move_x, 100), (150 + move_x, 200), (200 + move_x, 100), (250 + move_x, 200)], 0)

    text = font.render("Hello, world", True,BLACK)
    screen.blit(text, (300, 300))


    # Draw a house
    pygame.draw.rect(screen, (139, 69, 19), (150, 200, 100, 100))  # House base
    pygame.draw.polygon(screen, (255, 0, 0), [(150, 200), (200, 150), (250, 200)])  # Roof
    pygame.draw.rect(screen, (0, 0, 255), (180, 250, 40, 50))  # Door
    pygame.draw.rect(screen, (0, 255, 0), (160, 220, 30, 30))  # Window 1
    pygame.draw.rect(screen, (0, 255, 0), (210, 220, 30, 30))  # Window 2
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
