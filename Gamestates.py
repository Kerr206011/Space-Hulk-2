from Models import *
from Board import *
from Game import *
import pygame.docs 

class GameStateManager:     #class to manage interactions between gamestates and provide a shared game object and storage
    def __init__(self, game, screen) -> None:
        self.game:Game = game
        self.screen = screen
        self.gamestates = {"smTurn": smTurn(self, self.game), 
                           "smAction": smAction(self, self.game), 
                           "gsAction": gsAction(self, self.game),
                           "blAction": blAction(self, self.game),
                           "gsTurn": gsTurn(self, self.game),
                           "reveal": revealGS(self, self.game),
                           "revealSM": revealSM(self, self.game),
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
                           "shootflamer": ShootFlamer(self, self.game),
                           "overwatch": Overwatch(self, self.game)}

        self.overwatchAction = None

        self.revealList = [] #list of touples (model, tile)
        self.actionState = None #saves the current gamestate for out of sequence (oos) reveals

        self.freeShot = False   #if sm has free shoot Action and doesn't need to pay the AP for shooting
        self.freeTurn = False   #if gs has a free turn and doesn't need to expend AP for turning 90°

    def run_gamestate(self, gameState):     #method for executing the run methods of the individual gamestates saved in self.gamestates
        self.gamestates[gameState].run()

    def check_wincondition(self):
        gsWin = True
        smWin = False

        for model in self.game.smModelList:
            if model.weapon == "Flamer":
                gsWin = False

        for tile in self.game.map:
            if tile.isBurning and tile.sector == 15:
                smWin = True

        if smWin == True:
            logger.info(f"Spacemarines win. \nCongratulations {self.game.player1}!")
            self.run_gamestate("main")

        elif gsWin == True:
            logger.info(f"Genstealers win. \nCongratulations {self.game.player2}!")
            self.run_gamestate("main")

class BLstart:
    """
    Gamestate to place the first blips, before the first command phase.
    """
    def __init__(self, gameStateManager, game) -> None:
        self.game:Game = game
        self.gameStateManager:GameStateManager = gameStateManager
        self.BLAmount:int
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


