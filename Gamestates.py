from Models import *
from Board import *
from Game import * 

class GameStateManager:     #class to manage interactions between gamestates and provide a schared game object and storage
    def __init__(self, game, screen) -> None:
        self.game = game
        self.screen = screen
        self.gamestates = {"smTurning": smTurning(self, self.game), "main":gamestateMain(self, self.game), "gsPlace": PlaceBL(self, self.game), "mlRoll": MeleeDiceRoll(self, self.game), "smPlace": PlaceSM(self, self.game)}
        self.runThread = True

    def run_gamestate(self, gameState):     #method for executing the run methods of the individual gamestates
        self.gamestates[gameState].run()

    def run_map_command(self):      #method for showing the map in the commandphase
        for tile in self.game.map:
            tile.render()

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

    def run_map_smPlace(self):      #method for showing the map during the Space Marine placement
        for tile in self.game.map:
            if tile.button.draw(self.screen):
                if isinstance(tile, ControlledArea):
                    self.game.selectedTile = tile
                    print(self.game.selectedTile)
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
                self.gameStateManager.run_gamestate("smTurning")

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

    def run_threat(self):
        while self.gameStateManager.runThread == True:
            self.gameStateManager.run_map_smPlace()

    def run(self):
        self.smList = self.game.smModelList
        finished = False
        # self.gameStateManager.runThread = True
        # thread = threading.Thread(target=self.run_threat,args=())
        # thread.start()

        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.amount_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.place_button = Button(810, 500, self.place_image, 1)
        self.right_button = Button(810, 600, self.amount_image, 1)
        self.left_button = Button(810, 700, self.amount_image, 1)
        self.accept_button = Button(810, 800, self.amount_image, 1)

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
                    pygame.display.update()

            if self.smList.__len__() > 0:
                if self.place_button.draw(self.gameStateManager.screen):
                    if isinstance(self.game.selectedTile, ControlledArea):
                        if self.game.selectedTile.isOccupied == False:
                            a = self.smList.pop(0)
                            self.game.selectedTile.occupand = a
                            self.game.selectedTile.isOccupied = True
                            self.game.selectedModel = a
                        else:
                            print("Chose an unoccupied Tile!")
                    else:
                        print("Can't Place Model there, please select valid Entrypoint!")
            
            else:
                if self.accept_button.draw(self.gameStateManager.screen):
                    self.gameStateManager.runThread = False
                    # thread.join()
                    for tile in self.game.map:
                        if isinstance(tile, ControlledArea):
                            tile.convert_to_tile()
                    self.gameStateManager.screen.fill("black")
                    self.gameStateManager.run_gamestate('gsPlace')

            if self.game.selectedModel != None:
                if self.left_button.draw(self.gameStateManager.screen):
                    self.game.turn_model( self.game.selectedModel, "left")
                    self.gameStateManager.screen.fill("black")

                if self.right_button.draw(self.gameStateManager.screen):
                    self.game.turn_model( self.game.selectedModel, "right")
                    self.gameStateManager.screen.fill("black")

            if self.smList.__len__() == 0 and finished == False:
                finished = True
                self.gameStateManager.screen.fill("black")
            
            for tile in self.game.map:
                if tile.button.draw(self.gameStateManager.screen):
                    if isinstance(tile, ControlledArea):
                        self.game.selectedTile = tile
                        print(self.game.selectedTile)
                tile.render(self.gameStateManager.screen)

            pygame.display.update()

class commandPhase:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game
        self.dice = Dice(800, 600)
        self.roll = int

    def run_thread(self):
        while self.gameStateManager.runThread:
            self.gameStateManager.run_map_command()

    def run(self):
        reroll = False
        for model in self.game.smModelList:
            if model.rank == "sergant":
                reroll = True

        self.dice.roll_dice(self.gameStateManager.screen)
        self.roll = self.dice.face
        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.amount_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.reroll_button = Button(810, 500, self.place_image, 1)
        self.accept_button = Button(810, 600, self.amount_image, 1)

        self.gameStateManager.runThread = True
        thread = threading.Thread(target=self.run_threat,args=())
        thread.start()

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

            if reroll:
                if self.reroll_button.draw(self.gameStateManager.screen):
                    self.dice.roll_dice(self.gameStateManager.screen)
                    roll = self.dice.face

            if self.accept_button.draw(self.gameStateManager.screen):
                self.game.CP = roll
                self.gameStateManager.runThread = False
                thread.join()
                self.gameStateManager.screen.fill("black")
                self.gameStateManager.runstate("") #input the run State for SM

