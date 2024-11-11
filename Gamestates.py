from Models import *
from Board import *
from Game import * 

class GameStateManager:     #class to manage interactions between gamestates and provide a schared game object and storage
    def __init__(self, game, screen) -> None:
        self.game = game
        self.screen = screen
        self.gamestates = {"smTurn": smTurn(self, self.game), 
                           "smAction": smAction(self, self.game), 
                           "gsTurn": gsTurn(self, self.game),
                           "gsTruning": gsTurning(self, self.game),
                           "command": commandPhase(self, self.game), 
                           "smTurning": smTurning(self, self.game), 
                           "main":gamestateMain(self, self.game),
                           "gsStart": BLstart(self, self.game),
                           "blSelect": ChooseBlip(self, self.game), 
                           "gsPlace": PlaceBL(self, self.game), 
                           "mlRoll": MeleeDiceRoll(self, self.game), 
                           "mlRollDoor": MeleeDiceRollDoor(self, self.game),
                           "smPlace": PlaceSM(self, self.game)}
        self.runThread = True

        self.freeShot = False   #if sm has free shoot Action
        self.freeTurn = False   #if gs has a free turn
        self.freeMove = False   #if gs has a free move

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

    def take_blips(self):
        x = 0
        while x < self.BLAmount:
            choice = random.randint(0, self.game.blipSack.__len__() - 1)
            print(choice)
            a = self.gameStateManager.game.blipSack.pop(choice)
            self.blipList.append(a)
            x += 1

    def run_threat(self):
        while self.gameStateManager.runThread == True:
            self.gameStateManager.run_map_blPlace()
        
    def run(self):
        self.BLAmount = self.game.startBlip
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
                    thread.join()
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
                    pygame.display.update()

            if self.blipList.__len__() == 0:
                self.gameStateManager.runThread = False
                thread.join()
                self.gameStateManager.run_gamestate("command")

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
                
            pygame.display.update()

class PlaceBL:     #Gamestate where the Blips are Placed(reinforcement phase)
    def __init__(self, gameStateManager, game) -> None:
        self.game = game
        self.gameStateManager = gameStateManager
        self.BLAmount = int
        self.blipList = []

    def take_blips(self):
        x = 0
        while x < self.BLAmount:
            choice = random.randint(0, self.game.blipSack.__len__() - 1)
            print(choice)
            a = self.gameStateManager.game.blipSack.pop(choice)
            self.blipList.append(a)
            x += 1

    def run_threat(self):
        while self.gameStateManager.runThread == True:
            self.gameStateManager.run_map_blPlace()
        
    def run(self):
        self.BLAmount = self.game.reinforcement
        self.take_blips()
        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.amount_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.place_button = Button(810, 500, self.place_image, 1)
        self.amount_button = Button(810, 600, self.amount_image, 1)

        self.gameStateManager.runThread = True
        thread = threading.Thread(target=self.run_threat,args=())
        thread.start()
        self.gameStateManager.screen.fill("black")

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateManager.runThread = False
                    thread.join()
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
                    pygame.display.update()

            if self.blipList.__len__() == 0:
                self.gameStateManager.runThread = False
                thread.join()
                self.gameStateManager.run_gamestate("command") ### rewrite to GS turn

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
                
            pygame.display.update()

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
        self.gameStateManager.screen.fill("black")
        self.gameStateManager.run_gamestate('gsStart')

    def run(self):
        self.smList = self.game.smModelList.copy()
        finished = False

        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)
        self.place_button.draw(self.gameStateManager.screen)
        self.right_button.draw(self.gameStateManager.screen)
        self.left_button.draw(self.gameStateManager.screen)
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateManager.runThread = False
                    # thread.join()
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

                    for tile in self.game.map:
                        if isinstance(tile, Tile):
                            if tile.button.rect.collidepoint(pygame.mouse.get_pos()):
                                self.game.selectedTile = tile  
                                if tile.isOccupied:
                                    self.game.selectedModel = tile.occupand
                                print(tile.occupand)   
                                print("It works!")

                    if self.smList.__len__() > 0:   
                        if self.place_button.rect.collidepoint(pygame.mouse.get_pos()):
                            self.placeModel()

                    else:
                        if self.accept_button.rect.collidepoint(pygame.mouse.get_pos()):
                            self.endState()

                    if self.game.selectedModel != None:
                        if self.right_button.rect.collidepoint(pygame.mouse.get_pos()):
                            self.game.turn_model( self.game.selectedModel, "left")
                            pygame.draw.rect(self.gameStateManager.screen, (0,0,0), self.game.selectedTile.button.rect)
                            self.game.selectedTile.render(self.gameStateManager.screen)
                            pygame.display.update(self.game.selectedTile.button.rect)
                        
                        if self.left_button.rect.collidepoint(pygame.mouse.get_pos()):
                            self.game.turn_model( self.game.selectedModel, "right")
                            pygame.draw.rect(self.gameStateManager.screen, (0,0,0), self.game.selectedTile.button.rect)
                            self.game.selectedTile.render(self.gameStateManager.screen)
                            pygame.display.update(self.game.selectedTile.button.rect)