class PlaceBL:     
    """
    Gamestate to place Blips during the reinforcement phase.
    """
    def __init__(self, gameStateManager, game) -> None:
        self.game:Game = game
        self.gameStateManager:GameStateManager = gameStateManager
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
            self.endState()
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
        for tile in self.game.map:
            if isinstance(tile, EntryPoint):
                for square in self.game.map:
                    if isinstance(square, Tile):
                        if square.isOccupied:
                            if square.occupand in self.game.smModelList:
                                if game.check_path(tile, square, 6):
                                    logger.info(f"Models in tile {tile} are forced to lurk!")
                                    for model in tile.blips:
                                        if model.lurking == False:
                                            model.AP = 0
                                            model.lurking = True
                                    for gs in tile.genstealers:
                                        if gs.lurking == False:
                                            gs.AP = 0
                                            gs.lurking = True
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
    """
    Gamestate to place Space Marines during the setup of the game.
    """
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager:GameStateManager = gameStateManager
        self.game:Game = game
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
    """
    Gamestate to reset the game after each turn.
    """
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager:GameStateManager = gameStateManager
        self.game:Game = game
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
        self.game.psykerPhase = False
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
    """
    Gamestate to manage the activation of a Spacemarine.
    """
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager:GameStateManager = gameStateManager
        self.game:Game = game
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
        """
        Method to check if a selected tile is viable for movement.

        Args:
            None

        Returns:
            boolean: True if viable, false if not.
        """
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
    
    def check_reveal(self):
        """
        Method to check if an action triggered an involuntary reveal.
        Also adds the seen blips to the  gameStateManagers revealList.

        Args:
            None

        Returns:
            boolean: True if yes.
        """
        visionList = self.game.check_vision(self.game.selectedModel, self.game.selectedTile)

        a = False

        for tile in visionList:
            if tile.occupand in self.game.blModelList:
                a = True
                self.gameStateManager.revealList.append((tile.occupand, tile))
        
        return a

    def check_melee(self):
        """
        Method to check if there is a door or an enemy model to the front of the selected model.

        Args:
            None

        Returns:
            boolean: True if yes.
        """
        if (self.game.selectedTile.x + self.game.selectedModel.face[0] == self.game.clickedTile.x) and (self.game.selectedTile.y + self.game.selectedModel.face[1] == self.game.clickedTile.y):
            if self.game.clickedModel != None:
                return True
            elif(isinstance(self.game.clickedTile, Door)):
                if self.game.clickedTile.isOpen == False:
                    return True
            else: 
                return False
            
    def check_ranged(self):
        """
        Method to check if a model can ranged attack a tile.

        Args:
            None

        Returns:
            boolean: True if viable, false if not.
        """
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
        self.overwatch_button.draw(self.gameStateManager.screen)

        pygame.display.flip()

        if self.check_reveal():
            self.gameStateManager.actionState = "smAction"
            self.gameStateManager.run_gamestate("revealSM")

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
                    self.turn_button.draw(self.gameStateManager.screen)
                    self.guard_button.draw(self.gameStateManager.screen)
                    if self.game.clickedTile != None:
                        if self.check_melee():
                            self.melee_button.draw(self.gameStateManager.screen)
                    self.shoot_button.draw(self.gameStateManager.screen)
                    self.accept_button.draw(self.gameStateManager.screen)
                    if self.check_door():
                        self.interact_button.draw(self.gameStateManager.screen)
                    self.overwatch_button.draw(self.gameStateManager.screen)
                    
                    pygame.display.flip()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.move_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.check_move():
                            if self.calculate_movement_cost() <= (self.game.selectedModel.AP + self.game.cp):
                                self.reduce_ap(self.calculate_movement_cost())
                                self.move_model()       
                                self.gameStateManager.freeShoot = True
                                if self.check_reveal():
                                    self.gameStateManager.actionState = "smAction"
                                    self.gameStateManager.run_gamestate("revealSM")
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
                                if self.check_reveal():
                                    self.gameStateManager.actionState = "smAction"
                                    self.gameStateManager.run_gamestate("revealSM")

                    elif self.turn_button.rect.collidepoint(pygame.mouse.get_pos()):
                        self.gameStateManager.screen.fill('black')
                        self.gameStateManager.run_gamestate("smTurning")

                    elif self.guard_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.game.selectedModel.AP + self.game.cp > 1:
                            self.game.selectedModel.guard = True
                            self.game.selectedModel.overwatch = False
                            self.reduce_ap(2)
                            logger.debug(f"Guard == {self.game.selectedModel.guard}")

                    elif self.overwatch_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.game.selectedModel.AP + self.game.cp > 1:
                            self.game.selectedModel.guard = False
                            self.game.selectedModel.overwatch = True
                            self.reduce_ap(2)
                            logger.debug(f"Overwatch == {self.game.selectedModel.overwatch}")

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
    """
    Gamestate to manage the choosing and activating of a SM.
    """
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager:GameStateManager = gameStateManager
        self.game:Game = game
        self.activate_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.end_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.activate_button = Button(810, 500, self.activate_image, 1)
        self.end_button = Button(810, 600, self.end_image, 1)

    def endState(self):
        for model in self.game.smModelList:
            model.susf = False
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
    """
    Gamestate to manage the turning of a SM.
    """
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager:GameStateManager = gameStateManager
        self.game:Game = game
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
    """
    Gamestate to manage the melee attack of a SM against a closed door.
    """
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager:GameStateManager = gameStateManager
        self.game:Game = game
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
    """
    Gamestate to manage the melee attack of a SM against a model to their front.
    """
    def __init__(self, gameStateManager, game) -> None:
        self.game:Game = game
        self.gameStateManager:GameStateManager = gameStateManager
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
        logger.debug(f"{roll_1}, {roll_2}, {roll_3}, {roll_4}, {roll_5}")
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
    """
    Gamestate to manage the shooting of a SM (excluding flamer).
    """
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager:GameStateManager = gameStateManager
        self.game:Game = game
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
        attacker = self.game.selectedModel
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
                                self.gameStateManager.screen.fill('black')
                                self.gameStateManager.run_gamestate("smAction")

                        else:
                            if self.game.clickedTile.isOccupied:
                                if (self.game.clickedTile.occupand in self.game.gsModelList):
                                    self.shoot_bolter(roll_1, roll_2)
                                else:
                                    logger.error(f"Non Genstealer type Object {self.game.clickedTile.occupand} selected as target!")
                            elif isinstance(self.game.clickedTile, Door):
                                if not self.game.clickedTile.isOpen:
                                    self.shoot_bolter_door(roll_1, roll_2)

                    # elif self.rollAgain_button.rect.collidepoint(pygame.mouse.get_pos()):
                    #     if (self.game.selectedModel.AP + self.game.cp > 0) or self.gameStateManager.freeShot:
                    #         if self.gameStateManager.freeShot == True:
                    #             self.gameStateManager.freeShot = False
                    #         else:
                    #             self.reduce_ap(1)
                    #         self.game.selectedModel.susf = True
                    #         self.gameStateManager.screen.fill('black')
                    #         pygame.display.flip()
                    #         self.gameStateManager.run_gamestate('shoot')

class ShootFlamer:
    """
    Gamestate to manage the shooting of a flamer.
    """
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager:GameStateManager = gameStateManager
        self.game:Game = game
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