class smAction:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game

    def run_thread(self):
        while self.gameStateManager.runThread:
            self.gameStateManager.run_map_smTurn()
            
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
        self.accept_button = Button(810, 400, self.amount_image, 1)


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

            if self.move_button.draw(self.gameStateManager.screen):
                pass
            


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
                            else:
                                print("Not enough AP/CP!")
                                self.game.selectedModel.face = startFace

                        case 2:
                            if self.game.cp + self.game.selectedModel.AP > 1:
                                self.game.reduce_ap_sm(self.game.selectedModel, 2)
                            else:
                                print("Not enough AP/CP!")
                                self.game.selectedModel.face = startFace

                        case 3:
                            if self.game.cp + self.game.selectedModel.AP > 0:
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
                            else:
                                print("Not enough AP/CP!")
                                self.game.selectedModel.face = startFace

                elif turnAmount > 0:
                    cost = abs(turnAmount) % 4
                    match cost:
                        case 0:
                            pass

                        case 1:
                            if self.game.cp + self.game.selectedModel.AP > 0:
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
                            else:
                                print("Not enough AP/CP!")
                                self.game.selectedModel.face = startFace

                        case 2:
                            if self.game.cp + self.game.selectedModel.AP > 1:
                                self.game.reduce_ap_sm(self.game.selectedModel, 2)
                            else:
                                print("Not enough AP/CP!")
                                self.game.selectedModel.face = startFace

                        case 3:
                            if self.game.cp + self.game.selectedModel.AP > 0:
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
                            else:
                                print("Not enough AP/CP!")
                                self.game.selectedModel.face = startFace
                    
                self.gameStateManager.screen.fill("black")
                print(self.game.selectedModel.AP)

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
                            if self.game.cp + self.game.selectedModel.AP > 0:
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
                            else:
                                print("Not enough AP/CP!")
                                self.game.selectedModel.face = startFace

                        case 2:
                            if self.game.cp + self.game.selectedModel.AP > 1:
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
                            else:
                                print("Not enough AP/CP!")
                                self.game.selectedModel.face = startFace

                        case 3:
                            if self.game.cp + self.game.selectedModel.AP > 0:
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
                            else:
                                print("Not enough AP/CP!")
                                self.game.selectedModel.face = startFace

                elif turnAmount > 0:
                    cost = abs(turnAmount) % 4
                    match cost:
                        case 0:
                            pass

                        case 1:
                            if self.game.cp + self.game.selectedModel.AP > 0:
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
                            else:
                                print("Not enough AP/CP!")
                                self.game.selectedModel.face = startFace

                        case 2:
                            if self.game.cp + self.game.selectedModel.AP > 1:
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
                            else:
                                print("Not enough AP/CP!")
                                self.game.selectedModel.face = startFace

                        case 3:
                            if self.game.cp + self.game.selectedModel.AP > 0:
                                self.game.reduce_ap_sm(self.game.selectedModel, 1)
                            else:
                                print("Not enough AP/CP!")
                                self.game.selectedModel.face = startFace
                    
                self.gameStateManager.screen.fill("black")
                print(self.game.selectedModel.AP)

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
                self.gameStateManager.run_gamestate("gsPlace")
            pygame.display.update()
            
pygame.init()
game = Game()
# wall = Wall("Pictures/Tiles/Floor_1.png",1,1)
# entry = EntryPoint("Pictures/Tiles/Floor_1.png",4,4)
# game.map.append(entry)
# game.map.append(wall)

screen = pygame.display.set_mode((900,900))
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