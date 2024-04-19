from Game import Game
from Board import *
from Models import *
from UI import *

pygame.init()
game = Game()
game.load_level("level1")
screen = pygame.display.set_mode((400,400))
screen.fill("black")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    for tile in game.map:
        tile.render(screen)
    pygame.display.update()