class Overwatch:
    """
    Gamestate to manage overwatching.
    """
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager:GameStateManager = gameStateManager
        self.game:Game = game
        self.activate_image = pygame.image.load("Pictures/Tiles/Floor_1.png")
        self.activate_button = Button(810, 600, self.activate_image, 1)
        self.dice_1 = Dice(10,10)
        self.dice_2 = Dice(110, 10)
        self.dice_3 = Dice(210,10)

    def shoot_bolter(self, roll_1, roll_2, target, attacker):
        attacker = attacker
        defender = target

        if attacker.susf:
            roll_1 += 1
            roll_2 += 1
        else:
            attacker.susf = True

        if isinstance(defender, Door):
            if roll_1 > 5 or roll_2 > 5:
                logger.info(f"Hit with: {roll_1}, {roll_2}")
                self.game.map.remove(target)
                newTile = target.get_destroyed()
                self.game.map.append(newTile)
                self.game.clickedTile = newTile
            else:
                logger.info(f"Missed with: {roll_1}, {roll_2}")

        elif isinstance(defender, Genestealer):
            if defender.isBroodlord == False:
                if roll_1 > 5 or roll_2 > 5:
                    logger.info(f"Hit with: {roll_1}, {roll_2}")
                    self.game.selectedTile.isOccupied = False
                    self.game.gsModelList.remove(defender)
                    self.game.selectedTile.occupand = None
                    self.game.reset_select()
                    self.game.reset_clicked()
                else:
                    logger.info(f"Missed with: {roll_1}, {roll_2}")

            else:
                if roll_1 > 5 and roll_2 > 5:
                    logger.info(f"Hit with: {roll_1}, {roll_2}")
                    self.game.selectedTile.isOccupied = False
                    self.game.gsModelList.remove(defender)
                    self.game.selectedTile.occupand = None
                    self.game.reset_select()
                    self.game.reset_clicked()
                else:            
                    logger.info(f"Missed with: {roll_1}, {roll_2}")

        if roll_1 == roll_2:
            logger.debug(f"Model {attacker} has jammed!")
            attacker.jam = True

    def shoot_ac(self, roll_1, roll_2, roll_3, target, attacker):
        attacker = attacker
        defender = target
        self.game.assaultCannonAmmo -= 1

        if attacker.susf:
            roll_1 += 1
            roll_2 += 1
            roll_3 += 1
        else:
            attacker.susf = True

        if isinstance(defender, Door):
            if roll_1 > 4 or roll_2 > 4 or roll_3 >4:
                logger.info(f"Hit with: {roll_1}, {roll_2}, {roll_3}")
                self.game.map.remove(target)
                newTile = target.get_destroyed()
                self.game.map.append(newTile)
                self.game.clickedTile = newTile
            else:
                logger.info(f"Missed with: {roll_1}, {roll_2}, {roll_3}")

        elif isinstance(defender, Genestealer):
            if defender.isBroodlord == False:
                if roll_1 > 4 or roll_2 > 4 or roll_3 > 4:
                    logger.info(f"Hit with: {roll_1}, {roll_2}, {roll_3}")
                    self.game.selectedTile.isOccupied = False
                    self.game.gsModelList.remove(defender)
                    self.game.selectedTile.occupand = None
                    self.game.reset_select()
                    self.game.reset_clicked()
                else:
                    logger.info(f"Missed with: {roll_1}, {roll_2}, {roll_3}")

            else:
                if (roll_1 > 4 and roll_2 > 4) or (roll_1 > 4 and roll_3 > 4) or (roll_2 > 4 and roll_3 > 4):
                    logger.info(f"Hit with: {roll_1}, {roll_2}, {roll_3}")
                    self.game.selectedTile.isOccupied = False
                    self.game.gsModelList.remove(defender)
                    self.game.selectedTile.occupand = None
                    self.game.reset_select()
                    self.game.reset_clicked()
                else:            
                    logger.info(f"Missed with: {roll_1}, {roll_2}, {roll_3}")

    def run(self):
        overwatchModel = None
        overwatchTile = None
        selected = False
        roll_1 = 0
        roll_2 = 0
        roll_3 = 0
        if self.gameStateManager.overwatchAction == "door":
            overwatchlist = self.game.check_overwatch("door")
        else:
            overwatchlist = self.game.check_overwatch()

        logger.debug(f"Overwatch Action: {self.gameStateManager.overwatchAction}")

        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)
        self.activate_button.draw(self.gameStateManager.screen)
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()  

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.activate_button.rect.collidepoint(pygame.mouse.get_pos()) and (selected == False):
                        if overwatchModel != None and overwatchTile != None:
                            self.gameStateManager.screen.fill('black')
                            if overwatchModel.weapon == "Assaultcannon":
                                self.dice_1.roll_dice(self.gameStateManager.screen)
                                roll_1 = self.dice_1.face
                                self.dice_2.roll_dice(self.gameStateManager.screen)
                                roll_2 = self.dice_2.face
                                self.dice_3.roll_dice(self.gameStateManager.screen)
                                roll_3 = self.dice_3.face
                                time.sleep(0.25)

                                if self.gameStateManager.overwatchAction == "door":
                                    if self.game.clickedTile in self.game.check_vision(overwatchModel, overwatchTile):
                                        self.shoot_ac(roll_1, roll_2, roll_3, self.game.clickedTile, overwatchModel)
                                        selected = True
                                    
                                    if self.game.selectedModel in self.game.check_vision(overwatchModel, overwatchTile):
                                        if selected:
                                            self.gameStateManager.screen.fill('black')
                                            self.dice_1.roll_dice(self.gameStateManager.screen)
                                            roll_1 = self.dice_1.face
                                            self.dice_2.roll_dice(self.gameStateManager.screen)
                                            roll_2 = self.dice_2.face
                                            self.dice_3.roll_dice(self.gameStateManager.screen)
                                            roll_3 = self.dice_3.face
                                            time.sleep(0.25)
                                        self.shoot_ac(roll_1, roll_2, roll_3, self.game.selectedModel, overwatchModel)
                                        self.gameStateManager.screen.fill('black')
                                    for tile in self.game.map:
                                        tile.render(self.gameStateManager.screen)
                                    self.activate_button.draw(self.gameStateManager.screen)
                                    overwatchlist.remove(overwatchTile)
                                    overwatchModel = None
                                    overwatchTile = None

                                
                                else:  
                                    self.shoot_ac(roll_1, roll_2, roll_3, self.game.selectedModel, overwatchModel)
                                    self.gameStateManager.screen.fill('black')
                                    for tile in self.game.map:
                                        tile.render(self.gameStateManager.screen) 
                                    self.activate_button.draw(self.gameStateManager.screen)
                                    overwatchlist.remove(overwatchTile)
                                    overwatchModel = None
                                    overwatchTile = None
                            else:
                                self.dice_1.roll_dice(self.gameStateManager.screen)
                                roll_1 = self.dice_1.face
                                self.dice_2.roll_dice(self.gameStateManager.screen)
                                roll_2 = self.dice_2.face
                                time.sleep(0.25)

                                if self.gameStateManager.overwatchAction == "door":
                                    if self.game.clickedTile in self.game.check_vision(overwatchModel, overwatchTile):
                                        self.shoot_bolter(roll_1, roll_2, self.game.clickedTile, overwatchModel)
                                        selected = True
                                    
                                    if self.game.selectedModel in self.game.check_vision(overwatchModel, overwatchTile):
                                        if overwatchModel.jam == False:
                                            if selected:
                                                self.gameStateManager.screen.fill('black')
                                                self.dice_1.roll_dice(self.gameStateManager.screen)
                                                roll_1 = self.dice_1.face
                                                self.dice_2.roll_dice(self.gameStateManager.screen)
                                                roll_2 = self.dice_2.face
                                                time.sleep(0.25)
                                            self.shoot_bolter(roll_1, roll_2, self.game.selectedModel, overwatchModel)
                                            self.gameStateManager.screen.fill('black')
                                    for tile in self.game.map:
                                        tile.render(self.gameStateManager.screen)
                                    self.activate_button.draw(self.gameStateManager.screen)
                                    overwatchlist.remove(overwatchTile)
                                    overwatchModel = None
                                    overwatchTile = None

                                
                                else:  
                                    self.shoot_bolter(roll_1, roll_2, self.game.selectedModel, overwatchModel)
                                    self.gameStateManager.screen.fill('black')
                                    for tile in self.game.map:
                                        tile.render(self.gameStateManager.screen) 
                                    self.activate_button.draw(self.gameStateManager.screen)
                                    overwatchlist.remove(overwatchTile)
                                    overwatchModel = None
                                    overwatchTile = None

                        if overwatchlist.__len__() == 0:
                            self.gameStateManager.screen.fill('black')
                            if self.game.selectedModel != None:
                                self.gameStateManager.run_gamestate("gsAction")
                            else:
                                self.gameStateManager.run_gamestate("gsTurn")
                        else:
                            pygame.display.flip()

                    else:
                        for tile in self.game.map:
                            if tile.button.rect.collidepoint(pygame.mouse.get_pos()):
                                if tile in overwatchlist:
                                    overwatchTile = tile
                                    overwatchModel = tile.occupand


