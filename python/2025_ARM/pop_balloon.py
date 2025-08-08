import pygame
import sys
import math
import random

width = 1280
height = 720
radius = 30
count = 6

class Balloon():
    def __init__(self, color):
        self.color = color
        self.position = (0,0)
        self.glide_time = 0
        self.delta_x=0.0
        self.delta_y=0.0

    def set_position(self,position):
        self.position = position

    def get_position(self):
        return self.position
    
    def get_color(self):
        return self.color
    
    def draw(self):
        pygame.draw.circle(screen,self.color,self.position,radius)
    
    def glide(self,seconds):
        if self.glide_time==0:
            self.glide_time=seconds   
            new_pos = (random.randint(0,width), random.randint(0,height))
            self.delta_x= (new_pos[0]-self.position[0])/seconds
            self.delta_y= (new_pos[1]-self.position[1])/seconds
        self.set_position((self.position[0]+self.delta_x,self.position[1]+self.delta_y))
        self.glide_time = self.glide_time - 1

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((width,height))
font = pygame.font.Font(None, 30)

def check_circle_collision(mouse_pos,balloon_pos) -> bool:
    if math.sqrt((mouse_pos[0] - balloon_pos[0])**2 + (mouse_pos[1] - balloon_pos[1])**2 ) < radius:
        return True
    return False

colors = ["pink","red","purple","blue","yellow"]

balloons = []
for i in range(6):
    for color in colors:
        balloons.append(Balloon(color))

for balloon in balloons:
    balloon.set_position((random.randint(0,width),random.randint(0,height)))

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click
                mouse_pos = pygame.mouse.get_pos()
                remove_balloon = False
                balloon_number = -1
                index = -1
                for balloon in balloons:
                    balloon_number += 1
                    balloon_color = balloon.get_color()
                    balloon_pos = balloon.get_position()
                    if balloon_color=="pink" and check_circle_collision(mouse_pos,balloon_pos):
                        count -= 1
                        remove_balloon = True
                        index = balloon_number
                if remove_balloon:
                    balloons.pop(index)
 
    if (count>0):                
        count_surface = font.render(f'Count: {count}', True, "black")
    else:
        count_surface = font.render('You won!', True, "black")
    screen.fill('lightblue')
    for balloon in balloons:
        balloon.glide(random.randint(90,120))
        balloon.draw()
    screen.blit(count_surface,(50,50))
    pygame.display.update()
    clock.tick(60)  # limits FPS to 60