class commandPhase:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game
        self.dice = Dice(800, 100)
        self.roll = int

    def run(self):
        print(self.game.smModelList)
        for tile in self.game.map:
            if isinstance(tile, Tile):
                if tile.isBurning:
                    tile.isBurning = False
                    tile.change_picture(tile.picturePath)

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
        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.amount_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.reroll_button = Button(810, 500, self.place_image, 1)
        self.accept_button = Button(810, 600, self.amount_image, 1)

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
                    pygame.display.update()

            if reroll == True:
                if self.reroll_button.draw(self.gameStateManager.screen):
                    self.gameStateManager.screen.fill("black")
                    for tile in self.game.map:
                        tile.render(self.gameStateManager.screen)
                    self.dice.roll_dice(self.gameStateManager.screen)
                    self.roll = self.dice.face
                    reroll = False

            if self.accept_button.draw(self.gameStateManager.screen):
                self.game.cp = self.roll
                self.gameStateManager.runThread = False
                self.gameStateManager.screen.fill("black")
                
                self.game.selectedModel = None
                self.game.selectedTile = None
                self.game.clickedModel = None
                self.game.clickedTile = None

                self.gameStateManager.run_gamestate("smTurn") #input the run State for SM

            pygame.display.update()

class smAction:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game

    def run_thread(self):
        while self.gameStateManager.runThread:
            self.gameStateManager.run_map_smActivation()

    def check_move(self, model, startTile, endTile):
        direction = False
        burning = False
        doorOpen = False
        occupied = False
        if isinstance(endTile, Tile):
            if (((endTile.x == startTile.x + model.face[0]) or (endTile.x == startTile.x - model.face[0])) and model.face[0] != 0) or (((endTile.y == startTile.y + model.face[1]) or (endTile.y == startTile.y - model.face[1])) and model.face[1] != 0):
                direction = True
            if endTile.isBurning == False:
                burning = True
            if endTile.isOccupied == False:
                occupied = True
            if isinstance(endTile, Door):
                if endTile.isOpen:
                    doorOpen = True
            else:
                doorOpen = True


        if direction and burning and doorOpen and occupied:
            return True
        else:
            return False 
        
    def check_melee(self, startTile, attacker):
        for tile in self.game.map:
            if tile.x == startTile.x + attacker.face[0] and tile.y == startTile.y + attacker.face[1]:
                if tile.isOccupied:
                    if isinstance(tile.occupand, Genestealer):
                        return True
                if isinstance(tile, Door):
                    if tile.isOpen == False:
                        return True
        
    def calculate_movement_cost(self, model, startTile, endTile):
        if (endTile.x == startTile.x + model.face[0]) or (endTile.y == startTile.y + model.face[1]):
            return 1
        elif (endTile.x == startTile.x - model.face[0]) or (endTile.y == startTile.y - model.face[1]):
            return 2
            
    def run(self):
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


        # self.gameStateManager.runThread = True
        # thread = threading.Thread(target=self.run_thread,args=())
        # thread.start()

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
                    pygame.display.update()

            if self.move_button.draw(self.gameStateManager.screen):
                if self.game.selectedTile != None:
                    if self.game.clickedTile != None:
                        if self.check_move(self.game.selectedModel, self.game.selectedTile, self.game.clickedTile):
                            if self.calculate_movement_cost(self.game.selectedModel, self.game.selectedTile, self.game.clickedTile) <= (self.game.selectedModel.AP + self.game.cp):
                                self.game.reduce_ap_sm(self.game.selectedModel, self.calculate_movement_cost(self.game.selectedModel, self.game.selectedTile, self.game.clickedTile))
                                game.move_model(self.game.selectedModel, self.game.selectedTile, self.game.clickedTile)
                                self.gameStateManager.freeShoot = True
                                self.gameStateManager.screen.fill("black")

            if self.turn_button.draw(self.gameStateManager.screen):
                self.gameStateManager.runThread = False
                self.gameStateManager.screen.fill('black')
                self.gameStateManager.run_gamestate("smTurning")

            if self.accept_button.draw(self.gameStateManager.screen):
                self.game.selectedModel.AP = 0
                self.game.selectedModel = None
                self.game.selectedTile = None
                self.game.clickedModel = None
                self.game.clickedTile = None
                self.gameStateManager.screen.fill("black")
                self.gameStateManager.run_gamestate("smTurn")

            if self.check_melee(self.game.selectedTile, self.game.selectedModel):
                if self.melee_button.draw(self.gameStateManager.screen):
                    for tile in self.game.map:
                        if tile.x == self.game.selectedTile.x + self.game.selectedModel.face[0] and tile.y == self.game.selectedTile.y + self.game.selectedModel.face[1]:
                            self.game.clickedTile = tile
                            self.game.clickedModel = tile.occupand
                            if tile.isOccupied:
                                self.gameStateManager.run_gamestate("mlRoll")
                            else:
                                self.gameStateManager.run_gamestate("mlRollDoor")
                    
            if isinstance(self.game.clickedTile, Door):
                print("Door")
                if self.interact_button.draw(self.gameStateManager.screen):
                    print("open/close")
                    if self.game.selectedModel.AP + self.game.cp > 0:
                        self.game.interact_door(self.game.clickedTile)
                        self.game.reduce_ap_sm(self.game.selectedModel, 1)
            
            for tile in self.game.map:
                if tile.button.draw(self.gameStateManager.screen):
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
                        self.game.clickedTile = tile
                        print(self.game.clickedTile)
                tile.render(self.gameStateManager.screen)
            pygame.display.update()            