class ChooseBlip:
    """
    Gamestate to manage the choosing and activating of a blip on an entrypoint.
    """
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager:GameStateManager = gameStateManager
        self.game:Game = game
        self.activate_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.end_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.activate_button = Button(810, 500, self.activate_image, 1)
        self.end_button = Button(810, 600, self.end_image, 1)
        self.model_1_button = Button(100,100, self.activate_image, 1)
        self.model_2_button = Button(200,100, self.activate_image, 1)
        self.model_3_button = Button(300,100, self.activate_image, 1)
        self.genstealer_button = Button(400, 100, self.activate_image, 1)

    def run(self):

        buttonlist = []
        if self.game.selectedTile.blips.__len__() > 0:
            buttonlist.append(self.model_1_button)
        if self.game.selectedTile.blips.__len__() > 1:
            buttonlist.append(self.model_2_button)
        if self.game.selectedTile.blips.__len__() > 2:
            buttonlist.append(self.model_3_button)
        if self.game.selectedTile.genstealers.__len__() > 0:
            buttonlist.append(self.genstealer_button)

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
                            if self.game.selectedModel in self.game.blModelList:
                                self.gameStateManager.run_gamestate("blAction")
                            else:
                                self.gameStateManager.run_gamestate("gsAction")

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
                                print(self.game.selectedModel.count)
                            elif button == self.model_2_button:
                                self.game.selectedModel = self.game.selectedTile.blips[1]
                                print(self.game.selectedModel.AP)
                                print(self.game.selectedModel.count)
                            elif button == self.model_3_button:
                                self.game.selectedModel = self.game.selectedTile.blips[2]
                                print(self.game.selectedModel.AP)
                                print(self.game.selectedModel.count)
                            elif button == self.genstealer_button:
                                self.game.selectedModel = self.game.selectedTile.genstealers[0]
                                print(self.game.selectedModel.AP)
                            

