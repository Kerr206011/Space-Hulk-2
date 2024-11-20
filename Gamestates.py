from Models import *
from Board import *
from Game import *
import pygame.docs 

class GameStateManager:     #class to manage interactions between gamestates and provide a schared game object and storage
    def __init__(self, game, screen) -> None:
        self.game = game
        self.screen = screen
        self.gamestates = {"smTurn": smTurn(self, self.game), 
                           "smAction": smAction(self, self.game), 
                           "gsAction": gsAction(self, self.game),
                           "blAction": blAction(self, self.game),
                           "gsTurn": gsTurn(self, self.game),
                           "reveal": revealGS(self, self.game),
                           "gsTruning": gsTurning(self, self.game),
                           "command": commandPhase(self, self.game), 
                           "smTurning": smTurning(self, self.game), 
                           "main":gamestateMain(self, self.game),
                           "gsStart": BLstart(self, self.game),
                           "blSelect": ChooseBlip(self, self.game), 
                           "gsPlace": PlaceBL(self, self.game), 
                           "mlRoll": MeleeDiceRoll(self, self.game), 
                           "mlRollDoorSM": MeleeDiceRollDoorSM(self, self.game),
                           "smPlace": PlaceSM(self, self.game)}
        self.runThread = True

        self.freeShot = False   #if sm has free shoot Action
        self.freeTurn = False   #if gs has a free turn

    def run_gamestate(self, gameState):     #method for executing the run methods of the individual gamestates
        self.gamestates[gameState].run()

    def refresh(self):
        for tile in self.game.map:
            tile.render(self.screen)
        pygame.display.flip()

    def run_map_command(self):      #method for showing the map in the commandphase
        for tile in self.game.map:
            tile.render(self.screen)

    def run_map_blPlace(self):      #method for showing the map in the reinforcement phase
        for tile in self.game.map:
            if tile.button.draw(self.screen):
                if isinstance(tile, EntryPoint):
                    self.game.clickedTile = tile
            tile.render(self.screen)
        pygame.display.update()

    def run_map_turning(self):
        for tile in self.game.map:
            tile.render(self.screen)
        pygame.display.update()

    def run_map_smActivation(self):
        for tile in self.game.map:
            if tile.button.draw(self.screen):
                if isinstance(tile, Wall):
                    pass
                elif isinstance(tile, EntryPoint):
                    pass
                elif tile.isOccupied:
                    if isinstance(tile.occupand, SpaceMarine):
                        pass
                    else:
                        self.game.clickedTile = tile
                        self.game.clickedModel = tile.occupand
                else:
                    self.clickedTile = tile
                    print(self.clickedTile)
            tile.render(self.screen)
        pygame.display.update()

    def run_map_smTurn(self):       #method for running the map during the Space Marine turn
        for tile in self.game.map:
            if tile.button.draw(self.screen):
                if isinstance(tile, Wall):
                    pass
                elif isinstance(tile, EntryPoint):
                    pass
                elif tile.isOccupied:
                    if isinstance(tile.occupand, SpaceMarine):
                        self.game.selectedTile = tile
                        self.game.selectedModel = tile.occupand
                    else:
                        self.game.clickedTile = tile
                        self.game.clickedModel = tile.occupand
                else:
                    self.clickedTile = tile
                    print(self.clickedTile)
            tile.render(self.screen)
        pygame.display.update()

