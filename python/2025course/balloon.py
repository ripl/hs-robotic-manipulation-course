import pygame
import sys
import math
import random

width = 1280
height = 720
radius = 30
wx = 50
wy = 70

circle_pos = (random.randint(0, width//2), random.randint(0, height//2))

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1280,720))

font = pygame.font.Font(None, 30)


class Balloon():
    def __init__(self, color):
        self.color = color
        self.position = (0,0)
        self.glide_time = 0
        self.delta_x = 0.0
        self.delta_y = 0.0

    def get_color(self):
        return self.color

    def set_position(self, position):
        self.position = position
    
    def draw(self):
        pos = (self.position[0]-wx//2,self.position[1]-wy//2)
        pygame.draw.ellipse(screen,self.color,(pos,(wx,wy)))
        pygame.draw.lines(screen,self.color,False,[(pos[0]+wx//2,pos[1]+wy),
                                                (pos[0]+wx//2+10,pos[1]+wy+15),
                                                (pos[0]+wx//2-5,pos[1]+wy+20),
                                                (pos[0]+wx//2+3,pos[1]+wy+35)],width=5)
    def check_collision(self, mouse_pos):
        if math.sqrt( (mouse_pos[0] - self.position[0])**2 + (mouse_pos[1] - self.position[1])**2 ) < radius:
            return True
        return False

    def glide(self,seconds):
        if self.glide_time==0:
            self.glide_time=seconds   
            new_pos = (random.randint(0, width), random.randint(0, height))
            self.delta_y = (new_pos[1]-self.position[1])/seconds
            self.delta_x = (new_pos[0]-self.position[0])/seconds
        self.position =  (self.position[0]+self.delta_x, self.position[1]+self.delta_y)
        self.glide_time = self.glide_time - 1

count = 8
colors = ["red","blue","yellow"]
balloons = []
for i in range(8):
    for j in range(3):
        balloons.append(Balloon(colors[j]))

for balloon in balloons:
    balloon.set_position((random.randint(0, width), random.randint(0, height)))

while True:
    clock.tick(60)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click
                mouse_pos = pygame.mouse.get_pos()
                index = -1
                i = 0
                for balloon in balloons:
                    if balloon.get_color()=="red" and balloon.check_collision(mouse_pos):
                       index = i
                    i += 1
                if index != -1:
                    balloons.pop(index)
                    count -= 1
    if (count!=0):
        score_surface = font.render(f'Count: {count}', True, "black")
    else:
        score_surface = font.render("You Won!",True,"black")

    screen.fill('lightblue')
    for balloon in balloons:
        balloon.glide(random.randint(30,120))
        balloon.draw()
    screen.blit(score_surface,(50,50))
    pygame.display.update()
