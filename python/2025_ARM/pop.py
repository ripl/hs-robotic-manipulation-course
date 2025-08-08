import pygame
import sys
import math
import random

width = 1280
height = 720
radius = 30
score = 0

circle_pos = (random.randint(0, width), random.randint(0, height))

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((width,height))
font = pygame.font.Font(None, 30)

def check_circle_collision() -> bool:
    mouse_pos = pygame.mouse.get_pos()
    if math.sqrt( (mouse_pos[0] - circle_pos[0])**2 + (mouse_pos[1] - circle_pos[1])**2 ) < radius:
        return True
    return False

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click
                if check_circle_collision():
                    score += 1
                    circle_pos = (random.randint(0,width), random.randint(0,height))
    score_surface = font.render(f'Score: {score}', True, "black")

    screen.fill('lightblue')
    pygame.draw.circle(screen,"purple",circle_pos,radius)
    screen.blit(score_surface,(50,50))
    pygame.display.update()
    clock.tick(60)  # limits FPS to 60
