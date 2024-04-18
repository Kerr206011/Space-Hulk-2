from UI import *
import pygame
import sys
import threading

buttonlist = []
pygame.init()
#screen = pygame.display.set_mode((1080,700))
screen = pygame.display.set_mode((800, 800))
screen.fill('black')
pygame.display.set_caption('Space Hulk')
x = 0
y = 0
a = 0
picture = pygame.image.load("Floor_1.png")
while x < 501:
    newButton = Button(x,y,picture,1)
    x+=51
    y+=51
def run_in_thread():
    while True:
        for button in buttonlist:
            if(button.draw(screen)):
                a += 1

# Create and start the thread
thread = threading.Thread(target=run_in_thread)
thread.start()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    if a == 5:
        print(a)
        pygame.quit()
        sys.exit()
    buttonlist[0].draw(screen)
    print(1)
    pygame.display.update()