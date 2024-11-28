from Models import *
from Board import *
from Game import *
import pygame.docs 

class GameStateManager:     #class to manage interactions between gamestates and provide a shared game object and storage
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
                           "mlRollDoorSM": MeleeDiceRollDoorSM(self, self.game),
                           "mlRollDoorGS": MeleeDiceRollDoorGS(self, self.game),
                           "mlRollSM": MeleeDiceRollSM(self, self.game),
                           "mlRollGS": MeleeDiceRollGS(self, self.game),
                           "smPlace": PlaceSM(self, self.game),
                           "shoot": Shoot(self, self.game),
                           "shootflamer": ShootFlamer(self, self.game)}
        self.runThread = True   #depricated
        self.overwatchAction = None

        self.freeShot = False   #if sm has free shoot Action and doesn't need to pay the AP for shooting
        self.freeTurn = False   #if gs has a free turn and doesn't need to expend AP for turning 90°

    def run_gamestate(self, gameState):     #method for executing the run methods of the individual gamestates saved in self.gamestates
        self.gamestates[gameState].run()

    def refresh(self):
        for tile in self.game.map:
            tile.render(self.screen)
        pygame.display.flip()


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
            logger.debug(f"Chosen position in blipSack: {choice}")
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
                logger.debug(f"Current Bliplist: {self.blipList}")
                logger.debug(f"Blips in the clicked Tile: {game.clickedTile.blips}")
            else:
                logger.debug("Too many blips outside the area!")
        else:
            #normally trow error to display for player to see
            logger.warning("Non Entrypoint Tile clicked!")

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

        logger.info(f"Current GameState: blStart")

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
                                    logger.debug(f"Blips on clicked Tile: {tile.blips}")  


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
        numb = 0
        for tile in self.game.map:
            if isinstance(tile, EntryPoint):
                numb += (3 - tile.blips.__len__())
        logger.debug(f"Amount of free Entrypoints: {numb}")
        if numb == 0:
            logger.debug(f"Skipping blPlace since there are no free Entrypoints")
            self.gameStateManager.run_gamestate('gsTurn')
        x = 0
        while x < self.BLAmount and x < numb:
            choice = random.randint(0, self.game.blipSack.__len__() - 1)
            logger.debug(f"Chosen position in blipSack: {choice}")
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
                logger.debug(f"Current Bliplist: {self.blipList}")
                logger.debug(f"Blips in the clicked Tile: {game.clickedTile.blips}")
            else:
                print(f"Too many blips outside the area!")
        else:
            #normally trow error to display for player to see
            logger.warning(f"Non Entrypoint Tile clicked!")

    def endState(self):
        for model in self.game.gsModelList:
            model.AP = 6
        for model in self.game.blModelList:
            model.AP = 6
            #set AP = 0 and lurking true if sm in proximity
        self.game.reset_select()
        self.game.reset_clicked()
        self.gameStateManager.screen.fill("black")
        self.gameStateManager.run_gamestate('gsTurn')

    def run(self):
        self.BLAmount = self.game.reinforcement
        #need to implement refilling of the game.blipsack
        self.take_blips()

        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)
        
        self.place_button.draw(self.gameStateManager.screen)
        self.amount_button.draw(self.gameStateManager.screen)

        pygame.display.flip()

        logger.info(f"Current GameState: blStart")

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
                                    logger.debug(f"Blips on clicked Tile: {tile.blips}")  


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
                logger.warning(f"Occupied Tile chosen!")
        else:
            logger.warning(f"Non ControlledArea Tile clicked!")
        
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

        logger.info("Current GameState: placeSM")

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
                            if isinstance(tile, ControlledArea):
                                if tile.button.rect.collidepoint(pygame.mouse.get_pos()):
                                    self.game.selectedTile = tile  
                                    if tile.isOccupied:
                                        self.game.selectedModel = tile.occupand
                                    


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
        logger.info("Current GameState: Command")

        reroll = False
        for model in self.game.smModelList:
            model.AP = 4
            model.overwatch = False
            model.guard = False
            model.jam = False
            model.susf = False

            if model.rank == "sergant":
                reroll = True
                logger.debug(f"Sergant model: {model} present")
                logger.debug(f"Reroll of CP: {reroll}")

        for tile in self.game.map:
            if isinstance(tile, Tile):
                if tile.isBurning:
                    tile.isBurning = False
                    tile.change_picture(tile.picturePath)
            tile.render(self.gameStateManager.screen)

        self.accept_button.draw(self.gameStateManager.screen)
        if reroll:
            self.reroll_button.draw(self.gameStateManager.screen)

        pygame.display.flip()
                
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
                        if self.reroll_button.rect.collidepoint(pygame.mouse.get_pos()):    
                            self.dice.roll_dice(self.gameStateManager.screen)
                            self.roll = self.dice.face
                            reroll = False
                            pygame.draw.rect(self.gameStateManager.screen, 'black', self.reroll_button.rect)
                            pygame.display.update(self.reroll_button.rect)

                    if self.accept_button.rect.collidepoint(pygame.mouse.get_pos()):
                        self.game.cp = self.roll
                        logger.debug(f"CP: {self.game.cp}")
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
            
    def check_ranged(self):
        if isinstance(self.game.clickedTile,  Tile):
            if ((((self.game.clickedModel != None) and (self.game.clickedModel in self.game.gsModelList))  or (self.game.selectedModel.weapon == "Flamer") or (isinstance(self.game.clickedTile, Door) and self.game.selectedModel.weapon != "Flamer"))) and (self.game.clickedTile in game.check_vision(self.game.selectedModel, self.game.selectedTile)):
                if self.game.selectedModel.weapon != "Lightningclaws" and self.game.selectedModel.weapon != "Thunderhammer":
                    return True
            else:
                logger.debug(f"check_ranged error")
        else:
            logger.debug(f"ClickedTile is None!")

        return False
            
    def check_door(self):
        face = self.game.selectedModel.face
        if isinstance(self.game.clickedTile, Door):
            if ((self.game.selectedTile.x + face[0] == self.game.clickedTile.x) and (face[0] != 0)) or ((self.game.selectedTile.y + face[1] == self.game.clickedTile.y) and (face[1] != 0)):
                logger.info(f"Door")
                for tile in self.game.map:
                    if ((tile.x + 1 == self.game.clickedTile.x) or (tile.x - 1 == self.game.clickedTile.x) or (tile.x == self.game.clickedTile.x)) and ((tile.y + 1 == self.game.clickedTile.y) or (tile.y - 1 == self.game.clickedTile.y) or (tile.y == self.game.clickedTile.y)):
                        if isinstance(tile, Tile):
                            if tile.isBurning:
                                return False
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
            self.game.cp -= (amount - self.game.selectedModel.AP)
            self.game.selectedModel.AP = 0

    def move_model(self):

        if self.game.clickedTile.isBurning:
            self.gameStateManager.screen.fill('black')
            pygame.display.flip()
            dice = Dice(100, 10)
            dice.roll_dice(self.gameStateManager.screen)
            result = dice.face
            logger.debug(f"Flamerroll: {result}")
            if result == 1:
                for tile in self.game.map:
                    tile.render(self.gameStateManager.screen)

                self.move_button.draw(self.gameStateManager.screen)
                self.turn_button.draw(self.gameStateManager.screen)
                self.guard_button.draw(self.gameStateManager.screen)
                if self.game.clickedTile != None:
                    if self.check_melee():
                        self.melee_button.draw(self.gameStateManager.screen)
                self.shoot_button.draw(self.gameStateManager.screen)
                self.accept_button.draw(self.gameStateManager.screen)
                if self.check_door():
                    self.interact_button.draw(self.gameStateManager.screen)
                # self.overwatch_button.draw(self.gameStateManager.screen)

                pygame.display.flip()

            else:
                self.game.selectedTile.isOccupied = False
                self.game.selectedTile.occupand = None
                self.game.smModelList.remove(self.game.selectedModel)
                self.game.reset_select()
                self.game.reset_clicked()
                self.gameStateManager.screen.fill('black')
                self.gameStateManager.run_gamestate('smTurn')

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
        self.gameStateManager.freeShot = True
        self.game.selectedModel.guard = False
        self.game.selectedModel.overwatch = False
        self.game.selectedModel.susf = False
            
    def run(self):
        logger.info("Current GameState: smAction")
        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)

        self.move_button.draw(self.gameStateManager.screen)
        self.turn_button.draw(self.gameStateManager.screen)
        self.guard_button.draw(self.gameStateManager.screen)
        if self.game.clickedTile != None:
            if self.check_melee():
                self.melee_button.draw(self.gameStateManager.screen)
        self.shoot_button.draw(self.gameStateManager.screen)
        self.accept_button.draw(self.gameStateManager.screen)
        if self.check_door():
            self.interact_button.draw(self.gameStateManager.screen)
        # self.overwatch_button.draw(self.gameStateManager.screen)

        pygame.display.flip()

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
                    self.guard_button.draw(self.gameStateManager.screen)
                    if self.game.clickedTile != None:
                        if self.check_melee():
                            self.melee_button.draw(self.gameStateManager.screen)
                    self.shoot_button.draw(self.gameStateManager.screen)
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
                                self.game.selectedModel.guard = False
                                self.game.selectedModel.overwatch = False
                                self.game.selectedModel.susf = False
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

                    elif self.guard_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.game.selectedModel.AP + self.game.cp > 1:
                            self.game.selectedModel.guard = True
                            self.game.selectedModel.overwatch = False
                            self.reduce_ap(2)
                            logger.debug(f"Guard == {self.game.selectedModel.guard}")

                    elif self.accept_button.rect.collidepoint(pygame.mouse.get_pos()):
                        self.game.selectedModel.AP = 0
                        self.game.selectedModel.susf = False
                        self.game.reset_select()
                        self.game.reset_clicked()
                        self.gameStateManager.screen.fill("black")
                        self.gameStateManager.run_gamestate("smTurn")

                    elif self.melee_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.game.selectedModel.AP + self.game.cp != 0:
                            if self.game.clickedTile != None:
                                self.reduce_ap(1)
                                if self.check_melee():
                                    if self.game.clickedTile.isOccupied == False:
                                        self.gameStateManager.screen.fill("Black")  #replace with semi Transparent blit
                                        self.game.selectedModel.guard = False
                                        self.game.selectedModel.overwatch = False
                                        self.game.selectedModel.susf = False
                                        self.gameStateManager.run_gamestate("mlRollDoorSM")                                   
                                    else:
                                        self.gameStateManager.screen.fill('black')                                    
                                        self.game.selectedModel.guard = False
                                        self.game.selectedModel.overwatch = False
                                        self.game.selectedModel.susf = False
                                        self.gameStateManager.run_gamestate("mlRollSM")

                    elif self.shoot_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.check_ranged():
                            if (self.game.selectedModel.weapon == "Thunderhammer") or (self.game.selectedModel.weapon == "Lightningclaws"):
                                pass
                            elif (self.game.selectedModel.weapon == "Flamer") and (self.game.selectedModel.AP + self.game.cp > 1) and (self.game.flamerAmmo != 0) and (self.game.check_path(self.game.selectedTile, self.game.clickedTile, 12)):
                                self.gameStateManager.screen.fill('black')
                                self.gameStateManager.run_gamestate('shootflamer')
                            elif ((self.game.selectedModel.weapon != "Flamer") and ((self.game.selectedModel.AP + self.game.cp > 0) or (self.gameStateManager.freeShot))):
                                self.gameStateManager.screen.fill('black')
                                pygame.display.flip()
                                self.gameStateManager.run_gamestate('shoot')

                    else:
                        for tile in self.game.map:
                            if isinstance(tile, Tile):
                                if tile.button.rect.collidepoint(pygame.mouse.get_pos()):
                                    if tile != self.game.selectedTile:
                                        self.game.clickedTile = tile
                                        if self.check_door():
                                            if tile.isOpen == False:
                                                if self.check_melee():
                                                    pygame.draw.rect(self.gameStateManager.screen, 'black', self.melee_button.rect)
                                                    self.melee_button.draw(self.gameStateManager.screen)
                                                    pygame.display.update(self.melee_button.rect)
                                                pygame.draw.rect(self.gameStateManager.screen, 'black', self.interact_button.rect)
                                                self.interact_button.draw(self.gameStateManager.screen)
                                                pygame.display.update(self.interact_button.rect)
                                        else:
                                            pygame.draw.rect(self.gameStateManager.screen, 'black', self.melee_button.rect)
                                            pygame.display.update(self.melee_button.rect)
                                            pygame.draw.rect(self.gameStateManager.screen, 'black', self.interact_button.rect)
                                            pygame.display.update(self.interact_button.rect)

                                        print(tile)
                                        if tile.isOccupied:
                                            if isinstance(tile.occupand, Genestealer):
                                                self.game.clickedModel = tile.occupand
                                                if self.check_melee():
                                                    pygame.draw.rect(self.gameStateManager.screen, 'black', self.melee_button.rect)
                                                    self.melee_button.draw(self.gameStateManager.screen)
                                                    pygame.display.update(self.melee_button.rect)
          

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
        self.gameStateManager.freeShot = False

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
            self.game.cp -= (amount - self.game.selectedModel.AP)
            self.game.selectedModel.AP = 0

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
                                        self.game.selectedModel.guard = False
                                        self.game.selectedModel.overwatch = False
                                        self.gameStateManager.freeShot = True
                                        self.game.selectedModel.susf = False
                                    else:
                                        print("Not enough AP/CP!")
                                        self.game.turn_model(self.game.selectedModel, "left")

                                case 2:
                                    if self.game.cp + self.game.selectedModel.AP > 1:
                                        self.reduce_ap(2)
                                        self.gameStateManager.freeShot = True                     
                                        self.game.selectedModel.guard = False
                                        self.game.selectedModel.overwatch = False
                                        self.game.selectedModel.susf = False
                                    else:
                                        print("Not enough AP/CP!")
                                        self.game.turn_model(self.game.selectedModel, "full")

                                case 3:
                                    if self.game.cp + self.game.selectedModel.AP > 0:
                                        self.reduce_ap(1)
                                        self.gameStateManager.freeShot = True                     
                                        self.game.selectedModel.guard = False
                                        self.game.selectedModel.overwatch = False
                                        self.game.selectedModel.susf = False
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
                                        self.game.selectedModel.guard = False
                                        self.game.selectedModel.overwatch = False
                                        self.game.selectedModel.susf = False
                                    else:
                                        print("Not enough AP/CP!")
                                        self.game.turn_model(self.game.selectedModel, "right")
                                        

                                case 2:
                                    if self.game.cp + self.game.selectedModel.AP > 1:
                                        self.reduce_ap(2)
                                        self.gameStateManager.freeShot = True                     
                                        self.game.selectedModel.guard = False
                                        self.game.selectedModel.overwatch = False
                                        self.game.selectedModel.susf = False
                                    else:
                                        print("Not enough AP/CP!")
                                        self.game.turn_model(self.game.selectedModel, "full")

                                case 3:
                                    if self.game.cp + self.game.selectedModel.AP > 0:
                                        self.reduce_ap(1)
                                        self.gameStateManager.freeShot = True                     
                                        self.game.selectedModel.guard = False
                                        self.game.selectedModel.overwatch = False
                                        self.game.selectedModel.susf = False
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
            self.game.cp -= (amount - self.game.selectedModel.AP)
            self.game.selectedModel.AP = 0
    
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

                    
                    if (self.game.selectedModel.AP + self.game.cp != 0) and (self.melee_door(roll_1,roll_2,psyPoints) == False):
                        if self.rollAgain_button.rect.collidepoint(pygame.mouse.get_pos()):
                            self.reduce_ap(1)
                            self.gameStateManager.screen.fill('black')
                            self.gameStateManager.run_gamestate("mlRollDoorSM")


