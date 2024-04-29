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

    def run_map_blPlace(self):
        for tile in self.game.map:
            if tile.button.draw(self.screen):
                if isinstance(tile, EntryPoint):
                    self.game.clickedTile = tile
            tile.render(self.screen)
            pygame.display.update()

    def run_map_smTurn(self):
        for tile in self.game.map:
            if tile.button.draw(self.screen):
                if isinstance(tile, Wall):
                    pass
                elif isinstance(tile, EntryPoint):
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
        self.BLAmount = self.game.reinforcement
        self.blipList = []

    def take_blips(self):
        x = 0
        while x < self.BLAmount:
            choice = random.randint(0, self.game.blipSack.__len__() - 1)
            print(choice)
            a = gameStateManager.game.blipSack.pop(choice)
            self.blipList.append(a)
            x += 1

    def run_threat(self):
        while self.gameStateManager.runThread == True:
            gameStateManager.run_map_blPlace()
        
    def run(self):
        self.take_blips()
        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.amount_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
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
                if isinstance(self.game.clickedTile, EntryPoint):
                    if self.game.clickedTile.blips.__len__() < 3:
                        a = self.blipList.pop(0)
                        self.game.clickedTile.blips.append(Blip(a))
                        print(self.blipList)
                        print(game.clickedTile.blips)
                        print(game.clickedTile.blips[0].count)
                    else:
                        print("Too many blips outside the area!")
                else:
                    #normally trow error to display for player to see
                    print("Can't Place Model there, please select valid Entrypoint!")

class PlaceSM:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game

    def run(self):
        pass