class gsAction:
    """
    Gamestate to manage the activation of a Genstealer.
    """
    def __init__(self, gameStateManager, game) -> None:
        self.game:Game = game
        self.gameStateManager:GameStateManager = gameStateManager
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
        """
        Checks if the selected tile is available for movement

        Args:
            None

        Returns:
            boolean: True if viable, false if not
        """
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
        """
        Calculates the cost for moving to the selected tile.
        Game.selectedTile needs to be a viable tile for the nethod to work.

        Args:
            None

        Returns:
            int: Movementcost in actionpoints
        """
        face = self.game.selectedModel.face
        if ((self.game.selectedTile.x - face[0] == self.game.clickedTile.x) and (face[0] != 0)) or ((self.game.selectedTile.y - face[1] == self.game.clickedTile.y) and (face[1] != 0)):
            return 2
        else:
            return 1
            
    def move_model(self):
        """
        Moves a model on the Map.
        Game.selectedTile and Game.selectedModel must be viable for the method to work.

        Args:
            None

        Returns:
            None
        """
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

        if isinstance(self.game.selectedTile, EntryPoint):
            while not (((self.game.selectedTile.x + self.game.selectedModel.face[0]) == self.game.clickedTile.x) and  ((self.game.selectedTile.y + self.game.selectedModel.face[1]) == self.game.clickedTile.y)):
                self.game.turn_model(self.game.selectedModel, "left")
            self.game.selectedTile.genstealers.remove(self.game.selectedModel)
            self.game.clickedTile.occupand = self.game.selectedModel
            self.game.clickedTile.isOccupied = True
            pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.clickedTile.button.rect)
            self.game.clickedTile.render(self.gameStateManager.screen)
            pygame.display.update(self.game.clickedTile.button.rect)
            self.game.selectedTile = self.game.clickedTile
            self.game.reset_clicked()
            
        else:
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
            self.gameStateManager.overwatchAction = "move"
            self.gameStateManager.screen.fill('black')
            self.gameStateManager.run_gamestate("overwatch")

    def check_door(self):
        """
        Checks if the selected tile is a door and if the model is eligable to open it.

        Args:
            None

        Returns:
            boolean: True if viable, false if not
        """
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
        """
        Checks if the selected model has a closed door or an enemy model to their front.

        Args:
            None

        Returns:
            boolean
        """
        if isinstance(self.game.clickedTile, Tile):
            if (self.game.selectedTile.x + self.game.selectedModel.face[0] == self.game.clickedTile.x) and (self.game.selectedTile.y + self.game.selectedModel.face[1] == self.game.clickedTile.y):
                if self.game.clickedModel != None:
                    return True
                elif(isinstance(self.game.clickedTile, Door)):
                    if self.game.clickedTile.isOpen == False:
                        return True
                else: 
                    return False
                
    def check_reveal(self):
        """
        Method to check if an action triggered an involuntary reveal.
        It also adds the seen models to the Gamestatemanager.revealList

        Args:
            None

        Returns:
            boolean: True if any models were seen
        """

        a = False
        seenList = self.game.check_full_vision()
        for tile in seenList:
            if tile.occupand in self.game.blModelList:
                self.gameStateManager.revealList.append((tile.occupand, tile))
                a = True
        
        return a

    def run(self):
        """
        Main method of the gamestate.
        """
        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)

        self.move_button.draw(self.gameStateManager.screen)
        if self.check_door():
            self.interact_button.draw(self.gameStateManager.screen)
        if not isinstance(self.game.selectedTile, EntryPoint):
            self.turn_button.draw(self.gameStateManager.screen)
        if self.check_melee():
            self.melee_button.draw(self.gameStateManager.screen)
        self.end_button.draw(self.gameStateManager.screen)

        pygame.display.flip()

        logger.info(f"Current gamestate: gsAction")
        logger.debug(f"SelectedModel.AP: {self.game.selectedModel.AP}")
        logger.debug(f"selectedModel.broodlord: {self.game.selectedModel.isBroodlord}")

        if self.check_reveal():
            self.gameStateManager.actionState = "gsAction"
            self.gameStateManager.run_gamestate("revealSM")

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
                    if not isinstance(self.game.selectedTile, EntryPoint):
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
                                self.move_model()
                                if self.check_reveal():
                                    self.gameStateManager.actionState = "gsAction"
                                    self.gameStateManager.run_gamestate("revealSM")
                    
                    elif self.interact_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.check_door():
                            if self.game.selectedModel.AP != 0:
                                self.game.interact_door(self.game.clickedTile)
                                self.game.selectedModel.AP -= 1
                                pygame.draw.rect(self.gameStateManager.screen, 'black', self.game.clickedTile.button.rect)
                                self.game.clickedTile.render(self.gameStateManager.screen)
                                pygame.display.update(self.game.clickedTile.button.rect)
                                if self.game.clickedTile.isOpen == False:
                                    if self.game.check_overwatch("door").__len__() != 0:
                                        logger.info(self.game.check_overwatch("door"))
                                        self.gameStateManager.overwatchAction = "door"
                                        self.gameStateManager.screen.fill('black')
                                        self.gameStateManager.run_gamestate("overwatch")
                                if self.check_reveal():
                                    self.gameStateManager.actionState = "gsAction"
                                    self.gameStateManager.run_gamestate("revealSM")

                    elif self.turn_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if not isinstance(self.game.selectedTile, EntryPoint):
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
    """
    Gamestate to manage the activation of a blip.
    """
    def __init__(self, gameStateManager, game) -> None:
        self.game:Game = game
        self.gameStateManager:GameStateManager = gameStateManager
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

    def check_reveal(self):
        """
        Method to check if an action triggered an involuntary reveal.
        It also adds the seen models to the Gamestatemanager.revealList

        Args:
            None

        Returns:
            boolean: True if any models were seen
        """

        a = False
        seenList = self.game.check_full_vision()
        for tile in seenList:
            if tile.occupand in self.game.blModelList:
                self.gameStateManager.revealList.append((tile.occupand, tile))
                a = True
        
        return a

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
                                if self.check_reveal():
                                    self.gameStateManager.actionState = "blAction"
                                    self.gameStateManager.run_gamestate("revealSM")

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
        self.game:Game = game
        self.gameStateManager:GameStateManager = gameStateManager

        self.left_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.right_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.accept_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.broodlord_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.left_button = Button(810, 400, self.left_image, 1)
        self.right_button = Button(810, 500, self.right_image, 1)
        self.accept_button = Button(810, 700, self.accept_image, 1)
        self.place_button = Button(810, 800, self.place_image, 1)
        self.broodlord_button = Button(810, 100, self.broodlord_image, 1)

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

        self.game.blipReserve.append(self.game.selectedModel.count)
        self.game.blModelList.remove(self.game.selectedModel)
        self.game.selectedModel = gsList.pop(0)
        if isinstance(self.game.selectedTile, Tile):
            self.game.selectedTile.occupand = self.game.selectedModel
            self.game.gsModelList.append(self.game.selectedModel)

        elif isinstance(self.game.selectedTile, EntryPoint):
            self.game.selectedTile.genstealers.append(self.game.selectedModel)
            self.game.gsModelList.append(self.game.selectedModel)
            if self.game.selectedModel in self.game.gsModelList:
                logger.debug(f"GS model = {self.game.selectedModel} in GSmodelList")
            for model in gsList:
                self.game.selectedTile.genstealers.append(model)
                self.game.gsModelList.append(model)
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
        if self.game.broodLord:
            if gsList.__len__() == 2:
                self.broodlord_button.draw(self.gameStateManager.screen)
        
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
                    if self.game.broodLord:
                        if gsList.__len__() == 2:
                            self.broodlord_button.draw(self.gameStateManager.screen)
                    
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

                    elif self.broodlord_button.rect.collidepoint(pygame.mouse.get_pos()):    
                        if self.game.broodLord:
                            if gsList.__len__() == 2:
                                self.game.selectedModel.isBroodlord = True
                                self.game.broodLord = False
                                gsList = []
                                pygame.draw.rect(self.gameStateManager.screen, 'black', self.broodlord_button.rect)
                                pygame.display.update(self.broodlord_button.rect)

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