class MeleeDiceRollSM:
    def __init__(self, gameStateManager, game) -> None:
        self.game = game
        self.gameStateManager = gameStateManager
        self.dice_1 = Dice(10, 10)
        self.dice_2 = Dice(110, 10)
        self.dice_3 = Dice(210, 10)
        self.dice_4 = Dice(360, 10)
        self.dice_5 = Dice(460,10)
        self.accept_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.reroll_image = pygame.image.load('Pictures/Tiles/Floor_1.png')     
        self.psyup_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.psydown_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.turn_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.accept_button = Button(410,500, self.accept_image, 1)
        self.reroll_button = Button(410,100, self.reroll_image, 1)
        self.psyup_button = Button(410,200, self.psyup_image, 1)
        self.psydown_button = Button(410,300, self.psydown_image, 1)
        self.turn_button = Button(410,400, self.turn_image, 1)

    def melee_model(self, roll_1, roll_2, roll_3, roll_4, roll_5, psypoints = 0):
        attacker = self.game.selectedModel
        defender = self.game.clickedModel
        facing = self.game.is_facing(attacker,defender)

        if attacker.weapon == "Thunderhammer":
            roll_3 = 0
            roll_4 += 2
        if attacker.weapon == "Powersword":
            roll_4 += 1
        if attacker.weapon == "Lightningclaws":
            if roll_4 > roll_5:
                roll_4 +=1
            else:
                roll_5 +=1
        if attacker.weapon == "Axe":
            roll_4 +=1
            roll_4 += psypoints

        if defender.isBroodlord and facing:
            if attacker.weapon != "Thunderhammer":
                if (roll_1 > roll_2 and roll_2 > roll_3) or (roll_3 > roll_2 and roll_2 > roll_1):
                    roll_1 = roll_1 + roll_3
                elif (roll_1 > roll_3 and roll_3 > roll_2) or (roll_2 > roll_3 and roll_3 > roll_1):
                    roll_1 = roll_1 + roll_2
                elif (roll_2 > roll_1 and roll_1 > roll_3) or (roll_3 > roll_1 and roll_1 > roll_2):
                    roll_1 = roll_2 + roll_3
            else:
                roll_1 = roll_1 + roll_2


        if attacker.weapon == "Thunderhammer":
            if roll_1 > roll_4 or roll_2 > roll_4:
                winner = defender
            elif roll_1 == roll_4 or roll_2 == roll_4:
                winner = None
            else:
                winner = attacker
        
        elif attacker.weapon == "Powersword":
            if roll_1 > roll_4 or roll_2 > roll_4 or roll_3 > roll_4:
                winner = defender
            elif roll_1 == roll_4 or roll_2 == roll_4 or roll_3 == roll_4:
                winner = None
            else:
                winner = attacker

        elif attacker.weapon == "Lightningclaws":
            defenderRoll = max(roll_1,roll_2,roll_3)
            attackerRoll = max(roll_4,roll_5)

            if defenderRoll > attackerRoll:
                return defender
            elif attackerRoll > defenderRoll:
                return attacker
            else:
                return None

        elif attacker.weapon == "Axe":
            if roll_1 > roll_4 or roll_2 > roll_4 or roll_3 > roll_4:
                winner = defender
            elif roll_1 == roll_4 or roll_2 == roll_4 or roll_3 == roll_4:
                winner = None
            else:
                winner = attacker
        
        else:
            if roll_1 > roll_4 or roll_2 > roll_4 or roll_3 > roll_4:
                winner = defender
            elif roll_1 == roll_4 or roll_2 == roll_4 or roll_3 == roll_4:
                winner = None
            else:
                winner = attacker

        return winner  

    def loose(self):
        model = self.game.selectedModel
        self.game.smModelList.remove(model)
        self.game.selectedTile.isOccupied = False
        self.game.selectedTile.occupand = None
        self.game.reset_select()
        self.game.reset_clicked()
        self.gameStateManager.screen.fill('black')
        self.gameStateManager.run_gamestate("smTurn")

    def win(self):
        self.game.gsModelList.remove(self.game.clickedModel)
        self.game.clickedTile.isOccupied = False
        self.game.clickedTile.occupand = None
        self.game.reset_clicked()
        self.gameStateManager.screen.fill('black')
        self.gameStateManager.run_gamestate('smAction')

    def adjust_facing(self):
        attacker = self.game.selectedModel
        defender = self.game.clickedModel
        wantedFace = (attacker.face[0] * (-1), attacker.face[1] * (-1))

        while defender.face != wantedFace:
            game.turn_model(defender, "left")

    def run(self):
        logger.info(f"Current gamestate: mlRollSM")
        roll_1 = 0 
        roll_2 = 0
        roll_3 = 0
        roll_4 = 0
        roll_5 = 0
        diceList = []
        facing = self.game.is_facing(self.game.selectedModel, self.game.clickedModel)
        reroll = False
        if self.game.selectedModel.weapon == "Powersword":
            reroll = True
        psypoints = 0
        turn = False

        self.accept_button.draw(self.gameStateManager.screen)
        self.reroll_button.draw(self.gameStateManager.screen)
        self.turn_button.draw(self.gameStateManager.screen)
        if self.game.selectedModel.weapon == "Axe":
            self.psyup_button.draw(self.gameStateManager.screen)
            self.psydown_button.draw(self.gameStateManager.screen)

        pygame.display.flip()

        diceList.append(self.dice_1)
        diceList.append(self.dice_2)
        self.dice_1.roll_dice(self.gameStateManager.screen)
        roll_1 = self.dice_1.face
        self.dice_2.roll_dice(self.gameStateManager.screen)
        roll_2 = self.dice_2.face

        if self.game.selectedModel.weapon != "Thunderhammer":
            self.dice_3.roll_dice(self.gameStateManager.screen)
            roll_3 = self.dice_3.face
            diceList.append(self.dice_3)

        self.dice_4.roll_dice(self.gameStateManager.screen)
        roll_4 = self.dice_4.face
        diceList.append(self.dice_4)
        if self.game.selectedModel.weapon == "Lightningclaws":
            self.dice_5.roll_dice(self.gameStateManager.screen)
            roll_5 = self.dice_5.face
            diceList.append(self.dice_5)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.accept_button.rect.collidepoint(pygame.mouse.get_pos()):
                        print(self.melee_model(roll_1,roll_2,roll_3,roll_4,roll_5,psypoints))
                        if self.melee_model(roll_1, roll_2,roll_3,roll_4,roll_5,psypoints) == self.game.clickedModel:
                            if facing:
                                self.loose()
                            else:
                                if turn:
                                    self.adjust_facing()
                                self.gameStateManager.screen.fill('black')
                                self.gameStateManager.run_gamestate('smAction')
                        elif self.melee_model(roll_1, roll_2,roll_3,roll_4,roll_5,psypoints) == self.game.selectedModel:
                            self.win()
                        else:
                            if turn:
                                self.adjust_facing()
                            self.gameStateManager.screen.fill('black')
                            self.gameStateManager.run_gamestate('smAction')

                    if self.turn_button.rect.collidepoint(pygame.mouse.get_pos()):
                        turn = not turn
                        print(turn)

                    if reroll and self.reroll_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if roll_1 > roll_2 and roll_1 > roll_3:
                            self.dice_1.roll_dice(self.gameStateManager.screen)
                            roll_1 = self.dice_1.face
                        elif roll_2 > roll_1 and roll_2 > roll_3:
                            self.dice_2.roll_dice(self.gameStateManager.screen)
                            roll_2 = self.dice_2.face
                        elif roll_3 != 0:
                            self.dice_3.roll_dice(self.gameStateManager.screen)
                            roll_3 = self.dice_3.face
                        else:
                            self.dice_1.roll_dice(self.gameStateManager.screen)
                            roll_1 = self.dice_1.face
                        reroll = False

                    if self.game.selectedModel.weapon == "Axe":
                        if self.psyup_button.rect.collidepoint(pygame.mouse.get_pos()):
                            if self.game.psyPoints != 0:
                                psypoints += 1

                        if self.psydown_button.rect.collidepoint(pygame.mouse.get_pos()):
                            if psypoints != 0:
                                psypoints -= 1


