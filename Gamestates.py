from Models import *
from Board import *
from Game import * 

class GameStateManager:
    def __init__(self, game, screen) -> None:
        self.game = game
        self.screen = screen
        self.gamestates = {"placeBL": PlaceBL(self), "mlRoll": MeleeDiceRoll(self)}
        self.selectedTile = None
        self.clickedTile = None
        self.selectedModel = None
        self.clickedModel = None
        self.runThread = True

    def run_gamestate(self, gameState):
        self.gamestates[gameState].run()

    def run_dice(self, dice):
        time.sleep(0.15)
        dice.roll_dice()
        self.screen.blit(dice.picture, (dice.x, dice.y))
        pygame.display.update()

    def run_map(self):
        for tile in game.map:
            if tile.button.draw(self.screen):
                if isinstance(tile, Wall):
                    pass
                elif tile.isOccupied:
                    self.selectedTile = tile
                    self.selectedModel = tile.occupand
                else:
                    self.clickedTile = tile
                    print(self.clickedTile)
            tile.render(self.screen)
            pygame.display.update()

class PlaceBL:
    def __init__(self, gameStateManager) -> None:
        self.gameStateManager = gameStateManager
        self.BLAmount = gameStateManager.game.reinforcement
        self.blipList = []

    def take_blips(self):
        x = 0
        while x < self.BLAmount:
            choice = random.randint(0, gameStateManager.game.blipSack.__len__() - 1)
            print(choice)
            a = gameStateManager.game.blipSack.pop(choice)
            self.blipList.append(a)
            x += 1

    def run_threat(self):
        while self.gameStateManager.runThread == True:
            gameStateManager.run_map()
        
    def run(self):
        self.take_blips()
        self.place_image = pygame.image.load('Floor_1.png')
        self.amount_image = pygame.image.load('Floor_1.png')
        self.place_button = Button(810, 500, self.place_image, 1)
        self.amount_button = Button(810, 600, self.amount_image, 1)

        self.gameStateManager.runThread = True
        thread = threading.Thread(target=self.run_threat,args=())
        thread.start()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateManager.runThread = False
                    pygame.quit()
                    sys.exit()
            if self.blipList.__len__() == 0:
                self.gameStateManager.runThread = False
                thread.join()
                self.gameStateManager.run_gamestate("placeBL")
            if self.place_button.draw(self.gameStateManager.screen):
                if isinstance(self.gameStateManager.clickedTile, EntryPoint):
                    a = self.blipList.pop(0)
                    self.gameStateManager.clickedTile.blips.append(Blip(a))
                    print(self.blipList)
                    print(gameStateManager.clickedTile.blips)
                    print(gameStateManager.clickedTile.blips[0].count)
                else:
                    #normally trow error to display for player to see
                    print("Can't Place Model there, please select valid Entrypoint!")

class MeleeDiceRoll():
    def __init__(self, gameStateManager) -> None:
        self.gameStateManager = gameStateManager
        self.dice_1 = Dice(10, 10)
        self.dice_2 = Dice(10, 110)
        self.dice_3 = Dice(10, 210)
        self.place_image = pygame.image.load('Floor_1.png')
        self.amount_image = pygame.image.load('Floor_1.png')
        self.place_button = Button(810, 500, self.place_image, 1)
        self.amount_button = Button(810, 600, self.amount_image, 1)
    
    def calculate_winner(gs_roll_1, gs_roll_2, gs_roll_3, sm_roll_1, sm_roll_2):
        pass

    def run_threat(self, dice):
        while self.gameStateManager.runThread == True:
            gameStateManager.run_dice(dice)
            
    def run(self):
        self.gameStateManager.runThread = True
        thread_1 = threading.Thread(target=self.run_threat,args=(self.dice_1,))
        thread_1.start()

        thread_2 = threading.Thread(target=self.run_threat,args=(self.dice_2,))
        thread_2.start()

        thread_3 = threading.Thread(target=self.run_threat,args=(self.dice_3,))
        thread_3.start()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if self.amount_button.draw(self.gameStateManager.screen):
                if self.gameStateManager.runThread == True:
                    self.gameStateManager.runThread = False
            
            if self.place_button.draw(self.gameStateManager.screen):
                self.gameStateManager.runThread = True
                thread = threading.Thread(target=self.run_threat,args=(self.dice_1,))
                thread.start()

pygame.init()
game = Game()
game.load_level("level1")
wall = Wall("Floor_1.png",1,1)
entry = EntryPoint("Floor_1.png",4,4)
game.map.append(entry)
game.map.append(wall)
# for tile in game.map:
#     if isinstance(tile, Tile):
#         tile.occupand = SpaceMarine("bolter", "sergant")
#         tile.isOccupied = True
game.map[0].occupand = SpaceMarine("Bolter", "sergeant")
game.map[0].isOccupied = True
screen = pygame.display.set_mode((900,900))
screen.fill("black")
gameStateManager = GameStateManager(game, screen)
gameStateManager.run_gamestate("mlRoll")

# for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     self.gameStateManager.runThread = False
#                     pygame.quit()
#                     sys.exit()
#             if self.place_button.draw(self.gameStateManager.screen):
#                 game.move_model(self.gameStateManager.selectedModel, self.gameStateManager.selectedTile, self.gameStateManager.clickedTile)
#                 self.gameStateManager.selectedTile = self.gameStateManager.clickedTile
#                 self.gameStateManager.clickedTile = None
#             if self.amount_button.draw(self.gameStateManager.screen):
#                 game.turn_model(self.gameStateManager.selectedModel, "right")