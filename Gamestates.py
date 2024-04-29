from Models import *
from Board import *
from Game import * 

class GameStateManager:
    def __init__(self, game, screen) -> None:
        self.game = game
        self.screen = screen
        self.gamestates = {"placeBL": PlaceBL(self, self.game), "mlRoll": MeleeDiceRoll(self, self.game)}
        self.runThread = True

    def run_gamestate(self, gameState):
        self.gamestates[gameState].run()

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
    def __init__(self, gameStateManager, game) -> None:
        self.game = game
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
                    if self.gameStateManager.clickedTile.blips.__len__() < 3:
                        a = self.blipList.pop(0)
                        self.gameStateManager.clickedTile.blips.append(Blip(a))
                        print(self.blipList)
                        print(gameStateManager.clickedTile.blips)
                        print(gameStateManager.clickedTile.blips[0].count)
                    else:
                        print("Too many blips outside the area!")
                else:
                    #normally trow error to display for player to see
                    print("Can't Place Model there, please select valid Entrypoint!")

class MeleeDiceRoll():
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game

    def run(self):
        sm = None
        gs = None
        facing = self.game.is_facing(self.game.selectedModel, self.game.clickedModel)

        if self.game.selectedModel in self.game.smModelList:
            sm = self.game.selectedModel
            gs = self.game.clickedModel
        else:
            gs = self.game.selectedModel
            sm = self.game.clickedModel

        self.place_image = pygame.image.load('Floor_1.png')
        self.amount_image = pygame.image.load('Floor_1.png')
        self.accept_image = pygame.image.load('Floor_1.png')
        self.place_button = Button(810, 500, self.place_image, 1)
        self.amount_button = Button(810, 600, self.amount_image, 1)
        self.accept_button = Button(410, 700, self.accept_image, 1)

        selectedDice = None
        if facing:
            parry = False
        guard = self.game.selectedModel.guard
        winner = None

        dice_1 = Dice(10,10)
        dice_2 = Dice(110, 10)
        dice_4 = Dice(410, 10)
        diceList = [dice_1, dice_2, dice_4]
        dice_3 = None
        dice_5 = None
        if self.game.isPlaying == self.game.player1:
            if sm.weapon != "Thunderhammer":
                dice_3 = Dice(210, 10)
            if sm.weapon == "Powersword":
                parry = True
            if self.game.selectedModel.weapon == "Lightningclaws":
                dice_5 = Dice(510, 10)

        elif self.game.isPlaying == self.game.player2:
            if self.game.is_facing(gs, sm):
                if sm.weapon != "Thunderhammer" or facing == False:
                    dice_3 = Dice(210, 10)
                if sm.weapon == "Powersword" and facing:
                    parry = True
                if sm.weapon == "Lightningclaws" and facing:
                    dice_5 = Dice(510, 10)

        if dice_3 != None:
            diceList.append(dice_3)
        if dice_5 != None:
            diceList.append(dice_5)

        a = True
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.gameStateManager.screen.fill("Black")
            if(a):
                dice_1.roll_dice(self.gameStateManager.screen)
                dice_2.roll_dice(self.gameStateManager.screen)
                if dice_3 != None:
                    dice_3.roll_dice(self.gameStateManager.screen)
                dice_4.roll_dice(self.gameStateManager.screen)
                if dice_5 != None:
                    dice_5.roll_dice(self.gameStateManager.screen)

                if dice_5 != None:
                    winner = self.game.melee(self.game.selectedModel, self.game.clickedModel, dice_1.face, dice_2.face, dice_3.face, dice_4.face, dice_5.face, 0)
                elif dice_3 != None:
                    winner = self.game.melee(self.game.selectedModel, self.game.clickedModel, dice_1.face, dice_2.face, dice_3.face, dice_4.face, 0, 0)
                else:
                    winner = self.game.melee(self.game.selectedModel, self.game.clickedModel, dice_1.face, dice_2.face, 0, dice_4.face, 0, 0)
                if winner in self.game.smModelList:
                    print("SM Wins!")
                elif winner == None:
                    print("Draw!")
                else:
                    print("GS Wins!")
                a = False

            for dice in diceList:
                if dice.show_result(self.gameStateManager.screen):
                    selectedDice = dice
                    print(selectedDice)

            if parry == True:
                if self.place_button.draw(self.gameStateManager.screen):
                    if selectedDice == dice_1 or selectedDice == dice_2 or selectedDice == dice_3:
                            selectedDice.roll_dice(self.gameStateManager.screen)
                            parry = False
                            winner = self.game.melee(self.game.selectedModel, self.game.clickedModel, dice_1.face, dice_2.face, dice_3.face, dice_4.face, 0, 0)
                            if winner in self.game.smModelList:
                                print("SM Wins!")
                            elif winner == None:
                                print("Draw!")
                            else:
                                print("GS Wins!")

            if guard == True:
                if self.amount_button.draw(self.gameStateManager.screen):
                    if selectedDice == dice_4 or selectedDice == dice_5:
                        selectedDice.roll_dice(self.gameStateManager.screen)
                        guard = False
                        if dice_5 != None:
                            winner = self.game.melee(self.game.selectedModel, self.game.clickedModel, dice_1.face, dice_2.face, dice_3.face, dice_4.face, dice_5.face, 0)
                        elif dice_3 != None:
                            winner = self.game.melee(self.game.selectedModel, self.game.clickedModel, dice_1.face, dice_2.face, dice_3.face, dice_4.face, 0, 0)
                        else:
                            winner = self.game.melee(self.game.selectedModel, self.game.clickedModel, dice_1.face, dice_2.face, 0, dice_4.face, 0, 0)
                        if winner in self.game.smModelList:
                            print("SM Wins!")
                        elif winner == None:
                            print("Draw!")
                        else:
                            print("GS Wins!")
            if self.accept_button.draw(self.gameStateManager.screen):
                if winner == None:
                    pass
                    #import option to turn, maby even in this menu?
                elif winner == self.game.selectedModel:
                    if facing:
                        self.game.destroy_model(self.game.selectedModel, self.game.selectedTile)       
                else: 
                    if facing:
                        self.game.destroy_model(self.game.clickedModel, self.game.clickedTile)     
                self.gameStateManager.screen.fill("black")
                self.gameStateManager.run_gamestate("placeBL")
            pygame.display.update()
            
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
game.map[0].occupand = SpaceMarine("Lightningclaws", "sergeant")
game.smModelList.append(game.map[0].occupand)
game.smModelList[0].guard = True
game.map[0].isOccupied = True
game.selectedTile = game.map[0]
game.gsModelList.append(Genestealer())
game.map[2].occupand = game.gsModelList[0]
game.map[2].isOccupied = True
screen = pygame.display.set_mode((900,900))
screen.fill("black")
gameStateManager = GameStateManager(game, screen)
game.selectedModel = game.smModelList[0]
game.clickedModel = game.gsModelList[0]
game.clickedModel.face = (-1,0)
print("Jetzt")
for tile in game.map:
            if issubclass(Tile,tile.class):
                print(tile)
# game.clickedModel.isBroodlord = True
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