class Shoot:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game
        self.dice_1 = Dice(10,10)
        self.dice_2 = Dice(110, 10)
        self.dice_3 = Dice(210, 10)
        self.rollAgain_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.accept_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.rollAgain_button = Button(410, 500, self.rollAgain_image, 1)
        self.accept_button = Button(410, 700, self.accept_image, 1)

    def reduce_ap(self, amount):
        if self.game.selectedModel.AP >= amount:
            self.game.selectedModel.AP -= amount
        else:
            self.game.cp -= (amount - self.game.selectedModel.AP)
            self.game.selectedModel.AP = 0

    def shoot_bolter(self, roll_1, roll_2):
        attacker = self.game.selectedModelModel
        defender = self.game.clickedModel

        if self.gameStateManager.freeShot:
            self.gameStateManager.freeShot == False
        else:
            self.reduce_ap(1)

        if attacker.susf:
            roll_1 += 1
            roll_2 += 1
        else:
            attacker.susf = True

        if defender.isBroodlord == False:
            if roll_1 > 5 or roll_2 > 5:
                self.game.clickedTile.isOccupied = False
                self.game.gsModelList.remove(defender)
                self.game.clickedTile.occupand = None
                self.gameStateManager.screen.fill('black')
                self.gameStateManager.run_gamestate('smAction')
            else:
                self.gameStateManager.screen.fill('black')
                self.gameStateManager.run_gamestate("smAction")

        else:
            if roll_1 > 5 and roll_2 > 5:
                self.game.clickedTile.isOccupied = False
                self.game.gsModelList.remove(defender)
                self.game.clickedTile.occupand = None
                self.gameStateManager.screen.fill('black')
                self.gameStateManager.run_gamestate('smAction')
            else:            
                self.gameStateManager.screen.fill('black')
                self.gameStateManager.run_gamestate("smAction")
            
    def shoot_bolter_door(self,roll_1,roll_2):
        attacker = self.game.selectedModel
        if self.gameStateManager.freeShot:
            self.gameStateManager.freeShot == False
        else:
            self.reduce_ap(1)

        if attacker.susf:
            roll_1 += 1
            roll_2 += 1
        else:
            attacker.susf = True

        if roll_1 > 5 or roll_2 > 5:
            self.game.map.remove(self.game.clickedTile)
            newTile = self.game.clickedTile.get_destroyed()
            self.game.map.append(newTile)
            self.game.clickedTile = newTile
            self.gameStateManager.screen.fill('black')
            self.gameStateManager.run_gamestate("smAction")
        else:
            self.gameStateManager.screen.fill('black')
            self.gameStateManager.run_gamestate("smAction")

    def shoot_ac(self, roll_1, roll_2, roll_3):
        attacker = self.game.selectedModelModel
        defender = self.game.clickedModel

        if self.gameStateManager.freeShot:
            self.gameStateManager.freeShot == False
        else:
            self.reduce_ap(1)
        self.game.assaultCannonAmmo -= 1

        if attacker.susf:
            roll_1 += 1
            roll_2 += 1
            roll_3 += 1
        else:
            attacker.susf = True

        if defender.isBroodlord == False:
            if roll_1 > 4 or roll_2 > 4 or roll_3 > 4:
                self.game.clickedTile.isOccupied = False
                self.game.gsModelList.remove(defender)
                self.game.clickedTile.occupand = None
                self.gameStateManager.screen.fill('black')
                self.gameStateManager.run_gamestate('smAction')
            else:
                self.gameStateManager.screen.fill('black')
                self.gameStateManager.run_gamestate("smAction")

        else:
            if (roll_1 > 4 and roll_2 > 4) or (roll_1 > 4 and roll_3 > 4) or (roll_2 > 4 and roll_3 > 4):
                self.game.clickedTile.isOccupied = False
                self.game.gsModelList.remove(defender)
                self.game.clickedTile.occupand = None
                self.gameStateManager.screen.fill('black')
                self.gameStateManager.run_gamestate('smAction')
            else:            
                self.gameStateManager.screen.fill('black')
                self.gameStateManager.run_gamestate("smAction")
            
    def shoot_ac_door(self,roll_1,roll_2, roll_3):
        attacker = self.game.selectedModel
        if self.gameStateManager.freeShot:
            self.gameStateManager.freeShot == False
        else:
            self.reduce_ap(1)
        self.game.assaultCannonAmmo -= 1

        if attacker.susf:
            roll_1 += 1
            roll_2 += 1
            roll_3 += 1
        else:
            attacker.susf = True

        if roll_1 > 4 or roll_2 > 4 or roll_3 >4:
            self.game.map.remove(self.game.clickedTile)
            newTile = self.game.clickedTile.get_destroyed()
            self.game.map.append(newTile)
            self.game.clickedTile = newTile
            self.gameStateManager.screen.fill('black')
            self.gameStateManager.run_gamestate("smAction")
        else:
            self.gameStateManager.screen.fill('black')
            self.gameStateManager.run_gamestate("smAction")

    def run(self):
        logger.info(f"Current Gamestate: smShoot")
        roll_1 = 0
        roll_2 = 0
        roll_3 = 0
        diceList = []
        
        if (self.game.selectedModel.weapon == "Thunderhammer") or (self.game.selectedModel.weapon == "Lightningclaws"):
            logger.error(f"SelectedModel {self.game.selectedModel} has no ranged Weapon!")
            self.gameStateManager.run_gamestate('smAction')

        diceList.append(self.dice_1)
        self.dice_1.roll_dice(self.gameStateManager.screen)
        roll_1 = self.dice_1.face
        diceList.append(self.dice_2)
        self.dice_2.roll_dice(self.gameStateManager.screen)
        roll_2 = self.dice_2.face
        
        if (self.game.selectedModel.weapon == "Assaultcannon"):
            diceList.append(self.dice_3)
            self.dice_3.roll_dice(self.gameStateManager.screen)
            roll_3 = self.dice_3.face

        self.accept_button.draw(self.gameStateManager.screen)
        self.rollAgain_button.draw(self.gameStateManager.screen)

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()  

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.accept_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.game.selectedModel.weapon == "Assaultcannon":
                            if self.game.assaultCannonAmmo > 0:
                                if self.game.clickedTile.isOccupied:
                                    if (self.game.clickedTile.occupand in self.game.gsModelList):
                                        self.shoot_ac(roll_1, roll_2, roll_3)
                                    else:
                                        logger.error(f"Non Genstealer type Object {self.game.clickedTile.occupand} selected as target!")
                                elif isinstance(self.game.clickedTile, Door):
                                    if not self.game.clickedTile.isOpen:
                                        self.shoot_ac_door(roll_1, roll_2, roll_3)
                                    
                            else:
                                logger.debug(f"AssaultcannonAmmo on {self.game.assaultCannonAmmo}")

                        else:
                            if self.game.clickedTile.isOccupied:
                                if (self.game.clickedTile.occupand in self.game.gsModelList):
                                    self.shoot_bolter(roll_1, roll_2)
                                else:
                                    logger.error(f"Non Genstealer type Object {self.game.clickedTile.occupand} selected as target!")
                            elif isinstance(self.game.clickedTile, Door):
                                if not self.game.clickedTile.isOpen:
                                    self.shoot_bolter_door(roll_1, roll_2)

                    if self.rollAgain_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if (self.game.selectedModel.AP + self.game.cp > 0) or self.gameStateManager.freeShot:
                            self.reduce_ap(1)
                            self.game.selectedModel.susf = True
                            self.gameStateManager.screen.fill('black')
                            pygame.display.flip()
                            self.gameStateManager.run_gamestate('shoot')