class smTurn:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game

    def run_thread(self):
        while self.gameStateManager.runThread:
            self.gameStateManager.run_map_smTurn()

    def run(self):
        self.activate_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.end_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.activate_button = Button(810, 500, self.activate_image, 1)
        self.end_button = Button(810, 600, self.end_image, 1)

        self.gameStateManager.runThread = True
        thread = threading.Thread(target=self.run_thread,args=())
        thread.start()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateManager.runThread = False
                    thread.join()
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
                    pygame.display.update()

            if self.game.selectedModel != None:
                if self.activate_button.draw(self.gameStateManager.screen):
                    self.gameStateManager.runThread = False
                    thread.join()
                    self.gameStateManager.run_gamestate("smAction")

            if self.end_button.draw(self.gameStateManager.screen):
                self.gameStateManager.run_gamestate("gsPlace")

            pygame.display.update()

class gsAction:
    def __init__(self, gameStateManager, game) -> None:
        self.game = game
        self.gameStateManager = gameStateManager

    def run(self):
        pass

class gsTurn:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game

    def run(self):
        self.activate_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.end_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.activate_button = Button(810, 500, self.activate_image, 1)
        self.end_button = Button(810, 600, self.end_image, 1)

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
                    pygame.display.update()

            if self.game.selectedModel != None or isinstance(self.game.selectedTile, EntryPoint):
                if self.activate_button.draw(self.gameStateManager.screen):
                    self.gameStateManager.runThread = False
                    if self.game.selectedModel != None:
                        self.gameStateManager.run_gamestate()
                    if isinstance(self.game.selectedTile, EntryPoint):
                        self.gameStateManager.run_gamestate("blSelect")

            if self.end_button.draw(self.gameStateManager.screen):
                pass
                # implement gs place

            for tile in self.game.map:
                if tile.button.draw(self.gameStateManager.screen):
                    if isinstance(tile, EntryPoint):
                        self.game.selectedTile = tile
                        self.game.selectedModel = None
                    elif isinstance(tile, Wall):
                        pass
                    elif tile.isOccupied:
                        if tile.occupand in self.game.smModelList:
                            pass
                        else:
                            self.game.selectedTile = tile
                            self.game.selectedModel = tile.occupand
                tile.render(self.gameStateManager.screen)

            pygame.display.update()