class MeleeDiceRoll():
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game
        self.dice_1 = Dice(10,10)
        self.dice_2 = Dice(110, 10)
        self.dice_3 = Dice(210, 10)
        self.dice_4 = Dice(410, 10)
        self.dice_5 = Dice(510, 10)

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

        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.amount_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.accept_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.psyup_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.psydown_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.place_button = Button(810, 500, self.place_image, 1)
        self.amount_button = Button(810, 600, self.amount_image, 1)
        self.accept_button = Button(410, 700, self.accept_image, 1)
        self.psyup_button = Button(410, 100, self.psyup_image, 1)
        self.psydown_button = Button(410, 160, self.psydown_image, 1)

        selectedDice = None
        psyPoints = 0
        
        parry = False
        guard = self.game.selectedModel.guard
        winner = None

        diceList = [self.dice_1, self.dice_2, self.dice_4]

        if self.game.isPlaying == self.game.player1:
            if sm.weapon != "Thunderhammer":
                diceList.append(self.dice_3)
            if sm.weapon == "Powersword":
                parry = True
            if self.game.selectedModel.weapon == "Lightningclaws":
                diceList.append(self.dice_5)

        elif self.game.isPlaying == self.game.player2:
            if self.game.is_facing(gs, sm):
                if sm.weapon != "Thunderhammer" or facing == False:
                    diceList.append(self.dice_3)
                if sm.weapon == "Powersword" and facing:
                    parry = True
                if sm.weapon == "Lightningclaws" and facing:
                    diceList.append(self.dice_5)

        a = True
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.gameStateManager.screen.fill("Black")
            if a:
                for dice in diceList:
                    dice.roll_dice(self.gameStateManager.screen)

                    if self.dice_5 in diceList:
                        winner = self.game.melee(self.game.selectedModel, self.game.clickedModel, self.dice_1.face, self.dice_2.face, self.dice_3.face, self.dice_4.face, self.dice_5.face, psyPoints)
                    elif self.dice_3 in diceList:
                        winner = self.game.melee(self.game.selectedModel, self.game.clickedModel, self.dice_1.face, self.dice_2.face, self.dice_3.face, self.dice_4.face, 0, psyPoints)
                    else:
                        winner = self.game.melee(self.game.selectedModel, self.game.clickedModel, self.dice_1.face, self.dice_2.face, 0, self.dice_4.face, 0, psyPoints)

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
                    if selectedDice == self.dice_1 or selectedDice == self.dice_2 or selectedDice == self.dice_3:
                            selectedDice.roll_dice(self.gameStateManager.screen)
                            parry = False
                            winner = self.game.melee(self.game.selectedModel, self.game.clickedModel, self.dice_1.face, self.dice_2.face, self.dice_3.face, self.dice_4.face, 0, 0)

                            if winner in self.game.smModelList:
                                print("SM Wins!")
                            elif winner == None:
                                print("Draw!")
                            else:
                                print("GS Wins!")

            if guard == True:
                if self.amount_button.draw(self.gameStateManager.screen):
                    if selectedDice == self.dice_4 or selectedDice == self.dice_5:
                        selectedDice.roll_dice(self.gameStateManager.screen)
                        guard = False
                        if self.dice_5 in diceList:
                            winner = self.game.melee(self.game.selectedModel, self.game.clickedModel, self.dice_1.face, self.dice_2.face, self.dice_3.face, self.dice_4.face, self.dice_5.face, psyPoints)
                        elif self.dice_3 in diceList:
                            winner = self.game.melee(self.game.selectedModel, self.game.clickedModel, self.dice_1.face, self.dice_2.face, self.dice_3.face, self.dice_4.face, 0, psyPoints)
                        else:
                            winner = self.game.melee(self.game.selectedModel, self.game.clickedModel, self.dice_1.face, self.dice_2.face, 0, self.dice_4.face, 0, psyPoints)
                        
                        if winner in self.game.smModelList:
                            print("SM Wins!")
                        elif winner == None:
                            print("Draw!")
                        else:
                            print("GS Wins!")

            if sm.weapon == "Axe":
                if self.psyup_button.draw(self.gameStateManager.screen):
                    if psyPoints <= self.game.psyPoints:
                        psyPoints += 1
                        winner = self.game.melee(self.game.selectedModel, self.game.clickedModel, self.dice_1.face, self.dice_2.face, self.dice_3.face, self.dice_4.face, 0, psyPoints)
                        
                        if winner in self.game.smModelList:
                            print("SM Wins!")
                        elif winner == None:
                            print("Draw!")
                        else:
                            print("GS Wins!")

                if self.psydown_button.draw(self.gameStateManager.screen):
                    if psyPoints > 0:
                        psyPoints -= 1
                        winner = self.game.melee(self.game.selectedModel, self.game.clickedModel, self.dice_1.face, self.dice_2.face, self.dice_3.face, self.dice_4.face, 0, psyPoints)
                        
                        if winner in self.game.smModelList:
                            print("SM Wins!")
                        elif winner == None:
                            print("Draw!")
                        else:
                            print("GS Wins!")

            if self.accept_button.draw(self.gameStateManager.screen):
                self.game.psyPoints -= psyPoints
                print(self.game.psyPoints)
                if winner == None:
                    pass
                    #import option to turn, maby even in this menu?
                elif winner == self.game.selectedModel:
                    if facing:
                        self.game.destroy_model(self.game.clickedModel, self.game.clickedTile)       
                else: 
                    if facing:
                        self.game.destroy_model(self.game.selectedModel, self.game.selectedTile)  

                print(game.selectedModel)
                print(game.clickedModel)   
                self.gameStateManager.screen.fill("black")
                self.gameStateManager.run_gamestate("placeBL")
            pygame.display.update()
            
pygame.init()
game = Game()
game.load_level("level_1")
# wall = Wall("Pictures/Tiles/Floor_1.png",1,1)
# entry = EntryPoint("Pictures/Tiles/Floor_1.png",4,4)
# game.map.append(entry)
# game.map.append(wall)

game.map[0].occupand = SpaceMarine("Axe", "sergeant")
game.smModelList.append(game.map[0].occupand)
game.smModelList[0].guard = True
game.map[0].isOccupied = True
game.selectedTile = game.map[0]
game.gsModelList.append(Genestealer())
game.map[2].occupand = game.gsModelList[0]
game.map[2].isOccupied = True
game.clickedTile = game.map[2]
screen = pygame.display.set_mode((900,900))
screen.fill("black")
gameStateManager = GameStateManager(game, screen)
game.selectedModel = game.smModelList[0]
game.clickedModel = game.gsModelList[0]
game.clickedModel.face = (-1,0)
# game.clickedModel.isBroodlord = True
gameStateManager.run_gamestate("placeBL")

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