class ShootFlamer:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game
        self.dice = Dice(100,10)
        self.shoot_image = pygame.image.load("Pictures/Tiles/Floor_1.png")
        self.exit_image = pygame.image.load("Pictures/Tiles/Floor_1.png")
        self.shoot_button = Button(410, 500, self.shoot_image, 1)
        self.exit_button = Button(410, 700, self.exit_image, 1)

    def reduce_ap(self, amount):
        if self.game.selectedModel.AP >= amount:
            self.game.selectedModel.AP -= amount
        else:
            self.game.cp -= (amount - self.game.selectedModel.AP)
            self.game.selectedModel.AP = 0
    
    def shoot_flamer(self, target, dice):
        target.isBurning = True
        save = 0
        if target.isOccupied:
            #add method to highlight the target
            dice.roll_dice(self.gameStateManager.screen)
            save = dice.face
            logger.info(f"Flamerroll: {save}")
            if save == 1:
                pass
            else:
                target.isOccupied = False
                if target.occupand in self.game.smModelList:
                    self.game.smModelList.remove(target.occupand)
                elif target.occupand in self.game.gsModelList:
                    self.game.gsMoelList.remove(target.occupand)
                elif target.occupand in self.game.blModelList:
                    self.game.blModelList.remove(target.occupand)
                target.occupand = None
        target.change_picture(target.burningPictureFilePath)

    def run(self):
        logger.info(f"Current Gamestate: smShoot")
        notDoor = True
        
        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)

        self.exit_button.draw(self.gameStateManager.screen)
        self.shoot_button.draw(self.gameStateManager.screen)

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

                    self.exit_button.draw(self.gameStateManager.screen)
                    self.shoot_button.draw(self.gameStateManager.screen)
                    
                    pygame.display.flip()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.shoot_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.game.clickedTile in self.game.check_vision(self.game.selectedModel, self.game.selectedTile):
                            if isinstance(self.game.clickedTile, Door):
                                if not self.game.clickedTile.isOpen:
                                    seenTiles = []
                                    for tile in self.game.map:
                                        if isinstance(tile, Tile):
                                            if tile.sector == self.game.clickedTile.sector:
                                                if tile in self.game.check_vision(self.game.selectedModel, self.game.selectedTile):
                                                    if tile != self.game.clickedTile:
                                                        seenTiles.append(tile)
                                    if seenTiles.__len__() != 0:
                                        pass
                                    else:
                                        notDoor = False
                            
                            if notDoor:
                                self.reduce_ap(2)
                                self.game.flamerAmmo -= 1
                                for tile in self.game.map:
                                    if isinstance(tile, Tile):
                                        if tile.sector == self.game.clickedTile.sector:
                                            if isinstance(tile, Door):
                                                if tile.isOpen == False:
                                                    pass
                                                else:
                                                    self.shoot_flamer(tile, self.dice) 
                                            else:
                                                self.shoot_flamer(tile, self.dice) 
                                self.gameStateManager.screen.fill('black')
                                self.game.reset_clicked()
                                if self.game.selectedModel in self.game.smModelList:
                                    self.gameStateManager.run_gamestate('smAction')
                                else:
                                    self.game.reset_select()
                                    self.gameStateManager.run_gamestate('smTurn')

                    elif self.exit_button.rect.collidepoint(pygame.mouse.get_pos()):
                        self.gameStateManager.screen.fill('black')
                        self.gameStateManager.run_gamestate('smAction')

                    else:
                        for tile in self.game.map:
                            if tile.button.rect.collidepoint(pygame.mouse.get_pos()):
                                if tile in self.game.check_vision(self.game.selectedModel, self.game.selectedTile):
                                    if self.game.check_path(self.game.selectedTile, tile, 12):
                                        self.game.clickedTile = tile
                                        logger.info(f"ClickedTile: {self.game.clickedTile}")

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

        if self.game.clickedTile.isBurning:
            self.gameStateManager.screen.fill('black')
            pygame.display.flip()
            dice = Dice(100, 10)
            dice.roll_dice(self.gameStateManager.screen)
            result = dice.face
            logger.debug(f"Flamerroll: {result}")
            if result == 1:
                for tile in self.game.map:
                    tile.render(self.gameStateManager.screen)

                self.move_button.draw(self.gameStateManager.screen)
                self.turn_button.draw(self.gameStateManager.screen)
                self.guard_button.draw(self.gameStateManager.screen)
                if self.game.clickedTile != None:
                    if self.check_melee():
                        self.melee_button.draw(self.gameStateManager.screen)
                self.shoot_button.draw(self.gameStateManager.screen)
                self.accept_button.draw(self.gameStateManager.screen)
                if self.check_door():
                    self.interact_button.draw(self.gameStateManager.screen)
                # self.overwatch_button.draw(self.gameStateManager.screen)

                pygame.display.flip()

            else:
                self.game.selectedTile.isOccupied = False
                self.game.selectedTile.occupand = None
                self.game.gsModelList.remove(self.game.selectedModel)
                self.game.reset_select()
                self.game.reset_clicked()
                self.gameStateManager.screen.fill('black')
                self.gameStateManager.run_gamestate('gsTurn')

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

        if (self.game.check_overwatch().__len__() != 0):
            logger.info(self.game.check_overwatch())
            gameStateManager.overwatchAction = "move"

    def check_door(self):
        face = self.game.selectedModel.face
        if isinstance(self.game.clickedTile, Door):
            if ((self.game.selectedTile.x + face[0] == self.game.clickedTile.x) and (face[0] != 0)) or ((self.game.selectedTile.y + face[1] == self.game.clickedTile.y) and (face[1] != 0)):
                logger.info(f"Door")
                for tile in self.game.map:
                    if ((tile.x + 1 == self.game.clickedTile.x) or (tile.x - 1 == self.game.clickedTile.x) or (tile.x == self.game.clickedTile.x)) and ((tile.y + 1 == self.game.clickedTile.y) or (tile.y - 1 == self.game.clickedTile.y) or (tile.y == self.game.clickedTile.y)):
                        if isinstance(tile, Tile):
                            if tile.isBurning:
                                return False
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

        logger.info(f"Current gamestate: gsAction")

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

                    elif self.melee_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.game.selectedModel.AP != 0:
                            if self.game.clickedTile != None:
                                if self.check_melee():
                                    if self.game.clickedTile.isOccupied == False:
                                        self.gameStateManager.screen.fill("Black")  #replace with semi Transparent blit
                                        self.gameStateManager.run_gamestate("mlRollDoorGS")
                                    else:
                                        self.gameStateManager.screen.fill("Black")  #replace with semi Transparent blit
                                        self.gameStateManager.run_gamestate("mlRollGS")
                                        
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
        inProximity = True

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

            for tile in self.game.map:
                if ((tile.x == self.game.clickedTile.x + 1) or (tile.x == self.game.clickedTile.x - 1) or (tile.x == self.game.clickedTile.x)) and ((tile.y == self.game.clickedTile.y + 1) or (tile.y == self.game.clickedTile.y - 1) or (tile.y == self.game.clickedTile.y)):
                    if isinstance(tile, Tile):
                        if tile.isOccupied:
                            if tile.occupand in self.game.smModelList:
                                inProximity = False

            if inRange and burning and doorOpen and occupied and seen and inProximity:
                return True
            else:
                return False 

    def check_door(self):
        if isinstance(self.game.clickedTile, Door):
            if((self.game.selectedTile.x == self.game.clickedTile.x + 1) or (self.game.selectedTile.x == self.game.clickedTile.x - 1) or (self.game.selectedTile.x == self.game.clickedTile.x)) and ((self.game.selectedTile.y == self.game.clickedTile.y + 1) or (self.game.selectedTile.y == self.game.clickedTile.y - 1) or (self.game.selectedTile.y == self.game.clickedTile.y)):
                logger.info(f"Door")
                for tile in self.game.map:
                    if ((tile.x + 1 == self.game.clickedTile.x) or (tile.x - 1 == self.game.clickedTile.x) or (tile.x == self.game.clickedTile.x)) and ((tile.y + 1 == self.game.clickedTile.y) or (tile.y - 1 == self.game.clickedTile.y) or (tile.y == self.game.clickedTile.y)):
                        if isinstance(tile, Tile):
                            if tile.isBurning and not self.game.clickedTile.isOpen:
                                return False
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

            if self.game.clickedTile.isBurning:
                self.gameStateManager.screen.fill('black')
                pygame.display.flip()
                dice = Dice(100, 10)
                dice.roll_dice(self.gameStateManager.screen)
                result = dice.face
                logger.debug(f"Flamerroll: {result}")
                if result == 1:
                    for tile in self.game.map:
                        tile.render(self.gameStateManager.screen)

                    self.move_button.draw(self.gameStateManager.screen)
                    self.turn_button.draw(self.gameStateManager.screen)
                    self.guard_button.draw(self.gameStateManager.screen)
                    if self.game.clickedTile != None:
                        if self.check_melee():
                            self.melee_button.draw(self.gameStateManager.screen)
                    self.shoot_button.draw(self.gameStateManager.screen)
                    self.accept_button.draw(self.gameStateManager.screen)
                    if self.check_door():
                        self.interact_button.draw(self.gameStateManager.screen)
                    # self.overwatch_button.draw(self.gameStateManager.screen)

                    pygame.display.flip()

                else:
                    self.game.selectedTile.isOccupied = False
                    self.game.selectedTile.occupand = None
                    self.game.blModelList.remove(self.game.selectedModel)
                    self.game.reset_select()
                    self.game.reset_clicked()
                    self.gameStateManager.screen.fill('black')
                    self.gameStateManager.run_gamestate('gsTurn')

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
        if isinstance(self.game.selectedTile, EntryPoint):
            self.game.selectedTile.blips.remove(self.game.selectedModel)
        #add Broodlord Button here
        self.game.blipReserve.append(self.game.selectedModel.count)
        self.game.blModelList.remove(self.game.selectedModel)
        self.game.selectedModel = gsList.pop(0)
        if isinstance(self.game.selectedTile, Tile):
            self.game.selectedTile.occupand = self.game.selectedModel
            self.game.gsModelList.append(self.game.selectedModel)

        elif isinstance(self.game.selectedTile, EntryPoint):
            self.game.selectedTile.genstealers.append(self.game.selectedModel)
            for model in gsList:
                self.game.selectedTile.genstealers.append(model)
            print(self.game.selectedTile.genstealers)
            self.game.reset_select()
            self.game.reset_clicked()
            self.gameStateManager.screen.fill('black')
            self.gameStateManager.run_gamestate('gsTurn')

        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)

        if isinstance(self.game.selectedTile, Tile):
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

                    if isinstance(self.game.selectedTile, Tile):
                        self.right_button.draw(self.gameStateManager.screen)
                        self.left_button.draw(self.gameStateManager.screen)
                    if hasPlaced:
                        self.accept_button.draw(self.gameStateManager.screen)
                    if hasPlaced == False:
                        self.place_button.draw(self.gameStateManager.screen)
                    
                    pygame.display.flip()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.left_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if isinstance(self.game.selectedTile, Tile):
                            if hasPlaced:
                                self.game.turn_model(self.game.selectedModel, "left")
                                pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.selectedTile.button.rect)
                                self.game.selectedTile.render(self.gameStateManager.screen)
                                pygame.display.update(self.game.selectedTile.button.rect)

                    elif self.right_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if isinstance(self.game.selectedTile, Tile):
                            if hasPlaced:
                                self.game.turn_model(self.game.selectedModel, "right")
                                pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.selectedTile.button.rect)
                                self.game.selectedTile.render(self.gameStateManager.screen)
                                pygame.display.update(self.game.selectedTile.button.rect)

                    elif self.accept_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if gsList.__len__() == 0 or freeTiles.__len__() == 0:                           
                            self.game.gsModelList.append(self.game.selectedModel)
                            self.game.reset_select()
                            self.game.reset_clicked()
                            self.gameStateManager.screen.fill('black')
                            self.gameStateManager.run_gamestate('gsTurn')
                        else:
                            hasPlaced = False  
                            self.game.gsModelList.append(self.game.selectedModel)
                            self.game.selectedModel = gsList.pop(0)
                            if (self.game.selectedTile in freeTiles) and not (isinstance(self.game.selectedTile, EntryPoint)):
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