class ChooseBlip:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game

    def run(self):
        model = None
        self.activate_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.end_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.activate_button = Button(810, 500, self.activate_image, 1)
        self.end_button = Button(810, 600, self.end_image, 1)
        self.model_1_button = Button(100,100, self.activate_image, 1)
        self.model_2_button = Button(200,100, self.activate_image, 1)
        self.model_3_button = Button(300,100, self.activate_image, 1)

        buttonlist = []
        if self.game.selectedTile.blips.__len__() > 0:
            buttonlist.append(self.model_1_button)
        if self.game.selectedTile.blips.__len__() > 1:
            buttonlist.append(self.model_2_button)
        if self.game.selectedTile.blips.__len__() > 2:
            buttonlist.append(self.model_3_button)

        self.gameStateManager.screen.fill("black")

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()  

            if self.model_1_button.hover(self.gameStateManager.screen):
                print(self.game.selectedTile.blips[0].count)

            if self.model_1_button.draw(self.gameStateManager.screen):
                model = self.game.selectedTile.blips[0]

            if self.model_2_button in buttonlist:
                if self.model_2_button.hover(self.gameStateManager.screen):
                    print(self.game.selectedTile.blips[1].count)
                if self.model_2_button.draw(self.gameStateManager.screen):
                    model = self.game.selectedTile.blips[1]

            if self.model_3_button in buttonlist:
                if self.model_3_button.hover(self.gameStateManager.screen):
                    print(self.game.selectedTile.blips[2].count)
                if self.model_3_button.draw(self.gameStateManager.screen):
                    model = self.game.selectedTile.blips[2]

            if self.activate_button.draw(self.gameStateManager.screen):
                if model != None:
                    if self.game.get_tile(self.game.selectedTile.x + self.game.selectedTile.face[0], self.game.selectedTile.y + self.game.selectedTile.face[1]).isOccupied == False:
                        self.game.selectedModel = model
                        self.game.selectedTile.blips.remove(model)
                        self.game.selectedTile = self.game.get_tile(self.game.selectedTile.x + self.game.selectedTile.face[0], self.game.selectedTile.y + self.game.selectedTile.face[1])
                        self.game.selectedTile.occupand = self.game.selectedModel
                        self.game.selectedTile.isOccupied = True
                        self.gameStateManager.run_gamestate()
                    else:
                        print("Cannot move onto the board, Tile is occupied!")
                        self.game.reset_select()
                        self.gameStateManager.run_gamestate(("gsTurn"))
                else: 
                    self.game.reset_select()
                    self.gameStateManager.run_gamestate(("gsTurn"))
            
            if self.end_button.draw(self.gameStateManager.screen):
                self.game.reset_select()
                self.gameStateManager.run_gamestate("gsTurn")

