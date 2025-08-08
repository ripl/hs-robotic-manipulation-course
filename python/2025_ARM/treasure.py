import pygame
import sys
import math
import random

width = 1280
height = 720
step = 25

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1280,720))

font = pygame.font.Font(None, 30)

surface1 = pygame.image.load("Fox.png")
player1 = pygame.transform.scale(surface1, (64, 64))
p1_rect = player1.get_rect()
p1_rect.center = (100,height//2)
p1_score = 0
surface2 = pygame.image.load("Pig.png")
player2 = pygame.transform.scale(surface2, (64, 64))
p2_rect = player1.get_rect()
p2_rect.center = (width-100,height//2)
p2_score = 0
treasure = pygame.image.load("Rose.png")
t_rect = player1.get_rect()
t_rect.center = (width//2,height//2)

running = True

while running:
    clock.tick(60)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                p2_rect.move_ip(0,-step)
            if event.key == pygame.K_DOWN:
                p2_rect.move_ip(0,step)
            if event.key == pygame.K_LEFT:
                p2_rect.move_ip(-step,0)
            if event.key == pygame.K_RIGHT:
                p2_rect.move_ip(step,0)
            if event.key == pygame.K_w:
                p1_rect.move_ip(0,-step)
            if event.key == pygame.K_s:
                p1_rect.move_ip(0,step)
            if event.key == pygame.K_a:
                p1_rect.move_ip(-step,0)
            if event.key == pygame.K_d:
                p1_rect.move_ip(step,0)

    hit = pygame.Rect.collidelist(t_rect,[p1_rect,p2_rect])
    if  hit!=-1:
        t_rect.update((random.randint(64,width-64),random.randint(64,height-64)), (64,64) )
        if hit==0:
            p1_score += 1
        else:
            p2_score += 1
    if p1_score < 10 and p2_score < 10:
        p1_score_surface = font.render(f'Fox Score: {p1_score}', True, "black")
        p2_score_surface = font.render(f'Pig Score: {p2_score}', True, "black")
    else:
        if p1_score < 10:
            p1_score_surface = font.render(f'Fox Loses: {p1_score}', True, "black")
            p2_score_surface = font.render(f'Pig Wins: {p2_score}', True, "black")
        else:
            p1_score_surface = font.render(f'Fox Wins: {p1_score}', True, "black")
            p2_score_surface = font.render(f'Pig Loses: {p2_score}', True, "black")
    screen.fill('lightblue')
    screen.blit(player1,p1_rect)
    screen.blit(player2,p2_rect)
    screen.blit(treasure,t_rect)
    screen.blit(p1_score_surface,(50,50))    
    screen.blit(p2_score_surface,(width-150,50))    
    pygame.display.flip()
pygame.quit()
sys.exit()