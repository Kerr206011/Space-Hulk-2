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
    buttonlist.append(newButton)
    x+=51
    y+=51
class SharedData:
    def __init__(self):
        self.value = 0
        self.run = True        

    def increment(self):
        self.value += 1

share = SharedData() 

def run_in_thread(share):
    while share.run:
        for button in buttonlist:
            if(button.draw(screen)):
                share.increment()
                share.run = False

# Create and start the thread
thread = threading.Thread(target=run_in_thread,args=(share,))
thread.start()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    if share.value == 1:
        print(share.value)
        pygame.quit()
        sys.exit()
    print(1)
    pygame.display.update()