class smTurning:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game

    def run_thread(self):
        while self.gameStateManager.runThread:
            self.gameStateManager.run_map_turning()

    def run(self):
        startFace = self.game.selectedModel.face
        turnAmount = 0
        self.gameStateManager.runThread = True
        thread = threading.Thread(target=self.run_thread,args=())
        thread.start()

        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.amount_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.right_button = Button(810, 500, self.place_image, 1)
        self.left_button = Button(810, 600, self.amount_image, 1)
        self.accept_button = Button(810, 700, self.amount_image, 1)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateManager.runThread = False
                    thread.join()
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
                    pygame.display.update()

            if self.left_button.draw(self.gameStateManager.screen):
                turnAmount += 1
                self.game.turn_model(self.game.selectedModel, "left")
                self.gameStateManager.screen.fill("black")

            if self.right_button.draw(self.gameStateManager.screen):
                turnAmount -= 1
                self.game.turn_model(self.game.selectedModel, "right")
                self.gameStateManager.screen.fill("black")

            if self.accept_button.draw(self.gameStateManager.screen):
                if turnAmount == 0:
                    pass

                elif turnAmount < 0:
                    cost = abs(turnAmount) % 4
                    match cost:
                        case 0:
                            pass

                        case 1:
                            if self.game.cp + self.game.selectedModel.AP > 0:
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
                                self.gameStateManager.freeShot = True
                            else:
                                print("Not enough AP/CP!")
                                self.game.turn_model(self.game.selectedModel, "left")

                        case 2:
                            if self.game.cp + self.game.selectedModel.AP > 1:
                                self.game.reduce_ap_sm(self.game.selectedModel, 2)
                                self.gameStateManager.freeShot = True
                            else:
                                print("Not enough AP/CP!")
                                self.game.turn_model(self.game.selectedModel, "full")

                        case 3:
                            if self.game.cp + self.game.selectedModel.AP > 0:
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
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
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
                                self.gameStateManager.freeShot = True
                            else:
                                print("Not enough AP/CP!")
                                self.game.turn_model(self.game.selectedModel, "right")
                                

                        case 2:
                            if self.game.cp + self.game.selectedModel.AP > 1:
                                self.game.reduce_ap_sm(self.game.selectedModel, 2)
                                self.gameStateManager.freeShot = True
                            else:
                                print("Not enough AP/CP!")
                                self.game.turn_model(self.game.selectedModel, "full")

                        case 3:
                            if self.game.cp + self.game.selectedModel.AP > 0:
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
                                self.gameStateManager.freeShot = True
                            else:
                                print("Not enough AP/CP!")
                                self.game.turn_model(self.game.selectedModel, "left")

                self.gameStateManager.runThread = False
                self.gameStateManager.screen.fill("black")
                print(self.game.selectedModel.AP)
                self.gameStateManager.run_gamestate("smAction")

                #implement switch to action menu!
            pygame.display.update()

class gsTurning:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game

    def run_thread(self):
        while self.gameStateManager.runThread:
            self.gameStateManager.run_map_turning()

    def run(self):
        startFace = self.game.selectedModel.face
        turnAmount = 0
        self.gameStateManager.runThread = True
        thread = threading.Thread(target=self.run_thread,args=())
        thread.start()

        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.amount_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.right_button = Button(810, 500, self.place_image, 1)
        self.left_button = Button(810, 600, self.amount_image, 1)
        self.accept_button = Button(810, 700, self.amount_image, 1)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateManager.runThread = False
                    thread.join()
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
                    pygame.display.update()

            if self.left_button.draw(self.gameStateManager.screen):
                turnAmount += 1
                self.game.turn_model(self.game.selectedModel, "left")
                self.gameStateManager.screen.fill("black")

            if self.right_button.draw(self.gameStateManager.screen):
                turnAmount -= 1
                self.game.turn_model(self.game.selectedModel, "right")
                self.gameStateManager.screen.fill("black")

            if self.accept_button.draw(self.gameStateManager.screen):
                if turnAmount == 0:
                    pass

                elif turnAmount < 0:
                    cost = abs(turnAmount) % 4
                    match cost:
                        case 0:
                            pass

                        case 1:
                            if self.gameStateManager.freeTurn:
                                pass
                            elif self.game.selectedModel.AP > 0:
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
                                self.gameStateManager.freeMove = True
                            else:
                                print("Not enough AP/CP!")
                                self.game.turn_model(self.game.selectedModel, "left")

                        case 2:
                            if self.game.selectedModel.AP > 0:
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
                            else:
                                print("Not enough AP/CP!")
                                self.game.turn_model(self.game.selectedModel, "full")

                        case 3:
                            if self.gameStateManager.freeTurn:
                                pass
                            if self.game.selectedModel.AP > 0:
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
                                self.gameStateManager.freeMove = True
                            else:
                                print("Not enough AP/CP!")
                                self.game.turn_model(self.game.selectedModel, "right")

                elif turnAmount > 0:
                    cost = abs(turnAmount) % 4
                    match cost:
                        case 0:
                            pass

                        case 1:
                            if self.gameStateManager.freeTurn == True:
                                pass
                            elif self.game.selectedModel.AP > 0:
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
                                self.gameStateManager.freeMove = True
                            else:
                                print("Not enough AP/CP!")
                                self.game.turn_model(self.game.selectedModel, "right")
                                

                        case 2:
                            if self.game.selectedModel.AP > 0:
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
                            else:
                                print("Not enough AP/CP!")
                                self.game.turn_model(self.game.selectedModel, "full")

                        case 3:
                            if self.gameStateManager.freeTurn:
                                pass
                            elif self.game.selectedModel.AP > 0:
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
                                self.gameStateManager.freeMove = True
                            else:
                                print("Not enough AP/CP!")
                                self.game.turn_model(self.game.selectedModel, "left")

                self.gameStateManager.runThread = False
                self.gameStateManager.screen.fill("black")
                print(self.game.selectedModel.AP)
                self.gameStateManager.run_gamestate("smAction")

                #implement switch to action menu!
            pygame.display.update()

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

