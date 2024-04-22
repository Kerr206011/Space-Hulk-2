import threading
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

sm = SpaceMarine("bolter", 'sargeant')

for tile in game.map:
    if isinstance(tile, Door):
        game.turn_model(tile.occupand, "left")

currentTile = None

class SharedData:
    def __init__(self, game, screen):
        self.value = 0
        self.run = True  
        self.game = game
        self.screen = screen 

    def loop(self):
        for tile in self.game.map:
            if isinstance(tile, Tile):
                tile.interact(self.screen, self.game)
     

share = SharedData(game, screen) 

def run_in_thread(share):
    while share.run:
        share.loop()

# Create and start the thread
thread = threading.Thread(target=run_in_thread,args=(share,))
thread.start()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            share.run = False
            pygame.quit()
            sys.exit()
    # for tile in game.map:
    #     if isinstance(tile, Tile):
    #         tile.interact(screen, game)
    pygame.display.update()