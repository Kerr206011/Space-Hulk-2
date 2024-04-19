from Game import Game
from Board import *
from Models import *
from UI import *

pygame.init()
game = Game()
game.load_level("level1")
wall = Wall("Floor_1.png",1,1)
game.map.append(wall)
for tile in game.map:
    if isinstance(tile, Tile):
        tile.occupand = SpaceMarine("bolter", "sergant")
        tile.isOccupied = True
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