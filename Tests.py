from UI import *
import pygame

buttonlist = []
pygame.init()
#screen = pygame.display.set_mode((1080,700))
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen.fill('black')
pygame.display.set_caption('Space Hulk')
x = 0
y = 0
picture = pygame.image.load("Floor_1.png")
while x < 501:
    newButton = Button(x,y,picture,1)
    x+=51
    y+=51

while True:
    for event in pygame.event.get():
        if event.type == pygame.quit():
            pygame.QUIT