""" 
This class is used for converting Blips into Genstealers in the Spacemarine Turn.
This is neccecary because there are seperate Rules for this, such as Overwatching and placing in line of sight.
"""
class revealSM:
    
    def __init__(self, gameStateManager, game:Game) -> None:
        self.game:Game = game
        self.gameStateManager:GameStateManager = gameStateManager

        self.gsList = []
        self.activated = False  #Used to track if there was an oos action 
        self.returnState = None
        self.targetTile = None
        self.placeTile = None

        self.left_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.right_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.accept_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.place_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.broodlord_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.left_button = Button(810, 400, self.left_image, 1)
        self.right_button = Button(810, 500, self.right_image, 1)
        self.accept_button = Button(810, 700, self.accept_image, 1)
        self.place_button = Button(810, 800, self.place_image, 1)
        self.broodlord_button = Button(810, 100, self.broodlord_image, 1)

    def check_place(self, tile):
        """
        Checks if the selected Tile is viable for placing a model.

        Args:
            tile (Tile): The tile that is checked.

        Returns:
            bool: True if the tile is viable
        """

        if ((self.game.clickedTile.x == tile.x +1) or (self.game.clickedTile.x == tile.x -1) or (self.game.clickedTile.x == tile.x)) and ((self.game.clickedTile.y == tile.y +1) or (self.game.clickedTile.y == tile.y -1) or (self.game.cklickedTile.y == tile.y)):
            if isinstance(self.game.clickedTile, Tile):
                if not self.game.clickedTile.isOccupied:
                    if not self.game.clickedTile.isBurning:
                        return True
                    
    def generate_models(self, blip:Blip):
        """
        Generates Genstealer models from a Blip. Dependant on current number of Genstealers.

        Args:
            blip (Blip): The blip that needs to be converted

        Returns:
            None, adds the Genstealers to the Objects gsList
        """
        a = 0
        while (a < blip.count) and self.game.gsModelList.__len__() <= self.game.maxGS:
            a += 1
            self.gsList.append(Genestealer())
        self.game.blipReserve.append(blip.count)
        self.game.blModelList.remove(blip)

                    
    def end_phase(self):
        self.gameStateManager.screen.fill('black')
        self.activated = False

        if gameStateManager.revealList.__len__() != 0:
            gameStateManager.run_gamestate("revealSM")

        if self.returnState == "smAction":
            if self.game.selectedModel != None:
                self.gameStateManager.run_gamestate("smAction")
            else:
                self.gameStateManager.run_gamestate("smTurn")
        
        elif self.returnState == "gsAction":
            if self.game.selectedModel != None:
                self.gameStateManager.run_gamestate("gsAction")
            else:
                self.gameStateManager.run_gamestate("gsTurn")

        elif self.returnState == "blAction":
            if self.game.selectedModel in self.game.blModelList:
                self.gameStateManager.run_gamestate("blAction")
            else:
                self.gameStateManager.run_gamestate("gsTurn")

    def shoot_bolter(self, roll_1, roll_2, target, attacker, targetTile):
        attacker = attacker
        defender = target

        if attacker.susf:
            roll_1 += 1
            roll_2 += 1

        if isinstance(defender, Genestealer):
            if defender.isBroodlord == False:
                if roll_1 > 5 or roll_2 > 5:
                    logger.info(f"Hit with: {roll_1}, {roll_2}")
                    targetTile.isOccupied = False
                    self.game.gsModelList.remove(defender)
                    targetTile.occupand = None
                else:
                    logger.info(f"Missed with: {roll_1}, {roll_2}")

            else:
                if roll_1 > 5 and roll_2 > 5:
                    logger.info(f"Hit with: {roll_1}, {roll_2}")
                    targetTile.isOccupied = False
                    self.game.gsModelList.remove(defender)
                    targetTile.occupand = None
                else:            
                    logger.info(f"Missed with: {roll_1}, {roll_2}")

        if roll_1 == roll_2:
            logger.debug(f"Model {attacker} has jammed!")
            attacker.jam = True

    def shoot_ac(self, roll_1, roll_2, roll_3, target, attacker, targetTile):
        attacker = attacker
        defender = target
        self.game.assaultCannonAmmo -= 1

        if attacker.susf:
            roll_1 += 1
            roll_2 += 1
            roll_3 += 1

        if isinstance(defender, Genestealer):
            if defender.isBroodlord == False:
                if roll_1 > 4 or roll_2 > 4 or roll_3 > 4:
                    logger.info(f"Hit with: {roll_1}, {roll_2}, {roll_3}")
                    targetTile.isOccupied = False
                    self.game.gsModelList.remove(defender)
                    targetTile.occupand = None
                else:
                    logger.info(f"Missed with: {roll_1}, {roll_2}, {roll_3}")

            else:
                if (roll_1 > 4 and roll_2 > 4) or (roll_1 > 4 and roll_3 > 4) or (roll_2 > 4 and roll_3 > 4):
                    logger.info(f"Hit with: {roll_1}, {roll_2}, {roll_3}")
                    targetTile.isOccupied = False
                    self.game.gsModelList.remove(defender)
                    targetTile.occupand = None
                else:            
                    logger.info(f"Missed with: {roll_1}, {roll_2}, {roll_3}")
                    
    def overwatch(self, target:Genestealer, targetTile:Tile):
        overwatchList = self.game.check_overwatch("reveal", targetTile)
        dice_1 = Dice(10, 10)
        dice_2 = Dice(110, 10)
        dice_3 = Dice(210, 10)

        while overwatchList.__len__() > 0:
            overwatchTile = overwatchList.pop(0)
            overwatchModel = overwatchTile.occupand

            dice_1.roll_dice(self.gameStateManager.screen)
            roll_1 = dice_1.face
            dice_2.roll_dice(self.gameStateManager.screen)
            roll_2 = dice_2.face
            
            if overwatchModel.weapon == "Assaultcannon":
                dice_3.roll_dice(self.gameStateManager.screen)
                roll_3 = dice_3.face

                self.shoot_ac(roll_1, roll_2, roll_3, target, overwatchModel, targetTile)

            else:
                self.shoot_bolter(roll_1, roll_2, target, overwatchModel, targetTile)

            pygame.draw.rect(self.gameStateManager.screen, 'black', dice_1.rect)
            pygame.draw.rect(self.gameStateManager.screen, 'black', dice_2.rect)
            pygame.draw.rect(self.gameStateManager.screen, 'black', dice_3.rect)
            pygame.display.flip()
                
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

        return frSpace
        
    def run(self):

        logger.info(f"Current Gamestate: SMreveal")
        placed = False
        self.placeTile = None

        if self.activated == False:
            a = gameStateManager.revealList.pop(0)
            self.gsList = []
            self.generate_models(a[0])
            self.targetTile = a[1]
            self.returnState = self.gameStateManager.actionState
            self.activated = True
            placeModel = self.gsList.pop(0)
            self.targetTile.occupand = placeModel
            placed = True
            self.placeTile = self.targetTile

        else:
            if self.gsList.__len__() == 0 or freeTiles.__len__() == 0:
                self.end_phase()
            else:
                placeModel = self.gsList.pop(0)
        
        freeTiles = self.check_space(self.targetTile)

        self.gameStateManager.screen.fill('black')

        for tile in self.game.map:
            tile.render(self.gameStateManager.screen)
        
        self.left_button.draw(self.gameStateManager.screen)
        self.right_button.draw(self.gameStateManager.screen)
        self.accept_button.draw(self.gameStateManager.screen)
        if self.game.broodLord:
            self.broodlord_button.draw(self.gameStateManager.screen)

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
                    
                    pygame.display.flip()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.left_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if isinstance(self.placeTile, Tile):
                            if placed:
                                self.game.turn_model(placeModel, "left")
                                pygame.draw.rect(self.gameStateManager.screen, 'black', self.placeTile.button.rect)
                                self.placeTile.render(self.gameStateManager.screen)
                                pygame.display.update(self.placeTile.button.rect)

                    elif self.right_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if isinstance(self.placeTile, Tile):
                            if placed:
                                self.game.turn_model(placeModel, "right")
                                pygame.draw.rect(self.gameStateManager.screen, 'black', self.placeTile.button.rect)
                                self.placeTile.render(self.gameStateManager.screen)
                                pygame.display.update(self.placeTile.button.rect)

                    elif self.accept_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if placed:
                            self.overwatch(placeModel, self.placeTile)
                            freeTiles = self.check_space(self.targetTile)

                            if self.gsList.__len__() == 0 or freeTiles.__len__() == 0:                           
                                self.game.gsModelList.append(placeModel)
                                self.end_phase()
                            else:
                                placed = False  
                                self.game.gsModelList.append(placeModel)
                                placeModel = self.gsList.pop(0)
                                if (self.placeTile in freeTiles) and not (isinstance(self.placeTile, EntryPoint)):
                                    freeTiles.remove(self.placeTile)
                                pygame.draw.rect(self.gameStateManager.screen,'black',self.accept_button.rect)
                                self.place_button.draw(self.gameStateManager.screen)
                                pygame.display.update(self.accept_button.rect)
                                pygame.display.update(self.place_button.rect)

                    elif self.place_button.rect.collidepoint(pygame.mouse.get_pos()):
                        if placed == False:
                            if isinstance(self.placeTile, Tile):
                                if self.placeTile in freeTiles:
                                    self.placeTile.occupand = placeModel
                                    self.placeTile.isOccupied = True
                                    pygame.draw.rect(self.gameStateManager.screen, 'black', self.placeTile.button.rect)
                                    self.placeTile.render(self.gameStateManager.screen)
                                    pygame.display.update(self.placeTile.button.rect)
                                    placed = True
                                    self.accept_button.draw(self.gameStateManager.screen)
                                    pygame.draw.rect(self.gameStateManager.screen, 'black', self.place_button.rect)
                                    pygame.display.update(self.accept_button.rect)
                                    pygame.display.update(self.place_button.rect)
                                else:
                                    logger.debug('select a valid tile')

                            elif isinstance(self.game.selectedTile, EntryPoint):
                                self.placeTile.genstealers.append(placeModel)
                                if self.gsList.__len__() == 0 or freeTiles.__len__() == 0:
                                    self.end_phase()
                                else:
                                    placed = False
                                    placeModel = self.gsList.pop(0)

                    elif self.broodlord_button.rect.collidepoint(pygame.mouse.get_pos()):    
                        if self.game.broodLord:
                            if self.gsList.__len__() == 2:
                                self.targetTile.occupand.isBroodlord = True
                                self.game.broodLord = False
                                self.gsList = []
                                pygame.draw.rect(self.gameStateManager.screen, 'black', self.broodlord_button.rect)
                                pygame.display.update(self.broodlord_button.rect)

                    else:
                        if placed == False:
                            for tile in self.game.map:
                                if tile.button.rect.collidepoint(pygame.mouse.get_pos()):
                                    if isinstance(tile, Tile) and (tile in freeTiles):
                                        self.placeTile = tile
                                    elif isinstance(tile, EntryPoint) and (tile in freeTiles):
                                        self.placeTile = tile
                                    else:
                                        logger.info('select a valid Tile(click)')