class MeleeDiceRollDoor:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game
        self.dice_1 = Dice(10,10)
        self.dice_2 = Dice(110, 10)
        self.dice_3 = Dice(210, 10)
    
    def run(self):
        roll_1 = 0
        roll_2 = 0
        roll_3 = 0
        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.amount_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.accept_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.psyup_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.psydown_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.rollagain_button = Button(810, 600, self.amount_image, 1)
        self.accept_button = Button(410, 700, self.accept_image, 1)
        self.psyup_button = Button(410, 100, self.psyup_image, 1)
        self.psydown_button = Button(410, 160, self.psydown_image, 1)

        selectedDice = None
        psyPoints = 0

        diceList = []

        if self.game.isPlaying == self.game.player1:
            if self.game.selectedModel.weapon == "Lightningclaws":
                diceList.append(self.dice_1)
                diceList.append(self.dice_2)
            else:
                diceList.append(self.dice_1)

        elif self.game.isPlaying == self.game.player2:
            diceList.append(self.dice_1)
            diceList.append(self.dice_2)
            diceList.append(self.dice_3)

        a = True
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.gameStateManager.screen.fill("Black")  #replace with semi Transparent blit

            if a:
                for dice in diceList:
                    dice.roll_dice(self.gameStateManager.screen)
                    if self.dice_1 in diceList:
                        roll_1 = self.dice_1.face
                    if self.dice_2 in diceList:
                        roll_2 = self.dice_2.face
                    if self.dice_3 in diceList:
                        roll_3 = self.dice_3.face
                a = False

            for dice in diceList:
                if dice.show_result(self.gameStateManager.screen):
                    selectedDice = dice
                    print(selectedDice)

            if self.game.isPlaying == self.game.player1:
                if self.game.selectedModel.weapon == "Axe":

                    if self.psyup_button.draw(self.gameStateManager.screen):
                        if psyPoints <= self.game.psyPoints:
                            psyPoints += 1
                            if self.game.melee_door(self.game.selectedModel, roll_1, roll_2, roll_3, psyPoints):
                                print("success")

                    if self.psydown_button.draw(self.gameStateManager.screen):
                        if psyPoints > 0:
                            psyPoints -= 1
                            if self.game.melee_door(self.game.selectedModel, roll_1, roll_2, roll_3, psyPoints):
                                print("success")

            if self.accept_button.draw(self.gameStateManager.screen):
                self.game.psyPoints -= psyPoints
                print(self.game.psyPoints)
                if self.game.melee_door(self.game.selectedModel, roll_1, roll_2, roll_3, psyPoints):
                    self.game.map.append(self.game.clickedTile.get_destroyed())

                print(game.selectedModel)
                print(game.clickedModel)   
                self.gameStateManager.screen.fill("black")

                if self.game.isPlaying == self.game.player1:
                    self.gameStateManager.run_gamestate("smAction")
                else:
                    self.gameStateManager.run_gamestate()

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