class MeleeDiceRollDoorGS:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager = gameStateManager
        self.game = game
        self.dice_1 = Dice(10,10)
        self.dice_2 = Dice(110, 10)
        self.dice_3 = Dice(210, 10)
        self.rollAgain_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.accept_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.rollAgain_button = Button(410, 500, self.rollAgain_image, 1)
        self.accept_button = Button(410, 700, self.accept_image, 1)

    def melee_door(self, roll_1, roll_2, roll_3):
        if roll_1 > 5 or roll_2 > 5 or roll_3 > 5:
            return True
    
    def run(self):
        roll_1 = 0
        roll_2 = 0
        roll_3 = 0

        diceList = []

        diceList.append(self.dice_1)
        diceList.append(self.dice_2)
        diceList.append(self.dice_3)
        
        self.accept_button.draw(self.gameStateManager.screen)
        if self.game.selectedModel.AP != 0:
            self.rollAgain_button.draw(self.gameStateManager.screen)

        pygame.display.flip()

        for dice in diceList:
            dice.roll_dice(self.gameStateManager.screen)
        roll_1 = self.dice_1.face
        roll_2 = self.dice_2.face
        roll_3 = self.dice_3.face

        print('Melee Diceroll Door GS')

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.accept_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.melee_door(roll_1, roll_2, roll_3):
                            self.game.map.remove(self.game.clickedTile)
                            newTile = self.game.clickedTile.get_destroyed()
                            self.game.map.append(newTile)
                            self.game.clickedTile = newTile
                        self.gameStateManager.screen.fill('black')
                        self.gameStateManager.run_gamestate("gsAction")

                    
                    if self.game.selectedModel.AP != 0:
                        if self.rollAgain_button.rect.collidepoint(pygame.mouse.get_pos()):
                            self.game.selectedModel.AP -= 1
                            self.gameStateManager.screen.fill('black')
                            self.gameStateManager.run_gamestate("mlRollDoorGS")