class gsTurn:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager:GameStateManager = gameStateManager
        self.game:Game = game
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
        self.gameStateManager:GameStateManager = gameStateManager
        self.game:Game = game
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
                        if turnAmount != 0 and cost != 0:
                            if self.game.check_overwatch():
                                self.gameStateManager.run_gamestate("overwatch")
                        self.gameStateManager.run_gamestate("gsAction")


class MeleeDiceRollDoorGS:
    def __init__(self, gameStateManager, game) -> None:
        self.gameStateManager:GameStateManager = gameStateManager
        self.game:Game = game
        self.dice_1 = Dice(10,10)
        self.dice_2 = Dice(110, 10)
        self.dice_3 = Dice(210, 10)
        self.rollAgain_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.accept_image = pygame.image.load('Pictures/Tiles/Floor_1.png')
        self.rollAgain_button = Button(410, 500, self.rollAgain_image, 1)
        self.accept_button = Button(410, 700, self.accept_image, 1)

    def melee_door(self, roll_1, roll_2, roll_3):
        if self.game.selectedModel.isBroodlord == True:   
            if (roll_1 > roll_2 and roll_2 > roll_3) or (roll_3 > roll_2 and roll_2 > roll_1):
                roll_1 = roll_1 + roll_3
            elif (roll_1 > roll_3 and roll_3 > roll_2) or (roll_2 > roll_3 and roll_3 > roll_1):
                roll_1 = roll_1 + roll_2
            elif (roll_2 > roll_1 and roll_1 > roll_3) or (roll_3 > roll_1 and roll_1 > roll_2):
                roll_1 = roll_2 + roll_3

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
        self.game.selectedModel.AP -= 1
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
        self.game:Game = game
        self.gameStateManager:GameStateManager = gameStateManager
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

        logger.debug(f"{roll_1}, {roll_2}, {roll_3}, {roll_4}, {roll_5}")
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
        self.gameStateManager:GameStateManager = gameStateManager
        self.game:Game = game

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