class BLstart:
    def __init__(self, gameStateManager, game) -> None:
        self.game = game
        self.gameStateManager = gameStateManager
        self.BLAmount = int
        self.blipList = []
        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.amount_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.place_button = Button(810, 500, self.place_image, 1)
        self.amount_button = Button(810, 600, self.amount_image, 1)

    def take_blips(self):
        x = 0
        while x < self.BLAmount:
            choice = random.randint(0, self.game.blipSack.__len__() - 1)
            print(choice)
            a = self.gameStateManager.game.blipSack.pop(choice)
            self.blipList.append(a)
            x += 1

    def place_blip(self):
        if isinstance(self.game.clickedTile, EntryPoint):
            if self.game.clickedTile.blips.__len__() < 3:
                a = self.blipList.pop(0)
                blip = Blip(a)
                self.game.clickedTile.blips.append(blip)
                self.game.blModelList.append(blip)
                print(self.blipList)
                print(game.clickedTile.blips)
                print(game.clickedTile.blips[0].count)
            else:
                print("Too many blips outside the area!")
        else:
            #normally trow error to display for player to see
            print("Can't Place Model there, please select valid Entrypoint!")

    def endState(self):
        self.game.reset_select()
        self.game.reset_clicked()
        self.gameStateManager.screen.fill("black")
        self.gameStateManager.run_gamestate("command")
        
    def run(self):
        self.BLAmount = self.game.startBlip
        self.take_blips()

        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)
        
        self.place_button.draw(self.gameStateManager.screen)
        self.amount_button.draw(self.gameStateManager.screen)

        pygame.display.flip()

        print('BL Start')

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for tile in self.game.map:
                            tile.scroll((0, -1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_w:
                        for tile in self.game.map:
                            tile.scroll((0, 1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_a:
                        for tile in self.game.map:
                            tile.scroll((1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    if event.key == pygame.K_d:
                        for tile in self.game.map:
                            tile.scroll((-1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    self.gameStateManager.screen.fill("black")

                    for tile in self.game.map:
                        tile.render(self.gameStateManager.screen)

                    self.place_button.draw(self.gameStateManager.screen)
                    self.amount_button.draw(self.gameStateManager.screen)

                    pygame.display.flip()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.place_button.rect.collidepoint(pygame.mouse.get_pos()):
                        self.place_blip()
                        if self.blipList.__len__() == 0:
                            self.endState()
                    else:
                        for tile in self.game.map:
                            if isinstance(tile, EntryPoint):
                                if tile.button.rect.collidepoint(pygame.mouse.get_pos()):
                                    self.game.clickedTile = tile  
                                    print(tile.blips)  
                                    print("It works!")


class PlaceBL:     #Gamestate where the Blips are Placed(reinforcement phase)
    def __init__(self, gameStateManager, game) -> None:
        self.game = game
        self.gameStateManager = gameStateManager
        self.BLAmount = int
        self.blipList = []
        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.amount_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.place_button = Button(810, 500, self.place_image, 1)
        self.amount_button = Button(810, 600, self.amount_image, 1)

    def take_blips(self):
        x = 0
        while x < self.BLAmount:
            choice = random.randint(0, self.game.blipSack.__len__() - 1)
            print(choice)
            a = self.gameStateManager.game.blipSack.pop(choice)
            self.blipList.append(a)
            x += 1

    def place_blip(self):
        if isinstance(self.game.clickedTile, EntryPoint):
            if self.game.clickedTile.blips.__len__() < 3:
                a = self.blipList.pop(0)
                blip = Blip(a)
                self.game.clickedTile.blips.append(blip)
                self.game.blModelList.append(blip)
                print(self.blipList)
                print(game.clickedTile.blips)
                print(game.clickedTile.blips[0].count)
            else:
                print("Too many blips outside the area!")
        else:
            #normally trow error to display for player to see
            print("Can't Place Model there, please select valid Entrypoint!")

    def endState(self):
        for model in self.game.gsModelList:
            model.AP = 6
        for model in self.game.blModelList:
            model.AP = 6
            #set AP = 0 and lurking true if sm in proximity
        self.game.reset_select()
        self.game.reset_clicked()
        self.gameStateManager.screen.fill("black")
        self.gameStateManager.run_gamestate('gsTurn')  ### rewrite to GS turn

    def run(self):
        self.BLAmount = self.game.reinforcement
        #need to implement refilling of the game.blipsack
        self.take_blips()

        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)
        
        self.place_button.draw(self.gameStateManager.screen)
        self.amount_button.draw(self.gameStateManager.screen)

        pygame.display.flip()

        print('Place BL')

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for tile in self.game.map:
                            tile.scroll((0, -1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_w:
                        for tile in self.game.map:
                            tile.scroll((0, 1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_a:
                        for tile in self.game.map:
                            tile.scroll((1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    if event.key == pygame.K_d:
                        for tile in self.game.map:
                            tile.scroll((-1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    self.gameStateManager.screen.fill("black")

                    for tile in self.game.map:
                        tile.render(self.gameStateManager.screen)

                    self.place_button.draw(self.gameStateManager.screen)
                    self.amount_button.draw(self.gameStateManager.screen)

                    pygame.display.flip()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.place_button.rect.collidepoint(pygame.mouse.get_pos()):
                        self.place_blip()
                        if self.blipList.__len__() == 0:
                            self.endState()
                    else:
                        for tile in self.game.map:
                            if isinstance(tile, EntryPoint):
                                if tile.button.rect.collidepoint(pygame.mouse.get_pos()):
                                    self.game.clickedTile = tile  
                                    print(tile.blips)  
                                    print("It works!")


class PlaceSM:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game
        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.amount_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.place_button = Button(810, 500, self.place_image, 1)
        self.right_button = Button(810, 600, self.amount_image, 1)
        self.left_button = Button(810, 700, self.amount_image, 1)
        self.accept_button = Button(810, 800, self.amount_image, 1)

    def placeModel(self):
        if isinstance(self.game.selectedTile, ControlledArea):
            if self.game.selectedTile.isOccupied == False:
                a = self.smList.pop(0)
                self.game.selectedTile.occupand = a
                self.game.selectedTile.isOccupied = True
                self.game.selectedModel = a
                self.game.selectedTile.render(self.gameStateManager.screen)
                pygame.display.update(self.game.selectedTile.button.rect)
            else:
                print("Chose an unoccupied Tile!")
        else:
            print("Can't Place Model there, please select valid Entrypoint!")
        
        if self.smList.__len__() == 0:
            self.gameStateManager.screen.fill('black')
            self.accept_button.draw(self.gameStateManager.screen)
            for tile in self.game.map:
                tile.render(self.gameStateManager.screen)
            self.right_button.draw(self.gameStateManager.screen)
            self.left_button.draw(self.gameStateManager.screen)
            pygame.display.flip()

    def endState(self):
        for tile in self.game.map:
            if isinstance(tile, ControlledArea):
                self.game.map.append(tile.convert_to_tile())
                self.game.map.remove(tile)
        self.game.reset_select()
        self.game.reset_clicked()
        self.gameStateManager.screen.fill("black")
        self.gameStateManager.run_gamestate('gsStart')

    def run(self):
        self.smList = self.game.smModelList.copy()

        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)

        self.place_button.draw(self.gameStateManager.screen)
        self.right_button.draw(self.gameStateManager.screen)
        self.left_button.draw(self.gameStateManager.screen)

        pygame.display.flip()

        print('Place SM')

        while True:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for tile in self.game.map:
                            tile.scroll((0, -1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_w:
                        for tile in self.game.map:
                            tile.scroll((0, 1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_a:
                        for tile in self.game.map:
                            tile.scroll((1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    if event.key == pygame.K_d:
                        for tile in self.game.map:
                            tile.scroll((-1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    self.gameStateManager.screen.fill("black")

                    for tile in self.game.map:
                        tile.render(self.gameStateManager.screen)

                    self.right_button.draw(self.gameStateManager.screen)
                    self.left_button.draw(self.gameStateManager.screen)
                    
                    if self.smList.__len__() > 0:   
                        self.place_button.draw(self.gameStateManager.screen)
                    else:
                        self.accept_button.draw(self.gameStateManager.screen)
                    pygame.display.flip()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    action = True

                    if self.smList.__len__() > 0:   
                        if self.place_button.rect.collidepoint(pygame.mouse.get_pos()):
                            action = False
                            self.placeModel()

                    else:
                        if self.accept_button.rect.collidepoint(pygame.mouse.get_pos()):
                            action = False
                            self.endState()

                    if self.game.selectedModel != None:
                        if self.right_button.rect.collidepoint(pygame.mouse.get_pos()):
                            action = False
                            self.game.turn_model( self.game.selectedModel, "left")
                            pygame.draw.rect(self.gameStateManager.screen, (0,0,0), self.game.selectedTile.button.rect)
                            self.game.selectedTile.render(self.gameStateManager.screen)
                            pygame.display.update(self.game.selectedTile.button.rect)
                        
                        if self.left_button.rect.collidepoint(pygame.mouse.get_pos()):
                            action = False
                            self.game.turn_model( self.game.selectedModel, "right")
                            pygame.draw.rect(self.gameStateManager.screen, (0,0,0), self.game.selectedTile.button.rect)
                            self.game.selectedTile.render(self.gameStateManager.screen)
                            pygame.display.update(self.game.selectedTile.button.rect)
                    if action:
                        for tile in self.game.map:
                            if isinstance(tile, Tile):
                                if tile.button.rect.collidepoint(pygame.mouse.get_pos()):
                                    self.game.selectedTile = tile  
                                    if tile.isOccupied:
                                        self.game.selectedModel = tile.occupand
                                    print(tile.occupand)   
                                    print("It works!")


class commandPhase:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game
        self.dice = Dice(800, 100)
        self.roll = int
        self.reroll_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.accept_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.reroll_button = Button(810, 500, self.reroll_image, 1)
        self.accept_button = Button(810, 600, self.accept_image, 1)

    def endState(self):
        self.gameStateManager.screen.fill("black")
        self.gameStateManager.run_gamestate('smTurn')

    def run(self):

        for tile in self.game.map:
            if isinstance(tile, Tile):
                if tile.isBurning:
                    tile.isBurning = False
                    tile.change_picture(tile.picturePath)
            tile.render(self.gameStateManager.screen)

        self.accept_button.draw(self.gameStateManager.screen)
        self.reroll_button.draw(self.gameStateManager.screen)

        pygame.display.flip()

        print('command')

        reroll = False
        for model in self.game.smModelList:
            model.AP = 4
            model.overwatch = False
            model.guard = False

            if model.rank == "sergant":
                reroll = True
                print("sergant")
                
        self.gameStateManager.freeShot = False

        self.dice.roll_dice(self.gameStateManager.screen)
        self.roll = self.dice.face

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for tile in self.game.map:
                            tile.scroll((0, -1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_w:
                        for tile in self.game.map:
                            tile.scroll((0, 1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_a:
                        for tile in self.game.map:
                            tile.scroll((1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    if event.key == pygame.K_d:
                        for tile in self.game.map:
                            tile.scroll((-1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    self.gameStateManager.screen.fill("black")

                    for tile in self.game.map:
                        tile.render(self.gameStateManager.screen)

                    self.reroll_button.draw(self.gameStateManager.screen)
                    self.accept_button.draw(self.gameStateManager.screen)

                    self.dice.show_result(self.gameStateManager.screen)
                    
                    pygame.display.flip()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if reroll == True:
                        if self.reroll_button.rect.collidepoint(pygame.mouse.get_pos()):    #remove Button after reroll
                            self.dice.roll_dice(self.gameStateManager.screen)
                            self.roll = self.dice.face
                            reroll = False

                    if self.accept_button.rect.collidepoint(pygame.mouse.get_pos()):
                        self.game.cp = self.roll
                        self.endState()


class smAction:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game
        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.amount_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.move_button = Button(810, 500, self.place_image, 1)
        self.turn_button = Button(810, 600, self.amount_image, 1)
        self.shoot_button = Button(810, 700, self.amount_image, 1)
        self.interact_button = Button(810, 400, self.amount_image, 1)
        self.melee_button = Button(810, 300, self.amount_image, 1)
        self.overwatch_button = Button(810, 200, self.amount_image, 1)
        self.guard_button = Button(810, 100, self.amount_image, 1)
        self.accept_button = Button(810, 800, self.amount_image, 1)

    def check_move(self):
        direction = False
        burning = False
        doorOpen = False
        occupied = False
        if isinstance(self.game.clickedTile, Tile):
            if (((self.game.clickedTile.x == self.game.selectedTile.x + self.game.selectedModel.face[0]) or (self.game.clickedTile.x == self.game.selectedTile.x - self.game.selectedModel.face[0])) and self.game.selectedModel.face[0] != 0) or (((self.game.clickedTile.y == self.game.selectedTile.y + self.game.selectedModel.face[1]) or (self.game.clickedTile.y == self.game.selectedTile.y - self.game.selectedModel.face[1])) and self.game.selectedModel.face[1] != 0):
                direction = True
            if (self.game.clickedTile.isBurning == False) or (self.game.selectedTile.isBurning == True):
                burning = True
            if (self.game.clickedTile.isOccupied == False) or (isinstance(self.game.clickedTile.occupand, Item)):
                occupied = True
            if isinstance(self.game.clickedTile, Door):
                if self.game.clickedTile.isOpen:
                    doorOpen = True
            else:
                doorOpen = True


        if direction and burning and doorOpen and occupied:
            return True
        else:
            return False 
        
    def check_melee(self):
        if (self.game.selectedTile.x + self.game.selectedModel.face[0] == self.game.clickedTile.x) and (self.game.selectedTile.y + self.game.selectedModel.face[1] == self.game.clickedTile.y):
            if self.game.clickedModel != None:
                return True
            elif(isinstance(self.game.clickedTile, Door)):
                if self.game.clickedTile.isOpen == False:
                    return True
            else: 
                return False
            
    def check_door(self):
        face = self.game.selectedModel.face
        if isinstance(self.game.clickedTile, Door):
            if ((self.game.selectedTile.x + face[0] == self.game.clickedTile.x) and (face[0] != 0)) or ((self.game.selectedTile.y + face[1] == self.game.clickedTile.y) and (face[1] != 0)):
                print("Door")
                return True
        else:
            return False
        
    def calculate_movement_cost(self):
        if ((self.game.clickedTile.x == self.game.selectedTile.x + self.game.selectedModel.face[0]) and (self.game.selectedModel.face[0] != 0)) or ((self.game.clickedTile.y == self.game.selectedTile.y + self.game.selectedModel.face[1]) and (self.game.selectedModel.face[1] != 0)):
            return 1
        else:
            return 2
        
    def reduce_ap(self, amount):
        if self.game.selectedModel.AP >= amount:
            self.game.selectedModel.AP -= amount
        else:
            self.game.selectedModel.AP = 0
            self.game.cp -= (amount - self.game.selectedModel.AP)

    def move_model(self):
        self.game.clickedTile.occupand = self.game.selectedModel
        self.game.selectedTile.isOccupied = False
        self.game.selectedTile.occupand = None
        self.game.clickedTile.isOccupied = True
        pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.selectedTile.button.rect)
        pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.clickedTile.button.rect)
        self.game.selectedTile.render(self.gameStateManager.screen)
        self.game.clickedTile.render(self.gameStateManager.screen)
        pygame.display.update(self.game.clickedTile.button.rect)
        pygame.display.update(self.game.selectedTile.button.rect)
        self.game.selectedTile = self.game.clickedTile
        self.game.reset_clicked()
            
    def run(self):

        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)

        self.move_button.draw(self.gameStateManager.screen)
        self.turn_button.draw(self.gameStateManager.screen)
        # self.guard_button.draw(self.gameStateManager.screen)
        if self.game.clickedTile != None:
            if self.check_melee():
                self.melee_button.draw(self.gameStateManager.screen)
        # self.shoot_button.draw(self.gameStateManager.screen)
        self.accept_button.draw(self.gameStateManager.screen)
        if self.check_door():
            self.interact_button.draw(self.gameStateManager.screen)
        # self.overwatch_button.draw(self.gameStateManager.screen)

        pygame.display.flip()

        print('SM Action')

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateManager.runThread = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for tile in self.game.map:
                            tile.scroll((0, -1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_w:
                        for tile in self.game.map:
                            tile.scroll((0, 1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_a:
                        for tile in self.game.map:
                            tile.scroll((1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    if event.key == pygame.K_d:
                        for tile in self.game.map:
                            tile.scroll((-1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    self.gameStateManager.screen.fill("black")

                    for tile in self.game.map:
                        tile.render(self.gameStateManager.screen)

                    self.move_button.draw(self.gameStateManager.screen)
                    self.turn_button.draw(self.gameStateManager.screen)
                    # self.guard_button.draw(self.gameStateManager.screen)
                    if self.game.clickedTile != None:
                        if self.check_melee():
                            self.melee_button.draw(self.gameStateManager.screen)
                    # self.shoot_button.draw(self.gameStateManager.screen)
                    self.accept_button.draw(self.gameStateManager.screen)
                    if self.check_door():
                        self.interact_button.draw(self.gameStateManager.screen)
                    # self.overwatch_button.draw(self.gameStateManager.screen)
                    
                    pygame.display.flip()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.move_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.check_move():
                            if self.calculate_movement_cost() <= (self.game.selectedModel.AP + self.game.cp):
                                self.reduce_ap(self.calculate_movement_cost())
                                self.move_model()       #add walking through flame
                                self.gameStateManager.freeShoot = True
                            print(self.game.check_full_vision())
                    
                    elif self.interact_button.rect.collidepoint(pygame.mouse.get_pos()):        #only render when door in proximity
                        if self.check_door():
                            if self.game.selectedModel.AP + self.game.cp != 0:
                                self.game.interact_door(self.game.clickedTile)
                                self.reduce_ap(1)
                                pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.clickedTile.button.rect)
                                self.game.clickedTile.render(self.gameStateManager.screen)
                                pygame.display.update(self.game.clickedTile.button.rect)
                                if not self.check_melee():
                                    pygame.draw.rect(self.gameStateManager.screen, 'black', self.melee_button.rect)
                                    pygame.display.update(self.melee_button.rect)

                    elif self.turn_button.rect.collidepoint(pygame.mouse.get_pos()):
                        self.gameStateManager.screen.fill('black')
                        self.gameStateManager.run_gamestate("smTurning")

                    elif self.accept_button.rect.collidepoint(pygame.mouse.get_pos()):
                        self.game.selectedModel.AP = 0
                        self.game.reset_select()
                        self.game.reset_clicked()
                        self.gameStateManager.screen.fill("black")
                        self.gameStateManager.run_gamestate("smTurn")

                    elif self.melee_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.game.selectedModel.AP + self.game.cp != 0:
                            if self.game.clickedTile != None:
                                if self.check_melee():
                                    if self.game.clickedTile.isOccupied == False:
                                        self.gameStateManager.screen.fill("Black")  #replace with semi Transparent blit
                                        self.gameStateManager.run_gamestate("mlRollDoorSM")

                    else:
                        for tile in self.game.map:
                            if isinstance(tile, Tile):
                                if tile.button.rect.collidepoint(pygame.mouse.get_pos()):
                                    if tile != self.game.selectedTile:
                                        self.game.clickedTile = tile
                                        if (self.game.selectedTile.x + self.game.selectedModel.face[0] == tile.x) and (self.game.selectedTile.y + self.game.selectedModel.face[1] == tile.y):
                                            if isinstance(tile, Door):
                                                if tile.isOpen == False:
                                                    pygame.draw.rect(self.gameStateManager.screen, 'black', self.melee_button.rect)
                                                    self.melee_button.draw(self.gameStateManager.screen)
                                                    pygame.display.update(self.melee_button.rect)
                                        print(tile)
                                        if tile.isOccupied:
                                            if isinstance(tile.occupand, Genestealer):
                                                self.game.clickedModel = tile.occupand
                                                if self.check_melee():
                                                    pygame.draw.rect(self.gameStateManager.screen, 'black', self.melee_button.rect)
                                                    self.melee_button.draw(self.gameStateManager.screen)
                                                    pygame.display.update(self.melee_button.rect)


            # if self.check_melee():
            #     if self.melee_button.draw(self.gameStateManager.screen):
            #         for tile in self.game.map:
            #             if tile.x == self.game.selectedTile.x + self.game.selectedModel.face[0] and tile.y == self.game.selectedTile.y + self.game.selectedModel.face[1]:
            #                 self.game.clickedTile = tile
            #                 self.game.clickedModel = tile.occupand
            #                 if tile.isOccupied:
            #                     self.gameStateManager.run_gamestate("mlRoll")
            #                 else:
            #                     self.gameStateManager.run_gamestate("mlRollDoorSM")
          

class smTurn:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game
        self.activate_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.end_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.activate_button = Button(810, 500, self.activate_image, 1)
        self.end_button = Button(810, 600, self.end_image, 1)

    def endState(self):
        self.game.reset_select()
        self.game.reset_clicked()
        self.gameStateManager.screen.fill("black")
        self.gameStateManager.run_gamestate('gsPlace')

    def run(self):

        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)

        self.activate_button.draw(self.gameStateManager.screen)
        self.end_button.draw(self.gameStateManager.screen)

        pygame.display.flip()

        print('SM Turn')

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for tile in self.game.map:
                            tile.scroll((0, -1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_w:
                        for tile in self.game.map:
                            tile.scroll((0, 1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_a:
                        for tile in self.game.map:
                            tile.scroll((1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    if event.key == pygame.K_d:
                        for tile in self.game.map:
                            tile.scroll((-1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    self.gameStateManager.screen.fill("black")

                    for tile in self.game.map:
                        tile.render(self.gameStateManager.screen)

                    self.activate_button.draw(self.gameStateManager.screen)
                    self.end_button.draw(self.gameStateManager.screen)
                    
                    pygame.display.flip()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.activate_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.game.selectedModel != None:
                            self.gameStateManager.screen.fill('black')
                            self.gameStateManager.run_gamestate("smAction")
                        else:
                            print("Please select a Model!")

                    elif self.end_button.rect.collidepoint(pygame.mouse.get_pos()):
                        self.endState()

                    else:
                        for tile in self.game.map:
                            if isinstance(tile, Tile):
                                if tile.button.rect.collidepoint(pygame.mouse.get_pos()):
                                    if tile.isOccupied:
                                        if tile.occupand in self.game.smModelList:
                                            self.game.selectedTile = tile
                                            self.game.selectedModel = tile.occupand
                                            print("It works!")


class smTurning:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game
        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.amount_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.right_button = Button(810, 500, self.place_image, 1)
        self.left_button = Button(810, 600, self.amount_image, 1)
        self.accept_button = Button(810, 700, self.amount_image, 1)

    def reduce_ap(self, amount):
        if self.game.selectedModel.AP >= amount:
            self.game.selectedModel.AP -= amount
        else:
            self.game.selectedModel.AP = 0
            self.game.cp -= (amount - self.game.selectedModel.AP)

    def run(self):
        turnAmount = 0

        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)
        
        self.right_button.draw(self.gameStateManager.screen)
        self.left_button.draw(self.gameStateManager.screen)
        self.accept_button.draw(self.gameStateManager.screen)
        pygame.display.flip()

        print('SM Turning')

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateManager.runThread = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for tile in self.game.map:
                            tile.scroll((0, -1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_w:
                        for tile in self.game.map:
                            tile.scroll((0, 1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_a:
                        for tile in self.game.map:
                            tile.scroll((1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    if event.key == pygame.K_d:
                        for tile in self.game.map:
                            tile.scroll((-1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    self.gameStateManager.screen.fill("black")

                    for tile in self.game.map:
                        tile.render(self.gameStateManager.screen)

                    self.left_button.draw(self.gameStateManager.screen)
                    self.right_button.draw(self.gameStateManager.screen)
                    self.accept_button.draw(self.gameStateManager.screen)
                    
                    pygame.display.flip()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.left_button.rect.collidepoint(pygame.mouse.get_pos()):
                        turnAmount += 1
                        self.game.turn_model(self.game.selectedModel, "left")
                        pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.selectedTile.button.rect)
                        self.game.selectedTile.render(self.gameStateManager.screen)
                        pygame.display.update(self.game.selectedTile.button.rect)

                    elif self.right_button.rect.collidepoint(pygame.mouse.get_pos()):
                        turnAmount -= 1
                        self.game.turn_model(self.game.selectedModel, "right")
                        pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.selectedTile.button.rect)
                        self.game.selectedTile.render(self.gameStateManager.screen)
                        pygame.display.update(self.game.selectedTile.button.rect)

                    elif self.accept_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if turnAmount == 0:
                            pass

                        elif turnAmount < 0:
                            cost = abs(turnAmount) % 4
                            match cost:
                                case 0:
                                    pass

                                case 1:
                                    if self.game.cp + self.game.selectedModel.AP > 0:
                                        self.reduce_ap(1)
                                        self.gameStateManager.freeShot = True
                                    else:
                                        print("Not enough AP/CP!")
                                        self.game.turn_model(self.game.selectedModel, "left")

                                case 2:
                                    if self.game.cp + self.game.selectedModel.AP > 1:
                                        self.reduce_ap(2)
                                        self.gameStateManager.freeShot = True
                                    else:
                                        print("Not enough AP/CP!")
                                        self.game.turn_model(self.game.selectedModel, "full")

                                case 3:
                                    if self.game.cp + self.game.selectedModel.AP > 0:
                                        self.reduce_ap(1)
                                        self.gameStateManager.freeShot = True
                                    else:
                                        print("Not enough AP/CP!")
                                        self.game.turn_model(self.game.selectedModel, "right")

                        elif turnAmount > 0:
                            cost = abs(turnAmount) % 4
                            match cost:
                                case 0:
                                    pass

                                case 1:
                                    if self.game.cp + self.game.selectedModel.AP > 0:
                                        self.reduce_ap(1)
                                        self.gameStateManager.freeShot = True
                                    else:
                                        print("Not enough AP/CP!")
                                        self.game.turn_model(self.game.selectedModel, "right")
                                        

                                case 2:
                                    if self.game.cp + self.game.selectedModel.AP > 1:
                                        self.reduce_ap(2)
                                        self.gameStateManager.freeShot = True
                                    else:
                                        print("Not enough AP/CP!")
                                        self.game.turn_model(self.game.selectedModel, "full")

                                case 3:
                                    if self.game.cp + self.game.selectedModel.AP > 0:
                                        self.reduce_ap(1)
                                        self.gameStateManager.freeShot = True
                                    else:
                                        print("Not enough AP/CP!")
                                        self.game.turn_model(self.game.selectedModel, "left")

                        self.gameStateManager.screen.fill("black")
                        print(self.game.selectedModel.AP)
                        print(self.game.cp)
                        self.gameStateManager.run_gamestate("smAction")


class MeleeDiceRollDoorSM:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game
        self.dice_1 = Dice(10,10)
        self.dice_2 = Dice(110, 10)
        self.rollAgain_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.accept_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.psyup_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.psydown_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.rollAgain_button = Button(410, 500, self.rollAgain_image, 1)
        self.accept_button = Button(410, 700, self.accept_image, 1)
        self.psyup_button = Button(410, 100, self.psyup_image, 1)
        self.psydown_button = Button(410, 160, self.psydown_image, 1)

    def melee_door(self, roll_1, roll_2, psycic):
        attacker = self.game.selectedModel

        if attacker.weapon == "Thunderhammer":
            roll_1 += 2
        if attacker.weapon == "Powersword":
            roll_1 += 1
        if attacker.weapon == "Chainfist":
            roll_1 = 6
        if attacker.weapon == "Lightningclaws":
            if roll_1 > roll_2:
                roll_1 +=1
            else:
                roll_2 +=1
        if attacker.weapon == "Axe":
            roll_1 +=1
            roll_1 += psycic

        if roll_1 > 5 or roll_2 > 5:
            return True
        
    def reduce_ap(self, amount):
        if self.game.selectedModel.AP >= amount:
            self.game.selectedModel.AP -= amount
        else:
            self.game.selectedModel.AP = 0
            self.game.cp -= (amount - self.game.selectedModel.AP)
    
    def run(self):
        roll_1 = 0
        roll_2 = 0

        psyPoints = 0

        diceList = []

        if self.game.selectedModel.weapon == "Lightningclaws":
            diceList.append(self.dice_1)
            diceList.append(self.dice_2)
        else:
            diceList.append(self.dice_1)

        if self.game.selectedModel.weapon == "Axe":
            self.psyup_button.draw(self.gameStateManager.screen)
            self.psydown_button.draw(self.gameStateManager.screen)
        self.accept_button.draw(self.gameStateManager.screen)
        if self.game.selectedModel.AP + self.game.cp != 0:
            self.rollAgain_button.draw(self.gameStateManager.screen)

        pygame.display.flip()

        for dice in diceList:
            dice.roll_dice(self.gameStateManager.screen)
            if self.dice_1 in diceList:
                roll_1 = self.dice_1.face
            if self.dice_2 in diceList:
                roll_2 = self.dice_2.face

        print('Melee Diceroll Door')

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.game.selectedModel.weapon == "Axe":
                        if self.psyup_button.rect.collidepoint(pygame.mouse.get_pos()):
                            if psyPoints <= self.game.psyPoints:
                                psyPoints += 1
                            if self.melee_door(roll_1, roll_2, psyPoints):
                                print("success")

                        if self.psydown_button.rect.collidepoint(pygame.mouse.get_pos()):
                            if psyPoints > 0:
                                psyPoints -= 1
                            if self.melee_door(roll_1, roll_2, psyPoints):
                                print("success")

                    if self.accept_button.rect.collidepoint(pygame.mouse.get_pos()):
                        self.game.psyPoints -= psyPoints
                        print(self.game.psyPoints)
                        if self.melee_door(roll_1, roll_2, psyPoints):
                            self.game.map.remove(self.game.clickedTile)
                            newTile = self.game.clickedTile.get_destroyed()
                            self.game.map.append(newTile)
                            self.game.clickedTile = newTile
                        self.gameStateManager.screen.fill('black')
                        self.gameStateManager.run_gamestate("smAction")

                    
                    if self.game.selectedModel.AP + self.game.cp != 0:
                        if self.rollAgain_button.rect.collidepoint(pygame.mouse.get_pos()):
                            self.reduce_ap(1)
                            self.gameStateManager.screen.fill('black')
                            self.gameStateManager.run_gamestate("mlRollDoorSM")
                                                   

class ChooseBlip:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game
        self.activate_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.end_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.activate_button = Button(810, 500, self.activate_image, 1)
        self.end_button = Button(810, 600, self.end_image, 1)
        self.model_1_button = Button(100,100, self.activate_image, 1)
        self.model_2_button = Button(200,100, self.activate_image, 1)
        self.model_3_button = Button(300,100, self.activate_image, 1)

    def run(self):

        buttonlist = []
        if self.game.selectedTile.blips.__len__() > 0:
            buttonlist.append(self.model_1_button)
        if self.game.selectedTile.blips.__len__() > 1:
            buttonlist.append(self.model_2_button)
        if self.game.selectedTile.blips.__len__() > 2:
            buttonlist.append(self.model_3_button)

        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)

        for button in buttonlist:
            button.draw(self.gameStateManager.screen)

        self.end_button.draw(self.gameStateManager.screen)
        self.activate_button.draw(self.gameStateManager.screen)
        pygame.display.flip()

        print('Choose Blip')

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()  

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.activate_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.game.selectedModel != None:
                            self.gameStateManager.screen.fill("black")
                            self.gameStateManager.run_gamestate("blAction")

                    elif self.end_button.rect.collidepoint(pygame.mouse.get_pos()):
                        self.game.reset_select()
                        self.game.reset_clicked()
                        self.gameStateManager.screen.fill('black')
                        self.gameStateManager.run_gamestate("gsTurn")

                    for button in buttonlist:
                        if button.rect.collidepoint(pygame.mouse.get_pos()):
                            if button == self.model_1_button:
                                self.game.selectedModel = self.game.selectedTile.blips[0]
                                print(self.game.selectedModel.AP)
                            if button == self.model_2_button:
                                self.game.selectedModel = self.game.selectedTile.blips[1]
                                print(self.game.selectedModel.AP)
                            if button == self.model_3_button:
                                self.game.selectedModel = self.game.selectedTile.blips[2]
                                print(self.game.selectedModel.AP)
                            print(self.game.selectedModel.count)


class gsAction:
    def __init__(self, gameStateManager, game) -> None:
        self.game = game
        self.gameStateManager = gameStateManager
        self.move_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.interact_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.turn_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.melee_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.end_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.move_button = Button(810, 400, self.move_image, 1)
        self.interact_button = Button(810, 500, self.interact_image, 1)
        self.turn_button = Button(810, 600, self.turn_image, 1)
        self.melee_button = Button(810, 700, self.melee_image, 1)
        self.end_button = Button(810, 800, self.end_image, 1)

    def check_move(self):
        inRange = False
        burning = False
        doorOpen = False
        occupied = False

        if isinstance(self.game.clickedTile, Tile):
            if ((self.game.selectedTile.x + 1 == self.game.clickedTile.x) or (self.game.selectedTile.x - 1 == self.game.clickedTile.x) or (self.game.selectedTile.x == self.game.clickedTile.x)) and ((self.game.selectedTile.y + 1 == self.game.clickedTile.y) or (self.game.selectedTile.y - 1 == self.game.clickedTile.y) or (self.game.selectedTile.y == self.game.clickedTile.y)):
                inRange = True
                print("inRange")
            if (self.game.clickedTile.isBurning == False) or (self.game.selectedTile.isBurning == True):
                burning = True
                print("burning")
            if (self.game.clickedTile.isOccupied == False) or (isinstance(self.game.clickedTile.occupand, Item)):
                occupied = True
                print("occupied")
            if isinstance(self.game.clickedTile, Door):
                if self.game.clickedTile.isOpen:
                    doorOpen = True
                    print("Door open")
            else:
                doorOpen = True
                print("Door open")

            if inRange and burning and doorOpen and occupied:
                return True
            else:
                return False
        else: 
            return False

    def calculate_movement_cost(self):
        face = self.game.selectedModel.face
        if ((self.game.selectedTile.x - face[0] == self.game.clickedTile.x) and (face[0] != 0)) or ((self.game.selectedTile.y - face[1] == self.game.clickedTile.y) and (face[1] != 0)):
            return 2
        else:
            return 1
            
    def move_model(self):
        self.game.clickedTile.occupand = self.game.selectedModel
        self.game.selectedTile.isOccupied = False
        self.game.selectedTile.occupand = None
        self.game.clickedTile.isOccupied = True
        pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.selectedTile.button.rect)
        pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.clickedTile.button.rect)
        self.game.selectedTile.render(self.gameStateManager.screen)
        self.game.clickedTile.render(self.gameStateManager.screen)
        pygame.display.update(self.game.clickedTile.button.rect)
        pygame.display.update(self.game.selectedTile.button.rect)
        self.game.selectedTile = self.game.clickedTile
        self.game.reset_clicked()
        self.gameStateManager.freeTurn = True

    def check_door(self):
        face = self.game.selectedModel.face
        if isinstance(self.game.clickedTile, Door):
            if ((self.game.selectedTile.x + face[0] == self.game.clickedTile.x) and (face[0] != 0)) or ((self.game.selectedTile.y + face[1] == self.game.clickedTile.y) and (face[1] != 0)):
                print("Door")
                return True
        else:
            return False
        
    def check_melee(self):
        if isinstance(self.game.clickedTile, Tile):
            if (self.game.selectedTile.x + self.game.selectedModel.face[0] == self.game.clickedTile.x) and (self.game.selectedTile.y + self.game.selectedModel.face[1] == self.game.clickedTile.y):
                if self.game.clickedModel != None:
                    return True
                elif(isinstance(self.game.clickedTile, Door)):
                    if self.game.clickedTile.isOpen == False:
                        return True
                else: 
                    return False

    def run(self):
        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)

        self.move_button.draw(self.gameStateManager.screen)
        if self.check_door():
            self.interact_button.draw(self.gameStateManager.screen)
        self.turn_button.draw(self.gameStateManager.screen)
        if self.check_melee():
            self.melee_button.draw(self.gameStateManager.screen)
        self.end_button.draw(self.gameStateManager.screen)

        pygame.display.flip()

        print('GS Action')

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for tile in self.game.map:
                            tile.scroll((0, -1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_w:
                        for tile in self.game.map:
                            tile.scroll((0, 1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_a:
                        for tile in self.game.map:
                            tile.scroll((1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    if event.key == pygame.K_d:
                        for tile in self.game.map:
                            tile.scroll((-1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    self.gameStateManager.screen.fill("black")

                    for tile in self.game.map:
                        tile.render(self.gameStateManager.screen)

                    self.move_button.draw(self.gameStateManager.screen)
                    if self.check_door():
                        self.interact_button.draw(self.gameStateManager.screen)
                    self.turn_button.draw(self.gameStateManager.screen)
                    if self.check_melee():
                        self.melee_button.draw(self.gameStateManager.screen)
                    self.end_button.draw(self.gameStateManager.screen)
                    
                    pygame.display.flip()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.move_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.check_move():
                            if self.calculate_movement_cost() <= (self.game.selectedModel.AP):
                                self.game.selectedModel.AP -= self.calculate_movement_cost()
                                self.move_model()       #add walking through flame
                    
                    elif self.interact_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.check_door():
                            if self.game.selectedModel.AP != 0:
                                self.game.interact_door(self.game.clickedTile)
                                self.game.selectedModel.AP -= 1
                                pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.clickedTile.button.rect)
                                self.game.clickedTile.render(self.gameStateManager.screen)
                                pygame.display.update(self.game.clickedTile.button.rect)

                    elif self.turn_button.rect.collidepoint(pygame.mouse.get_pos()):
                        self.gameStateManager.screen.fill('black')
                        self.gameStateManager.run_gamestate('gsTruning')

                    elif self.end_button.rect.collidepoint(pygame.mouse.get_pos()):
                        self.game.selectedModel.AP = 0
                        self.game.reset_select()
                        self.game.reset_clicked()
                        self.gameStateManager.screen.fill('black')
                        self.gameStateManager.run_gamestate('gsTurn')

                    else:
                        for tile in self.game.map:
                            if isinstance(tile, Tile):
                                if tile.button.rect.collidepoint(pygame.mouse.get_pos()):
                                    if tile != self.game.selectedTile:
                                        self.game.clickedTile = tile
                                        if self.check_melee():
                                            pygame.draw.rect(self.gameStateManager.screen, 'black', self.melee_button.rect)
                                            self.melee_button.draw(self.gameStateManager.screen)
                                            pygame.display.update(self.melee_button.rect)
                                        if self.check_door():
                                            pygame.draw.rect(self.gameStateManager.screen, 'black', self.interact_button.rect)
                                            self.interact_button.draw(self.gameStateManager.screen)
                                            pygame.display.update(self.interact_button.rect)
                                        print(tile)
                                        if tile.isOccupied:
                                            if isinstance(tile.occupand, SpaceMarine):
                                                self.game.clickedModel = tile.occupand


class blAction:
    def __init__(self, gameStateManager, game) -> None:
        self.game = game
        self.gameStateManager = gameStateManager
        self.move_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.interact_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.reveal_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.end_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.move_button = Button(810, 500, self.move_image, 1)
        self.interact_button = Button(810, 600, self.interact_image, 1)
        self.reveal_button = Button(810, 700, self.reveal_image, 1)
        self.end_button = Button(810, 800, self.end_image, 1)

    def check_move(self):
        inRange = False
        burning = False
        doorOpen = False
        occupied = False
        seen = True

        if isinstance(self.game.clickedTile, Tile):
            if ((self.game.selectedTile.x + 1 == self.game.clickedTile.x) or (self.game.selectedTile.x - 1 == self.game.clickedTile.x) or (self.game.selectedTile.x == self.game.clickedTile.x)) and ((self.game.selectedTile.y + 1 == self.game.clickedTile.y) or (self.game.selectedTile.y - 1 == self.game.clickedTile.y) or (self.game.selectedTile.y == self.game.clickedTile.y)):
                inRange = True
                print("inRange")
            if (self.game.clickedTile.isBurning == False) or (self.game.selectedTile.isBurning == True):
                burning = True
                print("burning")
            if (self.game.clickedTile.isOccupied == False) or (isinstance(self.game.clickedTile.occupand, Item)):
                occupied = True
                print("occupied")
            if isinstance(self.game.clickedTile, Door):
                if self.game.clickedTile.isOpen:
                    doorOpen = True
                    print("Door open")
            else:
                doorOpen = True
                print("Door open")

            if self.game.clickedTile in self.game.check_full_vision():
                seen = False
                print("seen!")

            if inRange and burning and doorOpen and occupied and seen:
                return True
            else:
                return False 

    def check_door(self):
        if isinstance(self.game.clickedTile, Door):
            if ((self.game.selectedTile.x + 1 == self.game.clickedTile.x) or (self.game.selectedTile.x - 1 == self.game.clickedTile.x) or (self.game.selectedTile.x == self.game.clickedTile.x)) and ((self.game.selectedTile.y + 1 == self.game.clickedTile.y) or (self.game.selectedTile.y - 1 == self.game.clickedTile.y) or (self.game.selectedTile.y == self.game.clickedTile.y)):
                print("Door")
                return True
        else:
            return False
            
    def move_blip(self):
        if isinstance(self.game.selectedTile, EntryPoint):
            self.game.selectedTile.blips.remove(self.game.selectedModel)
            print(self.game.selectedModel)
            self.game.clickedTile.occupand = self.game.selectedModel
            self.game.clickedTile.isOccupied = True
            self.game.selectedTile = self.game.clickedTile
            self.game.reset_clicked()
            pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.selectedTile.button.rect)
            self.game.selectedTile.render(self.gameStateManager.screen)
            pygame.display.update(self.game.selectedTile.button.rect)

        else:
            self.game.clickedTile.occupand = self.game.selectedModel
            self.game.clickedTile.isOccupied = True
            self.game.selectedTile.isOccupied = False
            self.game.selectedTile.occupand = None
            pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.selectedTile.button.rect)
            self.game.selectedTile.render(self.gameStateManager.screen)
            pygame.display.update(self.game.selectedTile.button.rect)
            self.game.selectedTile = self.game.clickedTile
            pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.selectedTile.button.rect)
            self.game.selectedTile.render(self.gameStateManager.screen)
            pygame.display.update(self.game.selectedTile.button.rect)
            
            self.game.reset_clicked()

    def run(self):
        
        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)

        self.move_button.draw(self.gameStateManager.screen)
        self.interact_button.draw(self.gameStateManager.screen)
        self.reveal_button.draw(self.gameStateManager.screen)
        self.end_button.draw(self.gameStateManager.screen)

        pygame.display.flip()

        print('BL Action')

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for tile in self.game.map:
                            tile.scroll((0, -1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_w:
                        for tile in self.game.map:
                            tile.scroll((0, 1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_a:
                        for tile in self.game.map:
                            tile.scroll((1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    if event.key == pygame.K_d:
                        for tile in self.game.map:
                            tile.scroll((-1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    self.gameStateManager.screen.fill("black")

                    for tile in self.game.map:
                        tile.render(self.gameStateManager.screen)

                    self.move_button.draw(self.gameStateManager.screen)
                    self.interact_button.draw(self.gameStateManager.screen)
                    self.reveal_button.draw(self.gameStateManager.screen)
                    self.end_button.draw(self.gameStateManager.screen)
                    
                    pygame.display.flip()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.move_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.game.clickedTile != None:
                            if self.check_move():
                                if self.game.selectedModel.AP > 0:
                                    self.game.selectedModel.AP -= 1
                                    self.move_blip()

                    elif self.end_button.rect.collidepoint(pygame.mouse.get_pos()):
                        self.game.selectedModel.AP = 0
                        self.game.reset_select()
                        self.game.reset_clicked()
                        self.gameStateManager.screen.fill('black')
                        self.gameStateManager.run_gamestate('gsTurn')

                    elif self.interact_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.check_door():
                            if self.game.selectedModel.AP > 0:
                                self.game.selectedModel.AP -= 1
                                self.game.interact_door(self.game.clickedTile)
                                pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.clickedTile.button.rect)
                                self.game.clickedTile.render(self.gameStateManager.screen)
                                pygame.display.update(self.game.clickedTile.button.rect)

                    elif self.reveal_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.game.selectedModel.AP == 6:
                            self.gameStateManager.screen.fill('black')
                            self.game.reset_clicked()
                            self.gameStateManager.run_gamestate('reveal')
                            #add option, if tile is Entrypoint, just add the GS to the entrypoint directly
                        else:
                            print("Need more AP!")

                    else:
                        for tile in self.game.map:
                            if isinstance(tile, Tile):
                                if tile != self.game.selectedTile:
                                    if tile.button.rect.collidepoint(pygame.mouse.get_pos()):
                                        if tile.isOccupied:
                                            self.game.clickedTile = tile
                                            self.game.clickedModel = tile.occupand
                                        else:
                                            self.game.clickedTile = tile
                                        print(tile)
                                        print(tile.occupand)


class revealGS:
    def __init__(self, gameStateManager, game) -> None:
        self.game = game
        self.gameStateManager = gameStateManager

        self.left_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.right_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.accept_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.left_button = Button(810, 400, self.left_image, 1)
        self.right_button = Button(810, 500, self.right_image, 1)
        self.accept_button = Button(810, 700, self.accept_image, 1)
        self.place_button = Button(810, 800, self.place_image, 1)

    def check_place(self, tile):
        if ((self.game.clickedTile.x == tile.x +1) or (self.game.clickedTile.x == tile.x -1) or (self.game.clickedTile.x == tile.x)) and ((self.game.clickedTile.y == tile.y +1) or (self.game.clickedTile.y == tile.y -1) or (self.game.cklickedTile.y == tile.y)):
            if isinstance(self.game.clickedTile, Tile):
                if not self.game.clickedTile.isOccupied:
                    if not self.game.clickedTile.isBurning:
                        #rewrite to check against list
                        return True
                
    def check_space(self, startTile):
        frSpace = []
        for tile in self.game.map:
            if ((startTile.x + 1 == tile.x) or (startTile.x - 1 == tile.x) or (startTile.x == tile.x)) and ((startTile.y + 1 == tile.y) or (startTile.y - 1 == tile.y) or (startTile.y == tile.y)):
                if isinstance(tile, Tile):
                    if not tile.isBurning:
                        if not tile.isOccupied:
                            if isinstance(tile,Door):
                                if tile.isOpen == True:
                                    frSpace.append(tile)
                            else:
                                frSpace.append(tile)
                elif isinstance(tile, EntryPoint):
                    frSpace.append(tile)

        for tile in frSpace[:]:
            if tile == startTile:
                frSpace.remove(startTile)
            if tile in self.game.check_full_vision():
                frSpace.remove(tile)

        return frSpace
        
    def run(self):
        gsList = []
        freeTiles = self.check_space(self.game.selectedTile)
        print(freeTiles)
        hasPlaced = True

        a = 0
        while (a < self.game.selectedModel.count) and self.game.gsModelList.__len__() <= self.game.maxGS:
            a += 1
            gsList.append(Genestealer())
        print(gsList)
        print(self.game.selectedModel.count)

        if self.game.maxGS == self.game.gsModelList.__len__() - 1:
            if self.game.broodLord == False or self.game.selectedmodel.count != 3:
                self.game.blModelList.remove(self.game.selectedModel)
                self.game.blipReserve.append(self.game.selectedModel.count)
                self.game.reset_select()
                self.game.reset_clicked()
                self.gameStateManager.screen.fill('black')
                self.gameStateManager.run_gamestate('gsTurn')

        print (self.game.selectedModel)
        #add Broodlord Button here
        self.game.blipReserve.append(self.game.selectedModel.count)
        self.game.blModelList.remove(self.game.selectedModel)
        self.game.selectedModel = gsList.pop(0)
        self.game.selectedTile.occupand = self.game.selectedModel
        self.game.gsModelList.append(self.game.selectedModel)

        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)

        self.right_button.draw(self.gameStateManager.screen)
        self.left_button.draw(self.gameStateManager.screen)
        self.accept_button.draw(self.gameStateManager.screen)
        
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for tile in self.game.map:
                            tile.scroll((0, -1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_w:
                        for tile in self.game.map:
                            tile.scroll((0, 1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_a:
                        for tile in self.game.map:
                            tile.scroll((1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    if event.key == pygame.K_d:
                        for tile in self.game.map:
                            tile.scroll((-1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    self.gameStateManager.screen.fill("black")

                    for tile in self.game.map:
                        tile.render(self.gameStateManager.screen)

                    self.right_button.draw(self.gameStateManager.screen)
                    self.left_button.draw(self.gameStateManager.screen)
                    if hasPlaced:
                        self.accept_button.draw(self.gameStateManager.screen)
                    if hasPlaced == False:
                        self.place_button.draw(self.gameStateManager.screen)
                    
                    pygame.display.flip()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.left_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if hasPlaced:
                            self.game.turn_model(self.game.selectedModel, "left")
                            pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.selectedTile.button.rect)
                            self.game.selectedTile.render(self.gameStateManager.screen)
                            pygame.display.update(self.game.selectedTile.button.rect)

                    elif self.right_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if hasPlaced:
                            self.game.turn_model(self.game.selectedModel, "right")
                            pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.selectedTile.button.rect)
                            self.game.selectedTile.render(self.gameStateManager.screen)
                            pygame.display.update(self.game.selectedTile.button.rect)

                    elif self.accept_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if gsList.__len__() == 0 or freeTiles.__len__() == 0:
                            self.game.reset_select()
                            self.game.reset_clicked()
                            self.gameStateManager.screen.fill('black')
                            self.gameStateManager.run_gamestate('gsTurn')
                        else:
                            hasPlaced = False
                            self.game.selectedModel = gsList.pop(0)
                            if self.game.selectedTile in freeTiles:
                                freeTiles.remove(self.game.selectedTile)
                            pygame.draw.rect(self.gameStateManager.screen,'black',self.accept_button.rect)
                            self.place_button.draw(self.gameStateManager.screen)
                            pygame.display.update(self.accept_button.rect)
                            pygame.display.update(self.place_button.rect)

                    elif self.place_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if hasPlaced == False:
                            if isinstance(self.game.selectedTile, Tile):
                                if self.game.selectedTile in freeTiles:
                                    self.game.selectedTile.occupand = self.game.selectedModel
                                    self.game.selectedTile.isOccupied = True
                                    pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.selectedTile.button.rect)
                                    self.game.selectedTile.render(self.gameStateManager.screen)
                                    pygame.display.update(self.game.selectedTile.button.rect)
                                    hasPlaced = True
                                    self.accept_button.draw(self.gameStateManager.screen)
                                    pygame.draw.rect(self.gameStateManager.screen, 'black', self.place_button.rect)
                                    pygame.display.update(self.accept_button.rect)
                                    pygame.display.update(self.place_button.rect)
                                else:
                                    print('select a valid tile')

                            elif isinstance(self.game.selectedTile, EntryPoint):
                                self.game.selectedTile.genstealers.append(self.game.selectedModel)
                                if gsList.__len__() == 0 or freeTiles.__len__() == 0:
                                    self.game.reset_select()
                                    self.game.reset_clicked()
                                    self.gameStateManager.screen.fill('black')
                                    self.gameStateManager.run_gamestate('gsTurn')
                                else:
                                    hasPlaced = False
                                    self.game.selectedModel = gsList.pop(0)

                    else:
                        if hasPlaced == False:
                            for tile in self.game.map:
                                if tile.button.rect.collidepoint(pygame.mouse.get_pos()):
                                    if tile in self.game.check_full_vision():
                                        print("Tile in vision")
                                    if isinstance(tile, Tile) and (tile in freeTiles):
                                        self.game.selectedTile = tile
                                    elif isinstance(tile, EntryPoint) and (tile in freeTiles):
                                        self.game.selectedTile = tile
                                    else:
                                        print('select a valid Tile(click)')


class gsTurn:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game
        self.activate_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.end_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.activate_button = Button(810, 500, self.activate_image, 1)
        self.end_button = Button(810, 600, self.end_image, 1)

    def run(self):

        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)

        self.end_button.draw(self.gameStateManager.screen)
        self.activate_button.draw(self.gameStateManager.screen)
        pygame.display.flip()

        print('GS Turn')

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for tile in self.game.map:
                            tile.scroll((0, -1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_w:
                        for tile in self.game.map:
                            tile.scroll((0, 1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_a:
                        for tile in self.game.map:
                            tile.scroll((1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    if event.key == pygame.K_d:
                        for tile in self.game.map:
                            tile.scroll((-1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    self.gameStateManager.screen.fill("black")

                    for tile in self.game.map:
                        tile.render(self.gameStateManager.screen)

                    self.activate_button.draw(self.gameStateManager.screen)
                    self.end_button.draw(self.gameStateManager.screen)
                    
                    pygame.display.flip()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.end_button.rect.collidepoint(pygame.mouse.get_pos()):
                        self.game.reset_select()
                        self.game.reset_clicked()
                        self.gameStateManager.screen.fill('black')
                        self.gameStateManager.run_gamestate("command")

                    elif self.activate_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.game.selectedModel != None:
                            if self.game.selectedModel in self.game.blModelList:
                                self.gameStateManager.screen.fill('black')
                                self.gameStateManager.run_gamestate("blAction")
                            else:
                                self.gameStateManager.screen.fill('black')
                                self.gameStateManager.run_gamestate('gsAction')
                        elif self.game.selectedTile != None:
                            self.gameStateManager.screen.fill('black')
                            self.gameStateManager.run_gamestate('blSelect')

                    else:
                        for tile in self.game.map:
                            if tile.button.rect.collidepoint(pygame.mouse.get_pos()):
                                if isinstance(tile, EntryPoint) or isinstance(tile.occupand, Genestealer) or isinstance(tile.occupand, Blip):
                                    self.game.selectedTile = tile
                                    print(tile)
                                    if not isinstance(tile, EntryPoint):
                                        self.game.selectedModel = tile.occupand 


class gsTurning:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game
        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.amount_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.right_button = Button(810, 500, self.place_image, 1)
        self.left_button = Button(810, 600, self.amount_image, 1)
        self.accept_button = Button(810, 700, self.amount_image, 1)

    def run(self):
        turnAmount = 0

        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)
        
        self.right_button.draw(self.gameStateManager.screen)
        self.left_button.draw(self.gameStateManager.screen)
        self.accept_button.draw(self.gameStateManager.screen)
        pygame.display.flip()

        print('GS Turning')

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for tile in self.game.map:
                            tile.scroll((0, -1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_w:
                        for tile in self.game.map:
                            tile.scroll((0, 1))
                        print(self.game.map[0].y)
                        print(self.game.map[0].graphicsY)

                    if event.key == pygame.K_a:
                        for tile in self.game.map:
                            tile.scroll((1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    if event.key == pygame.K_d:
                        for tile in self.game.map:
                            tile.scroll((-1, 0))
                        print(self.game.map[0].x)
                        print(self.game.map[0].graphicsX)

                    self.gameStateManager.screen.fill("black")

                    for tile in self.game.map:
                        tile.render(self.gameStateManager.screen)

                    self.left_button.draw(self.gameStateManager.screen)
                    self.right_button.draw(self.gameStateManager.screen)
                    self.accept_button.draw(self.gameStateManager.screen)
                    
                    pygame.display.flip()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.left_button.rect.collidepoint(pygame.mouse.get_pos()):
                        turnAmount += 1
                        self.game.turn_model(self.game.selectedModel, "left")
                        pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.selectedTile.button.rect)
                        self.game.selectedTile.render(self.gameStateManager.screen)
                        pygame.display.update(self.game.selectedTile.button.rect)

                    elif self.right_button.rect.collidepoint(pygame.mouse.get_pos()):
                        turnAmount -= 1
                        self.game.turn_model(self.game.selectedModel, "right")
                        pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.selectedTile.button.rect)
                        self.game.selectedTile.render(self.gameStateManager.screen)
                        pygame.display.update(self.game.selectedTile.button.rect)

                    elif self.accept_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if turnAmount == 0:
                            pass

                        elif turnAmount < 0:
                            cost = abs(turnAmount) % 4
                            match cost:
                                case 0:
                                    pass

                                case 1:
                                    if self.gameStateManager.freeTurn:
                                        self.gameStateManager.freeTurn = False
                                    elif self.game.selectedModel.AP > 0:
                                        self.game.selectedModel.AP -= 1
                                    else:
                                        print("Not enough AP/CP!")
                                        self.game.turn_model(self.game.selectedModel, "left")

                                case 2:
                                    if self.game.selectedModel.AP > 0:
                                        self.game.selectedModel.AP -= 1
                                    else:
                                        print("Not enough AP/CP!")
                                        self.game.turn_model(self.game.selectedModel, "full")

                                case 3:
                                    if self.gameStateManager.freeTurn:
                                        self.gameStateManager.freeTurn = False
                                    elif self.game.selectedModel.AP > 0:
                                        self.game.selectedModel.AP -= 1
                                    else:
                                        print("Not enough AP/CP!")
                                        self.game.turn_model(self.game.selectedModel, "right")

                        elif turnAmount > 0:
                            cost = abs(turnAmount) % 4
                            match cost:
                                case 0:
                                    pass

                                case 1:
                                    if self.gameStateManager.freeTurn:
                                        self.gameStateManager.freeTurn = False
                                    elif self.game.selectedModel.AP > 0:
                                        self.game.selectedModel.AP -= 1
                                    else:
                                        print("Not enough AP/CP!")
                                        self.game.turn_model(self.game.selectedModel, "right")
                                        

                                case 2:
                                    if self.game.selectedModel.AP > 0:
                                        self.game.selectedModel.AP -= 1
                                    else:
                                        print("Not enough AP/CP!")
                                        self.game.turn_model(self.game.selectedModel, "full")

                                case 3:
                                    if self.gameStateManager.freeTurn:
                                        self.gameStateManager.freeTurn = False
                                    elif self.game.selectedModel.AP > 0:
                                        self.game.selectedModel.AP -= 1
                                    else:
                                        print("Not enough AP/CP!")
                                        self.game.turn_model(self.game.selectedModel, "left")

                        self.gameStateManager.screen.fill("black")
                        print(self.game.selectedModel.AP)
                        self.gameStateManager.run_gamestate("gsAction")

class gamestateMain:
    def __init__(self,gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game

    def run(self):
        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.amount_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.place_button = Button(810, 500, self.place_image, 1)
        self.startNew_button = Button(810, 600, self.amount_image, 1)
        self.load_button = Button(810, 700, self.amount_image, 1)
        self.exit_button = Button(810, 800, self.amount_image, 1)

        print('Main')

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if self.exit_button.draw(self.gameStateManager.screen):
                pygame.quit
                sys.exit()
            
            if self.load_button.draw(self.gameStateManager.screen):
                pass

            if self.startNew_button.draw(self.gameStateManager.screen):
                self.game.load_level("level_1")
                self.gameStateManager.screen.fill("black")
                self.gameStateManager.run_gamestate("smPlace")

            pygame.display.update()


class MeleeDiceRoll:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game
        self.dice_1 = Dice(10,10)
        self.dice_2 = Dice(110, 10)
        self.dice_3 = Dice(210, 10)
        self.dice_4 = Dice(410, 10)
        self.dice_5 = Dice(510, 10)

    def turn_to_face(self, attacker, defender):
        match attacker.face:
            case (1, 0):
                match defender.face:
                    case (-1, 0):
                        pass
                    case (1, 0):
                        self.game.turn_model(defender, "full")
                    case (0, -1):
                        self.game.turn_model(defender, "left")
                    case (0, 1):
                        self.game.turn_model(defender, "right")
            case (-1, 0):
                match defender.face:
                    case (1, 0):
                        pass
                    case (-1, 0):
                        self.game.turn_model(defender, "full")
                    case (0, 1):
                        self.game.turn_model(defender, "left")
                    case (0, -1):
                        self.game.turn_model(defender, "right")
            case (0, 1):
                match defender.face:
                    case (0, -1):
                        pass
                    case (0, 1):
                        self.game.turn_model(defender, "full")
                    case (1, 0):
                        self.game.turn_model(defender, "left")
                    case (-1, 0):
                        self.game.turn_model(defender, "right")
            case (0, -1):
                match defender.face:
                    case (0, 1):
                        pass
                    case (0, -1):
                        self.game.turn_model(defender, "full")
                    case(1, 0):
                        self.game.turn_model(defender, "right")
                    case(-1, 0):
                        self.game.turn_model(defender, "left")

    def run(self):
        turnToFace = False
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
        self.face_button = Button(810, 400, self.place_image, 1)

        selectedDice = None
        psyPoints = 0
        
        parry = False
        guard = self.game.selectedModel.guard
        winner = None

        diceList = [self.dice_1, self.dice_2]

        if self.game.isPlaying == self.game.player1:
            if sm.weapon != "Thunderhammer":
                diceList.append(self.dice_3)
            if sm.weapon == "Powersword":
                parry = True
            if self.game.selectedModel.weapon == "Lightningclaws":
                diceList.append(self.dice_4)
                diceList.append(self.dice_5)
            else:
                diceList.append(self.dice_4)

        elif self.game.isPlaying == self.game.player2:
            if self.game.is_facing(gs, sm):
                if sm.weapon != "Thunderhammer" or facing == False:
                    diceList.append(self.dice_3)
                if sm.weapon == "Powersword" and facing:
                    parry = True
                if sm.weapon == "Lightningclaws" and facing:
                    diceList.append(self.dice_4)
                    diceList.append(self.dice_5)
                else:
                    diceList.append(self.dice_4)

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

            if winner != self.game.selectedModel:
                if self.face_button.draw(self.gameStateManager.screen):
                    if turnToFace:
                        turnToFace = False
                        print("turn to face")
                    else:
                        turnToFace = True
                        print("dont turn to face")

            if self.accept_button.draw(self.gameStateManager.screen):
                self.game.psyPoints -= psyPoints
                print(self.game.psyPoints)
                if turnToFace:
                    self.turn_to_face(self.game.selectedModle, self.game.clickedModel)
                    
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
                if self.game.selectedModel != None:
                    if self.game.isPlaying == self.game.player1:
                        self.gameStateManager.run_gamestate("smAction")
                    else:
                        self.gameStateManager.run_gamestate()
                else:
                    if self.game.isPlaying == self.game.player1:
                        self.gameStateManager.run_gamestate("smTurn")
                    else:
                        self.gameStateManager.run_gamestate()
            pygame.display.update()
            
pygame.init()
game = Game()
# wall = Wall("Pictures/Tiles/Floor_1.png",1,1)
# entry = EntryPoint("Pictures/Tiles/Floor_1.png",4,4)
# game.map.append(entry)
# game.map.append(wall)

screen = screen = pygame.display.set_mode((900, 900), pygame.DOUBLEBUF)
screen.fill("black")
gameStateManager = GameStateManager(game, screen)
# game.selectedModel = game.smModelList[0]
# game.clickedModel = game.gsModelList[0]
# game.clickedModel.face = (-1,0)
# game.clickedModel.isBroodlord = True
gameStateManager.run_gamestate("main")


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