class MeleeDiceRollGS:
    def __init__(self, gameStateManager, game) -> None:
        self.game = game
        self.gameStateManager = gameStateManager
        self.dice_1 = Dice(10, 10)
        self.dice_2 = Dice(110, 10)
        self.dice_3 = Dice(210, 10)
        self.dice_4 = Dice(360, 10)
        self.dice_5 = Dice(460,10)
        self.accept_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.reroll_image = pygame.image.load('Pictures/Tiles/Floor_1.png')     
        self.psyup_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.psydown_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.turn_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.accept_button = Button(410,500, self.accept_image, 1)
        self.reroll_button = Button(410,100, self.reroll_image, 1)
        self.psyup_button = Button(410,200, self.psyup_image, 1)
        self.psydown_button = Button(410,300, self.psydown_image, 1)
        self.turn_button = Button(410,400, self.turn_image, 1)

    def melee_model(self, roll_1, roll_2, roll_3, roll_4, roll_5, psypoints = 0):
        attacker = self.game.selectedModel
        defender = self.game.clickedModel
        facing = self.game.is_facing(attacker,defender)

        if defender.weapon == "Thunderhammer" and facing:
            roll_3 = 0
            roll_4 += 2
        if defender.weapon == "Powersword" and facing:
            roll_4 += 1
        if defender.weapon == "Lightningclaws" and facing:
            if roll_4 > roll_5:
                roll_4 +=1
            else:
                roll_5 +=1
        if defender.weapon == "Axe":
            if facing:
                roll_4 +=1
            roll_4 += psypoints

        if attacker.isBroodlord:
            if defender.weapon == "Thunderhammer" and facing:
                roll_1 = roll_1 + roll_2
            else:
                if (roll_1 > roll_2 and roll_2 > roll_3) or (roll_3 > roll_2 and roll_2 > roll_1):
                    roll_1 = roll_1 + roll_3
                elif (roll_1 > roll_3 and roll_3 > roll_2) or (roll_2 > roll_3 and roll_3 > roll_1):
                    roll_1 = roll_1 + roll_2
                elif (roll_2 > roll_1 and roll_1 > roll_3) or (roll_3 > roll_1 and roll_1 > roll_2):
                    roll_1 = roll_2 + roll_3

        if defender.weapon == "Thunderhammer" and facing:
            if roll_1 > roll_4 or roll_2 > roll_4:
                winner = attacker
            elif roll_1 == roll_4 or roll_2 == roll_4:
                winner = None
            else:
                winner = defender
        
        elif defender.weapon == "Powersword":
            if roll_1 > roll_4 or roll_2 > roll_4 or roll_3 > roll_4:
                winner = attacker
            elif roll_1 == roll_4 or roll_2 == roll_4 or roll_3 == roll_4:
                winner = None
            else:
                winner = defender

        elif defender.weapon == "Lightningclaws" and facing:
            attackerRoll = max(roll_1,roll_2,roll_3)
            defenderRoll = max(roll_4,roll_5)

            if defenderRoll > attackerRoll:
                return defender
            elif attackerRoll > defenderRoll:
                return attacker
            else:
                return None

        elif defender.weapon == "Axe":
            if roll_1 > roll_4 or roll_2 > roll_4 or roll_3 > roll_4:
                winner = attacker
            elif roll_1 == roll_4 or roll_2 == roll_4 or roll_3 == roll_4:
                winner = None
            else:
                winner = defender
        
        else:
            if roll_1 > roll_4 or roll_2 > roll_4 or roll_3 > roll_4:
                winner = attacker
            elif roll_1 == roll_4 or roll_2 == roll_4 or roll_3 == roll_4:
                winner = None
            else:
                winner = defender

        return winner  

    def loose(self):
        model = self.game.selectedModel
        self.game.gsModelList.remove(model)
        self.game.selectedTile.isOccupied = False
        self.game.selectedTile.occupand = None
        self.game.reset_select()
        self.game.reset_clicked()
        self.gameStateManager.screen.fill('black')
        self.gameStateManager.run_gamestate("gsTurn")

    def win(self):
        self.game.smModelList.remove(self.game.clickedModel)
        self.game.clickedTile.isOccupied = False
        self.game.clickedTile.occupand = None
        self.game.reset_clicked()
        self.gameStateManager.screen.fill('black')
        self.gameStateManager.run_gamestate('gsAction')

    def adjust_facing(self):
        attacker = self.game.selectedModel
        defender = self.game.clickedModel
        wantedFace = (attacker.face[0] * (-1), attacker.face[1] * (-1))

        while defender.face != wantedFace:
            game.turn_model(defender, "left")

    def run(self):
        logger.info(f"Gamestate GSMeleeRoll")
        roll_1 = 0 
        roll_2 = 0
        roll_3 = 0
        roll_4 = 0
        roll_5 = 0
        selectDice = None
        diceList = []
        facing = self.game.is_facing(self.game.selectedModel, self.game.clickedModel)
        reroll = False
        guard = False
        if self.game.clickedModel.weapon == "Powersword" and facing:
            reroll = True
        if self.game.clickedModel.guard:
            guard = True
        psypoints = 0
        turn = False

        self.accept_button.draw(self.gameStateManager.screen)
        self.reroll_button.draw(self.gameStateManager.screen)
        self.turn_button.draw(self.gameStateManager.screen)
        if self.game.clickedModel.weapon == "Axe":
            self.psyup_button.draw(self.gameStateManager.screen)
            self.psydown_button.draw(self.gameStateManager.screen)

        pygame.display.flip()

        diceList.append(self.dice_1)
        diceList.append(self.dice_2)
        self.dice_1.roll_dice(self.gameStateManager.screen)
        roll_1 = self.dice_1.face
        self.dice_2.roll_dice(self.gameStateManager.screen)
        roll_2 = self.dice_2.face

        if self.game.clickedModel.weapon != "Thunderhammer" or (facing == False):
            self.dice_3.roll_dice(self.gameStateManager.screen)
            roll_3 = self.dice_3.face
            diceList.append(self.dice_3)

        self.dice_4.roll_dice(self.gameStateManager.screen)
        roll_4 = self.dice_4.face
        diceList.append(self.dice_4)
        if self.game.clickedModel.weapon == "Lightningclaws" and facing:
            self.dice_5.roll_dice(self.gameStateManager.screen)
            roll_5 = self.dice_5.face
            diceList.append(self.dice_5)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.accept_button.rect.collidepoint(pygame.mouse.get_pos()):
                        logger.debug(f"Melee won by: {self.melee_model(roll_1,roll_2,roll_3,roll_4,roll_5,psypoints)}")
                        if self.melee_model(roll_1, roll_2,roll_3,roll_4,roll_5,psypoints) == self.game.clickedModel:
                            if facing:
                                self.loose()
                            else:
                                if turn:
                                    self.adjust_facing()
                                self.gameStateManager.screen.fill('black')
                                self.gameStateManager.run_gamestate('gsAction')
                        elif self.melee_model(roll_1, roll_2,roll_3,roll_4,roll_5,psypoints) == self.game.selectedModel:
                            self.win()
                        else:
                            if turn:
                                self.adjust_facing()
                            self.gameStateManager.screen.fill('black')
                            self.gameStateManager.run_gamestate('gsAction')

                    elif self.turn_button.rect.collidepoint(pygame.mouse.get_pos()):
                        turn = not turn
                        logger.debug(f"Turn = {turn}")

                    elif self.reroll_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if selectDice in diceList:
                            if (guard) and (selectDice == self.dice_4 or selectDice == self.dice_5):
                                selectDice.roll_dice(self.gameStateManager.screen)
                                if selectDice == self.dice_4:
                                    roll_4 = self.dice_4.face
                                else:
                                    roll_5 = self.dice_5.face
                                guard = False
                            
                            elif (reroll) and ((selectDice == self.dice_1) or (selectDice == self.dice_2) or (selectDice == self.dice_3)):
                                if selectDice == self.dice_1:
                                    self.dice_1.roll_dice(self.gameStateManager.screen)
                                    roll_1 = self.dice_1.face
                                elif selectDice == self.dice_2:
                                    self.dice_2.roll_dice(self.gameStateManager.screen)
                                    roll_2 = self.dice_2.face
                                elif selectDice == self.dice_3:
                                    self.dice_3.roll_dice(self.gameStateManager.screen)
                                    roll_3 = self.dice_3.face
                                reroll = False

                    else:
                        for dice in diceList:
                            if dice.rect.collidepoint(pygame.mouse.get_pos()):
                                selectDice = dice

                    if self.game.clickedModel.weapon == "Axe":
                        if self.psyup_button.rect.collidepoint(pygame.mouse.get_pos()):
                            if self.game.psyPoints != 0:
                                psypoints += 1

                        if self.psydown_button.rect.collidepoint(pygame.mouse.get_pos()):
                            if psypoints != 0:
                                psypoints -= 1


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

        logger.debug("Gamestate Main")

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

            
pygame.init()
game = Game()
logger.info("Game initialized successfully.")
# wall = Wall("Pictures/Tiles/Floor_1.png",1,1)
# entry = EntryPoint("Pictures/Tiles/Floor_1.png",4,4)
# game.map.append(entry)
# game.map.append(wall)

screen = screen = pygame.display.set_mode((900, 900), pygame.DOUBLEBUF)
screen.fill("black")
logger.info("Initialized screen.")
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