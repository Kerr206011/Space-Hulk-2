import pygame
import random 
import sys
import time
from collections import deque

SM_ModellList = []                     #a list of Space Marine models
GS_ModellList = []                     #a list of Genstealer models
BL_ModellList = []

pygame.init()
#screen = pygame.display.set_mode((1080,700))
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen.fill('black')
pygame.display.set_caption('Space Hulk')

#Button class
class Button():
    def __init__(self, x, y, image, scale) -> None:
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.prev_mouse_state = False

    def draw(self, surface):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()
        #get mouse state
        mouse_state = pygame.mouse.get_pressed()[0] == 1

        # Check if mouse is over the button
        if self.rect.collidepoint(pos):
            # Check if mouse button is pressed down
            if mouse_state and not self.prev_mouse_state:
                self.clicked = True

         # Check if mouse button is released
        if not mouse_state and self.prev_mouse_state:
            if self.clicked:
                action = True
            self.clicked = False

        #draw button on screen
        surface.blit(self.image, (self.rect.x, self.rect.y))

         # Update previous mouse state
        self.prev_mouse_state = mouse_state

        return action

    def safedraw(self, surface):    #only returns True if the Mouse is released and on the Button
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()
        #get mouse state
        mouse_state = pygame.mouse.get_pressed()[0] == 1

        # Check if mouse is over the button
        if self.rect.collidepoint(pos):
            # Check if mouse button is pressed down
            if mouse_state and not self.prev_mouse_state:
                self.clicked = True

         # Check if mouse button is released
        if not mouse_state and self.prev_mouse_state:
            if self.clicked:
                if(self.rect.collidepoint(pos)):
                    action = True
            self.clicked = False

        #draw button on screen
        surface.blit(self.image, (self.rect.x, self.rect.y))

         # Update previous mouse state
        self.prev_mouse_state = mouse_state

        return action

    def hover(self, surface):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        # Check if mouse is over the button
        if self.rect.collidepoint(pos):
            action = True

        #draw button on screen
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action
    
class GameStateManager:
    def __init__(self, state) -> None:
        self.state = state
        self.rev_models = []
        self.save_model = None
        self.save_tile = None
        self.rev_count = 0
        self.turn = False
        self.melee_turn = False
        self.gs_moveturn = False    #variables for free actions after moving/ turning
        self.gs_turnaftermove = False
        self.SM_move = False
        self.sections = []
        self.ooc = False
        self.ooc_models = []
        self.savestate = None
    def changestate(self, newstate):
        self.state = newstate
    def givestate(self):
        return self.state
    
gameStateManager = GameStateManager('main')

class Game:                                         #can variables be exported to individual gamestates?
    def __init__(self) -> None:
        self.level = 1
        self.reinforcement = int
        self.gs_start = int
        self.Manager = gameStateManager
        self.states = {}                            #a list of gamestates that the game can have
        self.is_playing = str                       #the name of the player who is playing
        self.round = 1                              #the current round of the game
        self.player1 = ''                           #name of player 1
        self.player2 = ''                           #name of player 2
        self.selected_Model = None
        self.selected_tile = None                   #saves the selected model for other classes to interact with
        self.clicked_tile = None
        self.clicked_model = None
        self.Assault_cannon_Ammo = 10
        self.Assault_cannon_reload = True
        self.Heavy_flamer_ammo = 6
        self.CP = random.randint(1,6)               #a random number of CP for the sm player to use
        self.psy_points = 20

    def SM_prep(self):
        self.is_playing = self.player1
        self.selected_Model = None
        self.selected_tile = None
        self.clicked_model = None
        self.clicked_tile = None
        self.Manager.SM_move = False
        self.Manager.save_model = None
        self.Manager.save_tile = None
        self.round += 1
        for Model in SM_ModellList:
            Model.AP = 4
            Model.overwatch = False
            Model.guard = False
            Model.jam = False
        self.CP = random.randint(1,6)
        self.Manager.ooc = False
        self.Manager.ooc_models = []
        x = False
        for model in SM_ModellList: 
            if(model.rank == 'sergeant'):
                x = True
        for row in map:
            for tile in row:
                tile.is_buring = False
        for row in map: 
            for tile in row:
                if(tile.occupand in SM_ModellList):
                    checked = self.vision(tile.occupand, tile)
                    for tile in checked:
                        if(tile.occupand in BL_ModellList):
                            self.Manager.rev_models.append(tile)
                            checked.remove(tile)
                    if(self.Manager.rev_models.__len__() != 0):
                        if(x):
                            if(self.CP != 6):
                                self.Manager.savestate = 'reroll'
                        self.Manager.save_model = self.selected_Model
                        self.Manager.save_tile = self.selected_tile
                        self.reveal(self.Manager.rev_models[0])

        if((self.CP != 6) and (x)):
            self.Manager.changestate('reroll')
            self.run()

    def GS_prep(self):
        self.selected_Model = None
        self.selected_tile = None
        self.clicked_model = None
        self.clicked_tile = None
        for Model in GS_ModellList:
            Model.AP = 6
        for Model in BL_ModellList:
            Model.AP = 6
        for Model in SM_ModellList:
            Model.AP = 0
        self.Manager.save_model = None
        self.Manager.save_tile = None
        self.Manager.gs_turnaftermove = False
        self.Manager.gs_moveturn = False

    def redAP(self,Model,amount):
        if(Model in SM_ModellList):
            if(amount > Model.AP):
                self.CP = self.CP - ((amount) - (Model.AP))
                Model.AP = 0
            else: Model.AP -= amount
        if((Model in GS_ModellList) or (Model in BL_ModellList)):
            Model.AP -= amount

    def checkwin(self):
        match(self.level):
            case(1):
                f = False
                w = False
                winlis = [map[4][21],map[3][20],map[3][21],map[3][22],map[2][20],map[2][21],map[2][22],map[1][20],map[1][21],map[1][22]]
                for model in SM_ModellList:
                    if(model.weapon == 'flamer'):
                        f = True
                for tile in winlis:
                    if(tile.is_buring == True):
                        w = True
                if((self.Heavy_flamer_ammo == 0) or (f == False)):
                    self.Manager.changestate('gswin')
                    game.run()
                elif(w):
                    self.Manager.changestate('smwin')
                    game.run()
            case(2):
                for row in map:
                    for tile in row:
                        if(tile.is_lurkingpoint == True):
                            if(tile.is_occupied == True):
                                tile.is_occupied = False
                                BL_ModellList.remove(tile.occupand)
                                tile.occupand = None
                lis = []
                for row in map:
                    for tile in row:
                        if(tile.is_entrypoint == True):
                            a = False
                            for row in map:
                                for obj in row:
                                    if(obj.occupand in SM_ModellList):
                                        if(self.gsdistance(obj,tile)):
                                            a = True
                            if(a == False):
                                lis.append(tile)
                if(lis.__len__() == 0):
                    self.Manager.changestate('smwin')
                    game.run()
                if(self.states['gsprep'].bl_list.__len__() == 0):
                    if((BL_ModellList.__len__() == 0) and (GS_ModellList.__len__() == 0)):
                        self.Manager.changestate('smwin')
                        game.run()
                if(SM_ModellList.__len__() == 0):
                    self.Manager.changestate('gswin')
                    game.run()
                

    def vision(self,model,tile):
        ofset_x = 0
        ofset_y = 0
        b = False
        ofs = None
        x = tile.x
        y = tile.y
        is_looking_at_object = False
        i = 1
        seenModels = []
        match(model.face):
            case(1,0):
                ofset_x = 0
                ofset_y = 1
                ofs = (1,0)
            case(0,1):
                ofset_x = 1
                ofset_y = 0
                ofs = (0, 1)
            case(-1,0):
                ofset_x = 0
                ofset_y = 1
                ofs = (-1,0)
            case(0,-1):
                ofset_x = 1
                ofset_y = 0
                ofs = (0,-1)
        runS = True
        runL1 = True
        runL2 = True
        runR1 = True
        runR2 = True
        while(runS):
            x += ofs[0]
            y += ofs[1]
            checked_tile = map[y][x]
            if(checked_tile.is_occupied == True):
                seenModels.append(checked_tile)
                x = ((tile.x) + (ofset_x) + (ofs[0]))
                y = ((tile.y) + (ofset_y) + (ofs[1]))
                runS = False
                if(i == 1):
                    is_looking_at_object = True 
                i = 1
            elif((checked_tile.is_door == True) and (checked_tile.is_open == False)):
                seenModels.append(checked_tile)
                x = ((tile.x) + (ofset_x) + (ofs[0]))
                y = ((tile.y) + (ofset_y) + (ofs[1]))
                runS = False
                if(i == 1):
                    is_looking_at_object = True 
                i = 1
            elif((checked_tile.is_buring == True) or (checked_tile.is_wall == True) or (checked_tile.is_entrypoint)):
                x = ((tile.x) + (ofset_x) + (ofs[0]))
                y = ((tile.y) + (ofset_y) + (ofs[1]))
                runS = False
                if(i == 1):
                    is_looking_at_object = True
                i = 1
            else:
                i += 1
                seenModels.append(checked_tile)
        if(is_looking_at_object):
            match(model.face):
                case((1,0)):
                    if((map[tile.y + 1][tile.x].is_wall) or (map[tile.y + 1][tile.x].is_occupied)):
                        runL1 = False
                        runL2 = False
                    if((map[tile.y -1][tile.x].is_wall) or (map[tile.y -1][tile.x].is_occupied)):
                        runR1 = False
                        runR2 = False
                case((0,1)):
                    if((map[tile.y][tile.x -1].is_wall) or (map[tile.y][tile.x -1].is_occupied)):
                        runL1 = False
                        runL2 = False
                    if((map[tile.y][tile.x +1].is_wall) or (map[tile.y][tile.x +1].is_occupied)):
                        runR1 = False
                        runR2 = False
                case((-1,0)):
                    if((map[tile.y -1][tile.x].is_wall) or (map[tile.y -1][tile.x].is_occupied)):
                        runL1 = False
                        runL2 = False
                    if((map[tile.y +1][tile.x].is_wall) or (map[tile.y +1][tile.x].is_occupied)):
                        runR1 = False
                        runR2 = False
                case((0,-1)):
                    if((map[tile.y][tile.x +1].is_wall) or (map[tile.y][tile.x +1].is_occupied)):
                        runL1 = False
                        runL2 = False
                    if((map[tile.y][tile.x -1].is_wall) or (map[tile.y][tile.x -1].is_occupied)):
                        runR1 = False
                        runR2 = False
        while(runL1):
            checked_tile = map[y][x]
            if((checked_tile.is_occupied == True) or ((checked_tile.is_entrypoint == False) and (checked_tile.is_wall == False) and (checked_tile.is_buring == False) and ((checked_tile.is_door == False) or (checked_tile.is_open == True)))):
                seenModels.append(checked_tile)
                if((i == 1) and (checked_tile.is_occupied == True)):
                    b = True
                    runL2 = False
            elif((checked_tile.is_door == True) and (checked_tile.is_open == False)):
                seenModels.append(checked_tile)
                runL1 = False
                if((i == 1) or (b)):
                    runL2 = False
                    x = ((tile.x) - (ofset_x) + (ofs[0]))
                    y = ((tile.y) - (ofset_y) + (ofs[1]))
                else:
                    x = tile.x + (2 * ofset_x) + (2 * ofs[0])
                    y = tile.y + (2 * ofset_y) + (2 * ofs[1])
                i = 1
                b = False

            elif((checked_tile.is_buring == True) or (checked_tile.is_wall == True) or (checked_tile.is_entrypoint)):
                runL1 = False
                if((i == 1) or (b)):
                    runL2 = False
                    x = ((tile.x) - (ofset_x) + (ofs[0]))
                    y = ((tile.y) - (ofset_y) + (ofs[1]))
                else:
                    x = tile.x + (2 * ofset_x) + (2 * ofs[0])
                    y = tile.y + (2 * ofset_y) + (2 * ofs[1])
                i = 1
                b = False
            if((map[(checked_tile.y)+(ofset_y)][(checked_tile.x)+(ofset_x)].is_wall) and (map[(checked_tile.y)-(ofset_y)][(checked_tile.x)-(ofset_x)].is_wall)):
                runL1 = False
                if((i == 1) or (b)):
                    runL2 = False
                    x = ((tile.x) - (ofset_x) + (ofs[0]))
                    y = ((tile.y) - (ofset_y) + (ofs[1]))
                else:
                    x = tile.x + (2 * ofset_x) + (2 * ofs[0])
                    y = tile.y + (2 * ofset_y) + (2 * ofs[1])
                i = 1
                b = False
            if(runL1):
                x += ofs[0]
                y += ofs[1]
                i +=1
            if(is_looking_at_object):
                runL1 = False
                x = ((tile.x) + (2 * ofset_x) + (2 * ofs[0]))
                y = ((tile.y) + (2 * ofset_y) + (2 * ofs[1]))
                if(checked_tile.is_occupied):
                    runL2 = False
                    x = ((tile.x) - (ofset_x) + (ofs[0]))
                    y = ((tile.y) - (ofset_y) + (ofs[1]))
                if((checked_tile.is_buring == True) or (checked_tile.is_wall == True) or ((checked_tile.is_door == True) and (checked_tile.is_open == False)) or (checked_tile.is_entrypoint)):
                    runL2 = False
                    x = ((tile.x) - (ofset_x) + (ofs[0]))
                    y = ((tile.y) - (ofset_y) + (ofs[1]))
                i = 1
        while(runL2):
            checked_tile = map[y][x]
            if((checked_tile.is_occupied == True) or ((checked_tile.is_entrypoint == False) and (checked_tile.is_wall == False) and (checked_tile.is_buring == False) and ((checked_tile.is_door == False) or (checked_tile.is_open == True)))):
                seenModels.append(checked_tile)
            elif((checked_tile.is_door == True) and (checked_tile.is_open == False)):
                seenModels.append(checked_tile)
                runL2 = False
                x = ((tile.x) - (ofset_x) + (ofs[0]))
                y = ((tile.y) - (ofset_y) + (ofs[1]))
            elif((checked_tile.is_buring == True) or (checked_tile.is_wall == True) or (checked_tile.is_entrypoint)):
                runL2 = False
                x = ((tile.x) - (ofset_x) + (ofs[0]))
                y = ((tile.y) - (ofset_y) + (ofs[1]))
            if((map[(checked_tile.y)+(ofset_y)][(checked_tile.x)+(ofset_x)].is_wall) and (map[(checked_tile.y)-(ofset_y)][(checked_tile.x)-(ofset_x)].is_wall)):
                runL2 = False
                x = ((tile.x) - (ofset_x) + (ofs[0]))
                y = ((tile.y) - (ofset_y) + (ofs[1]))
            if(runL2):
                x += ofs[0]
                y += ofs[1]
            if(is_looking_at_object):
                runL2 = False
                x = ((tile.x) - (ofset_x) + (ofs[0]))
                y = ((tile.y) - (ofset_y) + (ofs[1]))
        while(runR1):
            checked_tile = map[y][x]
            if((checked_tile.is_occupied == True) or ((checked_tile.is_entrypoint == False) and (checked_tile.is_wall == False) and (checked_tile.is_buring == False) and ((checked_tile.is_door == False) or (checked_tile.is_open == True)))):
                seenModels.append(checked_tile)
                if((i == 1) and (checked_tile.is_occupied == True)):
                    b = True
                    runR2 = False
            elif((checked_tile.is_door == True) and (checked_tile.is_open == False)):
                runR1 = False
                if((i == 1) or (b)):
                    runR2 = False
                else:
                    x = ((tile.x) - (2 * ofset_x) + (2 * ofs[0]))
                    y = ((tile.y) - (2 * ofset_y) + (2 * ofs[1]))
            elif((checked_tile.is_buring == True) or (checked_tile.is_wall == True) or (checked_tile.is_entrypoint)):
                runR1 = False
                if((i == 1) or (b)):
                    runR2 = False
                else:
                    x = ((tile.x) - (2 * ofset_x) + (2 * ofs[0]))
                    y = ((tile.y) - (2 * ofset_y) + (2 * ofs[1]))
            if((map[(checked_tile.y)+(ofset_y)][(checked_tile.x)+(ofset_x)].is_wall) and (map[(checked_tile.y)-(ofset_y)][(checked_tile.x)-(ofset_x)].is_wall)):
                runR1 = False
                if((i == 1) or (b)):
                    runR2 = False
                else:
                    x = ((tile.x) - (2 * ofset_x) + (2 * ofs[0]))
                    y = ((tile.y) - (2 * ofset_y) + (2 * ofs[1]))
            if(runR1):
                x += ofs[0]
                y += ofs[1]
                i += 1
            if(is_looking_at_object):
                runR1 = False
                x = ((tile.x) - (2 * ofset_x) + (2 * ofs[0]))
                y = ((tile.y) - (2 * ofset_y) + (2 * ofs[1]))
                if(checked_tile.is_occupied):
                    runR2 = False
                if((checked_tile.is_buring == True) or (checked_tile.is_wall == True) or ((checked_tile.is_door == True) and (checked_tile.is_open == False)) or (checked_tile.is_entrypoint)):
                    runR2 = False
        while(runR2):
            checked_tile = map[y][x]
            if((checked_tile.is_occupied == True) or ((checked_tile.is_entrypoint == False) and (checked_tile.is_wall == False) and (checked_tile.is_buring == False) and ((checked_tile.is_door == False) or (checked_tile.is_open == True)))):
                seenModels.append(checked_tile)
            elif((checked_tile.is_door == True) and (checked_tile.is_open == False)):
                seenModels.append(checked_tile)
                runR2 = False
            elif((checked_tile.is_buring == True) or (checked_tile.is_wall == True) or (checked_tile.is_entrypoint)):
                runR2 = False
            if((map[(checked_tile.y)+(ofset_y)][(checked_tile.x)+(ofset_x)].is_wall) and (map[(checked_tile.y)-(ofset_y)][(checked_tile.x)-(ofset_x)].is_wall)):
                runR2 = False
            if(runR2):
                x += ofs[0]
                y += ofs[1]
            if(is_looking_at_object):
                runR2 = False
        
        return(seenModels)

    def distance(self,tiles, tilee):
        x = tiles.x - tilee.x
        y = tiles.y - tilee.y
        z = x+y
        distance = abs(z)
        return distance

    def gsdistance(self,tiles,tilee):
        ran = False
        k = True
        i = 0
        tilestart = tiles
        tilelis = []
        dist = self.distance(tiles,tilee)
        chelis = [[map[tilestart.y][tilestart.x + 1],map[tilestart.y][tilestart.x - 1],map[tilestart.y + 1][tilestart.x],map[tilestart.y - 1][tilestart.x]]]
        for liste in chelis:
            for tile in liste:
                if(self.distance(tile,tilee) < dist):
                    dist = self.distance(tile,tilee)
                    tilelis.append(tile)
        while k:
            for tile in tilelis:
                chelis.append([map[tile.y][tile.x + 1],map[tile.y][tile.x - 1],map[tile.y + 1][tile.x],map[tile.y - 1][tile.x]])
            tilelis = []
            for liste in chelis:
                for tile in liste:
                    if((self.distance(tile,tilee) < dist) and (tile.is_wall == False)):
                        dist = self.distance(tile,tilee)
                        tilelis.append(tile)
            chelis = []
            i += 1
            if(i <= 6):
                if(dist == 0):
                    ran = True
                k = False
        return ran
    

    def shoot(self):
        if(self.selected_Model in SM_ModellList):
            liste = game.vision(self.selected_Model,self.selected_tile)
            hit = False
            fatal = False
            match(self.selected_Model.weapon):
                case('fist'):
                    a = random.randint(1,6)
                    b = random.randint(1,6)
                    c = 0
                case('powerSword'):
                    a = random.randint(1,6)
                    b = random.randint(1,6)
                    c = 0
                case('chainFist'):
                    a = random.randint(1,6)
                    b = random.randint(1,6)
                    c = 0
                case('AssaultCanon'):
                    if(game.Assault_cannon_Ammo != 0):
                        a = random.randint(1,6)
                        b = random.randint(1,6)
                        c = random.randint(1,6)
                        game.Assault_cannon_Ammo -= 1
                        if((game.Assault_cannon_reload == False) and ((a == b) and (b == c))):
                            fatal = True
                    else:
                        SB.problem = 'No Ammo!'
                case('flamer'):
                    a = 0
                    b = 0
                    c = 0
                    burn = None
                    door = False
                    if(self.Heavy_flamer_ammo != 0):
                        if((self.clicked_tile in liste) and (self.distance(self.selected_tile, self.clicked_tile) < 13)):
                            self.Heavy_flamer_ammo -= 1
                            self.redAP(self.selected_Model, 2)
                            self.selected_Model.guard = False
                            for section in self.Manager.sections:
                                for tile in section:
                                    if(tile == self.clicked_tile):
                                        burn = section
                            if(burn != None):
                                for tile in burn:
                                    if(isinstance(tile,Tile)):
                                        if((tile.is_door) and (tile.is_open == False)):
                                            for obj in burn:
                                                if(isinstance(obj, list)):
                                                    if(self.clicked_tile in obj):
                                                        burn = obj

                            if(burn != None):
                                for tile in burn:
                                    if(isinstance(tile,Tile)):
                                        roll = random.randint(1,6)
                                        if((roll > 1) and (tile.is_occupied == True)):
                                            tile.is_occupied = False
                                            if(tile.occupand in SM_ModellList):
                                                SM_ModellList.remove(tile.occupand)
                                            elif(tile.occupand in GS_ModellList):
                                                GS_ModellList.remove(tile.occupand)
                                            elif(tile.occupand in BL_ModellList):
                                                BL_ModellList.remove(tile.occupand)
                                        if((tile.is_door == False) or ((tile.is_door == True) and (tile.is_open == True))):
                                            tile.is_buring = True
                        else: 
                            SB.problem = 'Tile cannot be reached!(range is 12 Tiles!)'
                    else:
                        SB.problem = 'No Ammo!'
            if(self.selected_Model.overwatch == True):
                if(((a == b) and not (c != 0)) and (self.is_playing == self.player2) and (self.selected_Model.weapon != 'flamer')):
                    game.selected_Model.jam = True
                    SB.problem = 'Jammed!'
            if(self.clicked_model != None) :
                if((self.clicked_tile in liste) and (self.clicked_model in GS_ModellList)):
                    if(self.Manager.SM_move == True):
                        self.Manager.SM_move = False
                    elif((self.selected_Model.weapon != 'flamer') and (self.selected_Model.overwatch == False)):
                        self.redAP(self.selected_Model, 1)
                        self.selected_Model.guard = False 
                        self.selected_Model.overwatch = False
                    if((c == 0) and (((a == 6) or (b == 6)) or ((self.selected_Model.susf) and ((a >= 5) or (b >= 5))))):
                        hit = True
                    elif((c != 0) and (((a >= 5) or (b >= 5) or (c >=5)) or ((self.selected_Model.susf) and ((a >= 4) or (b >= 4) or (c >= 4))))):
                        hit = True
                    game.selected_Model.susf = True

                if(hit):
                    GS_ModellList.remove(game.clicked_model)
                    game.clicked_model = None
                    game.clicked_tile.is_occupied = False
                    game.clicked_tile.occupand = None
                    game.clicked_tile = None

            if((self.clicked_tile != None) and (self.selected_Model.weapon != 'flamer')):
                if((self.clicked_tile.is_door == True) and (self.clicked_tile.is_open == False)):
                    if(self.Manager.SM_move == True):
                        self.Manager.SM_move = False
                        self.selected_Model.guard = False
                        self.selected_Model.overwatch = False
                    elif(self.selected_Model.overwatch == True):
                        pass
                    else:
                        self.redAP(self.selected_Model, 1)
                        self.selected_Model.guard = False
                    if((self.selected_Model.weapon == 'fist') or (self.selected_Model.weapon == 'powerSword') or (self.selected_Model.weapon == 'chainFist')):
                        if(((a == 6) or (b == 6)) or ((self.selected_Model.susf) and ((a > 4) or (b > 4)))):
                            self.clicked_tile.is_door = False
                    elif(self.selected_Model.weapon == 'AssaultCanon'):
                        if(((a >= 5) or (b >= 5) or (c >= 5)) or ((self.selected_Model.susf) and ((a >= 4) or (b >= 4) or (c >= 4)))):
                            self.clicked_tile.is_door = False
                    self.selected_Model.susf = True

        for row in map: 
            for tile in row:
                if(tile.occupand in SM_ModellList):
                    checked = self.vision(tile.occupand, tile)
                    for tile in checked:
                        if(tile.occupand in BL_ModellList):
                            self.Manager.rev_models.append(tile)
                            checked.remove(tile)
                    if(self.Manager.rev_models.__len__() != 0):
                        self.Manager.save_model = self.selected_Model
                        self.Manager.save_tile = self.selected_tile
                        self.reveal(self.Manager.rev_models[0])

        if(self.selected_Model.weapon != 'flamer'):
            if(c != 0):
                SB.roll = str(a) + ' | ' + str(b) + ' | ' +str(c)
            else:
                SB.roll = str(a) + ' | ' + str(b)

        if(fatal):
            self.selected_Model = None
            self.selected_tile.is_occupied = False
            self.selected_tile.occupand = None
            self.Manager.SM_move = False
            for section in self.Manager.sections:
                if(self.selected_tile in section):
                    for tile in section:
                        roll = random.randint(1,6)
                        if(roll >= 4):
                            if(tile.is_occupied):
                                if(tile.occupand in SM_ModellList):
                                    tile.is_occupied = False
                                    SM_ModellList.remove(tile.occupand)
                                    tile.occupand = None
                                elif(tile.occupand in GS_ModellList):
                                    tile.is_occupied = False
                                    GS_ModellList.remove(tile.occupand)
                                    tile.occupand = None
                            elif(tile.is_door):
                                tile.is_door = False
            self.selected_tile = None

    def ocDoor(self):
        a = False
        if(self.clicked_tile != None):
            if(self.clicked_tile.is_door == True):
                if((self.selected_Model != None) and (self.clicked_tile.is_occupied == False)):
                    ofs = game.selected_Model.face
                    if((((self.selected_tile.x + ofs[0] == self.clicked_tile.x) and (ofs[0] != 0)) or ((self.selected_tile.y + ofs[1] == self.clicked_tile.y) and (ofs[1] != 0))) or ((self.selected_Model in BL_ModellList) and (self.distance(self.selected_tile,self.clicked_tile) == 1))):
                        if(self.is_playing == self.player1):
                            if((self.selected_Model.AP != 0) | (self.CP != 0)):
                                self.redAP(self.selected_Model, 1)
                                self.selected_Model.guard = False
                                self.selected_Model.overwatch = False
                                self.Manager.SM_move = False
                                a = True
                        if(self.is_playing == self.player2):
                            if(self.selected_Model.AP != 0):
                                self.redAP(self.selected_Model, 1)
                                a = True
                                self.Manager.gs_turnaftermove = False
                                self.Manager.gs_moveturn = False
                                for row in map: 
                                    for tile in row:
                                        if(tile.occupand in SM_ModellList):
                                            checked = self.vision(tile.occupand, tile)
                                            if(self.selected_tile in checked):
                                                if(self.CP != 0):
                                                    self.Manager.ooc = True
                                                    self.Manager.ooc_models.append(tile.occupand)
                    else:
                        SB.problem = 'Model needs to face the Door!'
                else:
                    SB.problem = 'Cannot be used when model is on Tile!'
                                
                if(map[self.clicked_tile.y +1][self.clicked_tile.x].is_buring):
                    a = False
                elif(map[self.clicked_tile.y - 1][self.clicked_tile.x].is_buring):
                    a = False
                elif(map[self.clicked_tile.y][self.clicked_tile.x + 1].is_buring):
                    a = False
                elif(map[self.clicked_tile.y][self.clicked_tile.x - 1].is_buring):
                    a = False
            else:
                SB.problem = 'Needs to be used on a Door!'
        else:
            SB.problem = 'Select a Tile!'
        if(a):
            if(self.clicked_tile.is_open == True):
                self.clicked_tile.is_open = False
            else:
                self.clicked_tile.is_open = True
        for row in map: 
            for tile in row:
                if(tile.occupand in SM_ModellList):
                    checked = self.vision(tile.occupand, tile)
                    if(self.is_playing == self.player2):
                        if(tile.occupand.overwatch == True):
                            if((tile.occupand.jam == False) & (self.clicked_tile in checked)):
                                if(self.distance(tile, self.clicked_tile) < 14):
                                    if(self.clicked_tile.is_open == False):
                                        self.Manager.save_tile = self.selected_tile
                                        self.Manager.save_model = self.selected_Model
                                        self.selected_Model = tile.occupand
                                        self.selected_tile = tile
                                        self.shoot()
                                        if(not (self.Manager.save_model in GS_ModellList)):
                                            self.Manager.gs_turnaftermove = False
                                        self.selected_Model = self.Manager.save_model
                                        self.selected_tile = self.Manager.save_tile
                            elif((tile.occupand.jam == False) & (self.selected_tile in checked)):
                                if(self.distance(tile, self.clicked_tile) < 14):
                                    self.Manager.save_tile = self.selected_tile
                                    self.Manager.save_model = self.selected_Model
                                    self.clicked_model = self.selected_Model
                                    self.clicked_tile = self.selected_tile
                                    self.selected_Model = tile.occupand
                                    self.selected_tile = tile
                                    self.shoot()
                                    if(not (self.Manager.save_model in GS_ModellList)):
                                        self.Manager.gs_turnaftermove = False
                                    self.selected_Model = self.Manager.save_model
                                    self.selected_tile = self.Manager.save_tile
                    for tile in checked:
                        if(tile.occupand in BL_ModellList):
                            self.Manager.rev_models.append(tile)
                            checked.remove(tile)
                    if(self.Manager.rev_models.__len__() != 0):
                        self.Manager.save_model = self.selected_Model
                        self.Manager.save_tile = self.selected_tile
                        self.reveal(self.Manager.rev_models[0])
                
    def melee(self):
        door = False
        facing = False
        SM1 = 0
        SM2 = 0
        GS1 = random.randint(1,6)
        GS2 = random.randint(1,6)
        GS3 = random.randint(1,6)
        if((self.selected_tile != None) & (self.clicked_tile != None)):
            if((self.clicked_tile.is_door == True) and (self.clicked_tile.is_open == False)):
                if(((self.selected_tile.x + self.selected_Model.face[0]) == self.clicked_tile.x) & ((self.selected_tile.y + self.selected_Model.face[1]) == self.clicked_tile.y)):
                    self.redAP(self.selected_Model, 1)
                    door = True
                    if(self.is_playing == self.player1):
                        match(self.selected_Model.weapon):
                            case('fist'):
                                SM1 = random.randint(1,6)
                                SB.roll = str(SM1)
                            case('powerSword'):
                                SM1 = random.randint(1,6)
                                SB.roll = str(SM1)
                            case('chainFist'):
                                SM1 = 6
                                SB.roll = str(SM1)
                            case('AssaultCanon'):
                                SM1 = random.randint(1,6)
                                SB.roll = str(SM1)
                            case('claws'):
                                SM1 = random.randint(1,6)
                                SM2 = random.randint(1,6)
                                if(SM1 > SM2):
                                    SM1 += 1
                                else:
                                    SM2 += 1
                                SB.roll = str(SM1)+' | '+str(SM2)
                            case('flamer'):
                                SM1 = random.randint(1,6)
                                SB.roll = str(SM1)
                            case('hammer'):
                                SM1 = random.randint(1,6) + 1
                                SB.roll = str(SM1)
                        if(self.selected_Model.rank == 'sergeant'):
                            SM1 += 1
                            if(SM2 != 0):
                                SM2 += 1
                            SB.roll = str(SM1)
                        if((SM1 >= 6) or (SM2 >= 6)):
                            self.clicked_tile.is_door = False
                    if(self.is_playing == self.player2):
                        SB.roll = str(GS1)+' | '+str(GS2)+' | '+str(GS3)
                        if((GS1 >= 6) or (GS2 >= 6) or (GS3 >= 6)):
                            self.clicked_tile.is_door = False
                else:
                    SB.problem = 'Model needs to face the Door!'
            elif(self.clicked_model != None):
                if(((self.selected_tile.x + self.selected_Model.face[0]) == self.clicked_tile.x) & ((self.selected_tile.y + self.selected_Model.face[1]) == self.clicked_tile.y)):
                    if(self.selected_tile.is_occupied == True):
                        match(self.selected_Model.face):
                            case((1,0)):
                                if(self.clicked_model.face == (-1,0)):
                                    facing = True
                            case((-1,0)):
                                if(self.clicked_model.face == (1,0)):
                                    facing = True
                            case((0,1)):
                                if(self.clicked_model.face == (0,-1)):
                                    facing = True
                            case((0,-1)):
                                if(self.clicked_model.face == (0,1)):
                                    facing = True
                        if(self.is_playing == self.player1):
                            if(self.clicked_model in GS_ModellList):
                                game.redAP(game.selected_Model, 1)
                                self.selected_Model.guard = False
                                self.selected_Model.overwatch = False
                                self.Manager.SM_move = False
                                match(self.selected_Model.weapon):
                                    case('fist'):
                                        SM1 = random.randint(1,6)
                                        SB.roll = 'SM: '+str(SM1)+ '|| GS: '+str(GS1)+ ' | '+str(GS2)+ ' | '+str(GS3)
                                    case('chainFist'):
                                        SM1 = random.randint(1,6)
                                        SB.roll = 'SM: '+str(SM1)+ '|| GS: '+str(GS1)+ ' | '+str(GS2)+ ' | '+str(GS3)
                                    case('AssaultCanon'):
                                        SM1 = random.randint(1,6)
                                        SB.roll = 'SM: '+str(SM1)+ '|| GS: '+str(GS1)+ ' | '+str(GS2)+ ' | '+str(GS3)
                                    case('flamer'):
                                        SM1 = random.randint(1,6)
                                        SB.roll = 'SM: '+str(SM1)+ '|| GS: '+str(GS1)+ ' | '+str(GS2)+ ' | '+str(GS3)
                                    case('powerSword'):
                                        SM1 = random.randint(1,6)
                                        if(((SM1 < GS1) or (SM1 < GS2) or (SM1 < GS3)) or ((SM2 > SM1) and ((SM2 < GS1) or (SM2 < GS2) or (SM2 < GS3)))):
                                            if((GS1 > GS2) and (GS1 > GS3)):
                                                GS1 = random.randint(1,6)
                                            elif((GS2 > GS1) and (GS2 > GS3)):
                                                GS2 = random.randint(1,6)
                                            else:
                                                GS3 = random.randint(1,6)
                                        SB.roll = 'SM: '+str(SM1)+ '|| GS: '+str(GS1)+ ' | '+str(GS2)+ ' | '+str(GS3)
                                    case('claws'):
                                        SM1 = random.randint(1,6)
                                        SM2 = random.randint(1,6)
                                        if(SM1 > SM2):
                                            SM1 += 1
                                        else:
                                            SM2 += 1
                                        SB.roll = 'SM: '+str(SM1)+' | '+str(SM2)+ '|| GS: '+str(GS1)+ ' | '+str(GS2)+ ' | '+str(GS3)
                                    case('hammer'):
                                        SM1 = random.randint(1,6) +1 
                                        GS3 = 0
                                if(self.selected_Model.rank == 'sergeant'):
                                    SM1 += 1
                                    if(self.selected_Model.weapon == 'hammer'):
                                        SB.roll = 'SM: '+str(SM1)+ '|| GS: '+str(GS1)+ ' | '+str(GS2)
                                    else:
                                        SB.roll = 'SM: '+str(SM1)+ '|| GS: '+str(GS1)+ ' | '+str(GS2)+ ' | '+str(GS3)
                                if(((SM1 > GS1) & (SM1 > GS2) & (SM1 > GS3)) or ((SM2 > GS1) & (SM2 > GS2) & (SM2 > GS3))):
                                    self.clicked_tile.is_occupied = False
                                    self.clicked_tile.occupand = None
                                    GS_ModellList.remove(self.clicked_model)
                                    self.clicked_model = None
                                elif((facing == True) & (((GS1 > SM1) & (GS1 > SM2)) or ((GS2 > SM1) & (GS2 > SM2)) or ((GS3 > SM1) & (GS3 > SM2)))):
                                    self.selected_tile.is_occupied = False
                                    self.selected_tile.occupand = None
                                    SM_ModellList.remove(self.selected_Model)
                                    self.selected_Model = None
                                else: 
                                    self.Manager.melee_turn = True
                                    self.Manager.changestate('turn')
                                    self.run()

                        if(self.is_playing == self.player2):
                            if(self.clicked_model in SM_ModellList):
                                game.redAP(game.selected_Model, 1)
                                self.Manager.gs_turnaftermove = False
                                self.Manager.gs_moveturn = False
                                match(self.clicked_model.weapon):
                                    case('fist'):
                                        SM1 = random.randint(1,6)
                                        SB.roll = 'SM: '+str(SM1)+ '|| GS: '+str(GS1)+ ' | '+str(GS2)+ ' | '+str(GS3)
                                    case('chainFist'):
                                        SM1 = random.randint(1,6)
                                        SB.roll = 'SM: '+str(SM1)+ '|| GS: '+str(GS1)+ ' | '+str(GS2)+ ' | '+str(GS3)
                                    case('AssaultCanon'):
                                        SM1 = random.randint(1,6)
                                        SB.roll = 'SM: '+str(SM1)+ '|| GS: '+str(GS1)+ ' | '+str(GS2)+ ' | '+str(GS3)
                                    case('flamer'):
                                        SM1 = random.randint(1,6)
                                        SB.roll = 'SM: '+str(SM1)+ '|| GS: '+str(GS1)+ ' | '+str(GS2)+ ' | '+str(GS3)
                                    case('claws'):
                                        SM1 = random.randint(1,6)
                                        if(facing):   
                                            SM2 = random.randint(1,6)
                                            if(SM1 > SM2):
                                                SM1 += 1
                                            else:
                                                SM2 += 1
                                        SB.roll = 'SM: '+str(SM1)+' | '+str(SM2) +'|| GS: '+str(GS1)+ ' | '+str(GS2)+ ' | '+str(GS3)
                                    case('powerSword'):
                                        SM1 = random.randint(1,6)
                                        if(((SM1 < GS1) or (SM1 < GS2) or (SM1 < GS3)) or ((SM2 > SM1) and ((SM2 < GS1) or (SM2 < GS2) or (SM2 < GS3)))):
                                            if((GS1 > GS2) and (GS1 > GS3)):
                                                GS1 = random.randint(1,6)
                                            elif((GS2 > GS1) and (GS2 > GS3)):
                                                GS2 = random.randint(1,6)
                                            else:
                                                GS3 = random.randint(1,6)
                                    case('hammer'):
                                        SM1 = random.randint(1,6) + 1
                                        if(facing):   
                                            GS3 = 0
                                            SB.roll = 'SM: '+str(SM1)+'|| GS: '+str(GS1)+ ' | '+str(GS2)
                                        else:
                                            SB.roll = 'SM: '+str(SM1)+'|| GS: '+str(GS1)+ ' | '+str(GS2)+ ' | '+str(GS3)
                                if(self.clicked_model.rank == 'sergeant'):
                                    SM1 += 1
                                    if((facing) and (self.clicked_model.weapon == 'hammer')):
                                        SB.roll = 'SM: '+str(SM1)+'|| GS: '+str(GS1)+ ' | '+str(GS2)
                                    else:
                                        SB.roll = 'SM: '+str(SM1)+'|| GS: '+str(GS1)+ ' | '+str(GS2)+ ' | '+str(GS3)
                                if(self.clicked_model.guard == True):
                                    if(((SM1 < GS1) or (SM1 < GS2) or (SM1 < GS3)) or ((SM2 != 0) and ((SM2 < GS1) or (SM2 < GS2) or (SM2 < GS3)))):
                                        if((SM2 > SM1) or (SM2 == 0)):
                                            SM1 = random.randint(1,6)
                                        else:
                                            SM2 = random.randint(1,6)
                                        if(self.clicked_model.rank == 'sergeant'):
                                            if((SM1 > SM2) or (SM2 == 0)):
                                                SM1 += 1
                                            else:
                                                SM2 += 1
                                            if(self.clicked_model.weapon == 'hammer'):
                                                if((SM1 > SM2) or (SM2 == 0)):
                                                    SM1 += 1
                                                else:
                                                    SM2 += 1
                                        if((self.clicked_model.weapon == 'claws') and (facing)):
                                            if((SM1 > SM2) or (SM2 == 0)):
                                                SM1 += 1
                                            else:
                                                SM2 += 1
                                        if(SM2 != 0):
                                            SB.roll = 'SM: '+str(SM1)+' | '+str(SM2)+ '|| GS: '+str(GS1)+ ' | '+str(GS2)+ ' | '+str(GS3)
                                        else:
                                            SB.roll = 'SM: '+str(SM1)+ '|| GS: '+str(GS1)+ ' | '+str(GS2)+ ' | '+str(GS3)
                                for row in map: 
                                    for tile in row:
                                        if(tile.occupand in SM_ModellList):
                                            checked = self.vision(tile.occupand, tile)
                                            if(self.selected_tile in checked):
                                                if(self.CP != 0):
                                                    self.Manager.ooc = True
                                                    self.Manager.ooc_models.append(tile.occupand)

                                if(((GS1 > SM1) & (GS1 > SM2)) or ((GS2 > SM1) & (GS2 > SM2)) or ((GS3 > SM1) & (GS3 > SM2))):
                                    self.clicked_tile.is_occupied = False
                                    self.clicked_tile.occupand = None
                                    SM_ModellList.remove(self.clicked_model)
                                    self.cicked_model = None
                                elif((facing == True) & (((SM1 > GS1) & (SM1 > GS2) & (SM1 > GS3)) or ((SM2 > GS1) & (SM2 > GS2) & (SM2 > GS3)))):
                                    self.selected_tile.is_occupied = False
                                    self.selected_tile.occupand = None
                                    GS_ModellList.remove(self.selected_Model)
                                    self.selected_Model = None
                                else: 
                                    self.Manager.melee_turn = True
                                    self.Manager.changestate('turn')
                                    self.run()
                    else:
                        SB.problem = 'Select a Target!'
                else:
                    SB.problem = 'Model needs to face the Target!'

        for row in map: 
            for tile in row:
                if(tile.occupand in SM_ModellList):
                    checked = self.vision(tile.occupand, tile)
                    for tiles in checked:
                        if(tiles.occupand in BL_ModellList):
                            self.Manager.rev_models.append(tiles)
                            checked.remove(tiles)
                        if(self.is_playing == self.player2):
                            if(tiles.occupand == self.selected_Model):
                                if((tile.occupand.jam == False) and (tile.occupand.overwatch == True)):
                                    if(self.distance(tile,tiles) < 14):
                                        self.clicked_tile = self.selected_tile
                                        self.clicked_model = self.selected_Model
                                        self.Manager.save_model = self.selected_Model
                                        self.Manager.save_tile = self.selected_tile
                                        self.selected_tile = tile
                                        self.selected_Model = tile.occupand
                                        self.shoot()
                                        if(not (self.Manager.save_model in GS_ModellList)):
                                            self.Manager.gs_turnaftermove = False
                                        self.selected_tile = self.Manager.save_tile
                                        self.selected_Model = self.Manager.save_model
                    if(self.Manager.rev_models.__len__() != 0):
                        self.Manager.save_model = self.selected_Model
                        self.Manager.save_tile = self.selected_tile
                        self.reveal(self.Manager.rev_models[0])

    def reveal(self, tile):
        self.selected_Model = tile.occupand
        self.selected_tile = tile
        self.Manager.changestate('reveal')
        self.run()
                
    def moveModel(self):
        a = False
        b = False
        c = 0
        match(game.selected_Model.face):
            case(1,0):
                ofset_x = 0
                ofset_y = 1
            case(0,1):
                ofset_x = 1
                ofset_y = 0
            case(-1,0):
                ofset_x = 0
                ofset_y = 1
            case(0,-1):
                ofset_x = 1
                ofset_y = 0
        ofs = game.selected_Model.face
        if((self.clicked_tile != None) & (self.selected_tile != None) & (self.selected_Model != None)): 
            if(self.clicked_tile.is_occupied == False):
                a = True
            else:
                SB.problem = 'Tile cannot be occupied!'
            if((self.is_playing == self.player1) & (self.selected_Model in SM_ModellList)):
                if(((self.selected_tile.x + ofs[0] == self.clicked_tile.x) and (ofs[0] != 0)) or ((self.selected_tile.y + ofs[1] == self.clicked_tile.y) and (ofs[1] != 0))):
                    if((self.selected_Model.AP != 0) | (self.CP != 0)):
                        c = 1
                        b = True
                elif(((self.selected_tile.x - ofs[0] == self.clicked_tile.x) and (ofs[0] != 0)) or ((self.selected_tile.y - ofs[1] == self.clicked_tile.y) and (ofs[1] != 0))):
                    if(self.selected_Model.AP + self.CP >= 2):
                        c = 2
                        b = True
                if((self.clicked_tile.is_wall == True) or ((self.clicked_tile.is_door == True) and (self.clicked_tile.is_open == False)) or (self.clicked_tile.is_entrypoint == True)):
                    b = False
                if((((map[self.selected_tile.y+1][self.selected_tile.x].is_wall) or (map[self.selected_tile.y+1][self.selected_tile.x].is_occupied)) and ((map[self.selected_tile.y-1][self.selected_tile.x].is_wall) or (map[self.selected_tile.y-1][self.selected_tile.x].is_occupied))) or (((map[self.selected_tile.y][self.selected_tile.x+1].is_wall) or (map[self.selected_tile.y][self.selected_tile.x+1].is_occupied)) and ((map[self.selected_tile.y][self.selected_tile.x-1].is_wall) or (map[self.selected_tile.y][self.selected_tile.x-1].is_occupied)))):
                    if(map[self.selected_tile.y + self.selected_Model.face[1]][self.selected_tile.x + self.selected_Model.face[0]].is_occupied == True):
                        if((self.clicked_tile == map[self.selected_tile.y + ofset_y + ofs[1]][self.selected_tile.x + ofset_x + ofs[0]]) or (self.clicked_tile == map[self.selected_tile.y - ofset_y + ofs[1]][self.selected_tile.x - ofset_x + ofs[0]])):
                            b = False
                    elif(map[self.selected_tile.y - self.selected_Model.face[1]][self.selected_tile.x - self.selected_Model.face[0]].is_occupied == True):
                        if((self.clicked_tile == map[self.selected_tile.y + ofset_y - ofs[1]][self.selected_tile.x + ofset_x - ofs[0]]) or (self.clicked_tile == map[self.selected_tile.y - ofset_y - ofs[1]][self.selected_tile.x - ofset_x - ofs[0]])):
                            b = False
                if(self.clicked_tile.is_buring):
                    if(self.selected_tile.is_buring):
                        if((random.randint(1,6)) > 1):
                            self.selected_tile.is_occupied = False
                            SM_ModellList.remove(self.selected_Model)
                            self.selected_tile.occupand = None
                            b = False
                    else:
                        b = False
            if((self.is_playing == self.player2) & (self.selected_Model in BL_ModellList)):
                if((self.selected_Model in BL_ModellList) and (self.selected_tile.is_lurkingpoint == True) and (self.clicked_tile.is_entrypoint == True)):
                    if((map[self.clicked_tile.y][self.clicked_tile.x - 1].is_wall == False) and (map[self.clicked_tile.y][self.clicked_tile.x - 1].is_lurkingpoint == False)):
                        self.clicked_tile = map[self.clicked_tile.y][self.clicked_tile.x - 1]
                        if(self.clicked_tile.is_occupied):
                            a = False
                    elif((map[self.clicked_tile.y][self.clicked_tile.x + 1].is_wall == False) and (map[self.clicked_tile.y][self.clicked_tile.x + 1].is_lurkingpoint == False)):
                        self.clicked_tile = map[self.clicked_tile.y][self.clicked_tile.x + 1]
                        if(self.clicked_tile.is_occupied):
                            a = False
                    elif((map[self.clicked_tile.y - 1][self.clicked_tile.x].is_wall == False) and (map[self.clicked_tile.y - 1][self.clicked_tile.x].is_lurkingpoint == False)):
                        self.clicked_tile = map[self.clicked_tile.y - 1][self.clicked_tile.x]
                        if(self.clicked_tile.is_occupied):
                            a = False
                    else:
                        self.clicked_tile = map[self.clicked_tile.y + 1][self.clicked_tile.x]
                        if(self.clicked_tile.is_occupied):
                            a = False
                    b = True
                    if(self.clicked_tile.is_buring):
                        b = False
                    if(self.selected_Model.AP == 0):
                        b = False
                    if(b):
                        c = 1

            if((self.is_playing == self.player2) & ((self.selected_Model in GS_ModellList) or (self.selected_Model in BL_ModellList)) and (self.selected_tile.is_lurkingpoint == False)):
                if(((self.selected_tile.x + ofs[0] == self.clicked_tile.x) and (ofs[0] != 0)) or ((self.selected_tile.y + ofs[1] == self.clicked_tile.y) and (ofs[1] != 0))):
                    if(self.selected_Model.AP != 0):
                        c = 1
                        b = True
                elif(((self.selected_tile.x - ofs[0] == self.clicked_tile.x) and (ofs[0] != 0)) or ((self.selected_tile.y - ofs[1] == self.clicked_tile.y) and (ofs[1] != 0))):
                    if(self.selected_Model in GS_ModellList):
                        if(self.selected_Model.AP >= 2):
                            c = 2
                            b = True
                    if(self.selected_Model in BL_ModellList):
                        if(self.selected_Model.AP != 0):
                            c = 1
                            b = True
                elif(((self.selected_tile.x + ofset_x == self.clicked_tile.x) and (ofset_x != 0)) or ((self.selected_tile.x - ofset_x == self.clicked_tile.x) and (ofset_x != 0)) or ((self.selected_tile.y + ofset_y == self.clicked_tile.y) and (ofset_y != 0)) or ((self.selected_tile.y - ofset_y == self.clicked_tile.y) and (ofset_y != 0))):
                    if(self.selected_Model.AP != 0):
                        c = 1
                        b = True
                if((self.clicked_tile.is_wall == True) or ((self.clicked_tile.is_door == True) and (self.clicked_tile.is_open == False)) or (self.clicked_tile.is_entrypoint == True)):
                    b = False
                if((((map[self.selected_tile.y+1][self.selected_tile.x].is_wall) or (map[self.selected_tile.y+1][self.selected_tile.x].is_occupied)) and ((map[self.selected_tile.y-1][self.selected_tile.x].is_wall) or (map[self.selected_tile.y-1][self.selected_tile.x].is_occupied))) or (((map[self.selected_tile.y][self.selected_tile.x+1].is_wall) or (map[self.selected_tile.y][self.selected_tile.x+1].is_occupied)) and ((map[self.selected_tile.y][self.selected_tile.x-1].is_wall) or (map[self.selected_tile.y][self.selected_tile.x-1].is_occupied)))):
                    if(map[self.selected_tile.y + self.selected_Model.face[1]][self.selected_tile.x + self.selected_Model.face[0]].is_occupied == True):
                        if((self.clicked_tile == map[self.selected_tile.y + ofset_y + ofs[1]][self.selected_tile.x + ofset_x + ofs[0]]) or (self.clicked_tile == map[self.selected_tile.y - ofset_y + ofs[1]][self.selected_tile.x - ofset_x + ofs[0]])):
                            b = False
                    elif(map[self.selected_tile.y - self.selected_Model.face[1]][self.selected_tile.x - self.selected_Model.face[0]].is_occupied == True):
                        if((self.clicked_tile == map[self.selected_tile.y + ofset_y - ofs[1]][self.selected_tile.x + ofset_x - ofs[0]]) or (self.clicked_tile == map[self.selected_tile.y - ofset_y - ofs[1]][self.selected_tile.x - ofset_x - ofs[0]])):
                            b = False
                if(self.clicked_tile.is_buring):
                    if(self.selected_tile.is_buring):
                        if((random.randint(1,6)) > 1):
                            self.selected_tile.is_occupied = False
                            if(self.selected_Model in GS_ModellList):
                                GS_ModellList.remove(self.selected_Model)
                            elif(self.selected_Model in BL_ModellList):
                                BL_ModellList.remove(self.selected_Model)
                            elif(self.selected_Model in SM_ModellList):
                                SM_ModellList.remove(self.selected_Model)
                            self.selected_tile.occupand = None
                            b = False
                    else:
                        b = False

                if(self.selected_Model in GS_ModellList):
                    if(self.Manager.gs_moveturn == True):
                        self.Manager.gs_moveturn = False
                        if(c == 2):
                            c = 1 
                        else: 
                            c = 0
        else:
            SB.problem = 'Select a Tile!'
        
        if(b == False):
            if(a == True):
                SB.problem = 'Cannot go there!'

        if(a & b):
            self.redAP(self.selected_Model, c)

            game.clicked_tile.occupand = game.selected_tile.occupand
            game.selected_tile.is_occupied = False
            game.clicked_tile.is_occupied = True
            game.selected_tile.occupand = None
            game.selected_tile = game.clicked_tile
            game.clicked_tile = None
            
            self.Manager.save_model = self.selected_Model
            self.Manager.save_tile = self.selected_tile

            if(self.is_playing == self.player1):
                self.Manager.save_model = None
                self.Manager.save_tile = None
                self.selected_Model.overwatch = False
                self.selected_Model.guard = False
                lis = game.vision(self.selected_Model, self.selected_tile)
                remlis = []
                for tile in lis:
                    if((tile.is_occupied == False) and ((tile.is_door == False) or (tile.is_open == True))):
                        remlis.append(tile)
                    elif(tile.occupand in SM_ModellList):
                        remlis.append(tile)
                    elif(tile.occupand in BL_ModellList):
                        self.Manager.rev_models.append(tile)
                        remlis.append(tile)
                for tile in remlis:
                    for obj in lis:
                        if tile == obj:
                            lis.remove(tile)
                self.selected_Model.susf = False
                if(self.Manager.rev_models.__len__() != 0):
                    self.Manager.save_model = self.selected_Model
                    self.Manager.save_tile = self.selected_tile
                    self.reveal(self.Manager.rev_models[0])
                elif(lis != []):
                    if(self.Manager.givestate() != 'ooc'):
                        if((self.selected_Model.weapon != 'claws') and (self.selected_Model.weapon != 'flamer')):
                            self.Manager.SM_move = True
                            SB.hint = 'You have a free shoot action.'
            elif(self.is_playing == self.player2):
                if(self.selected_Model in GS_ModellList):
                    self.Manager.gs_turnaftermove = True
                    self.clicked_model = self.selected_Model
                    self.clicked_tile = self.selected_tile

                    for row in map: 
                        for tile in row:
                            if(tile.occupand in SM_ModellList):
                                checked = self.vision(tile.occupand, tile)
                                if(self.selected_tile in checked):
                                    if(self.CP != 0):
                                        self.Manager.ooc = True
                                        self.Manager.ooc_models.append(tile.occupand)
                                if(tile.occupand.overwatch == True):
                                    if((tile.occupand.jam == False) & (self.clicked_tile in checked)):
                                        if(self.distance(tile, self.Manager.save_tile) < 14):
                                            self.selected_Model = tile.occupand
                                            self.selected_tile = tile
                                            self.shoot()
                                            if(not (self.Manager.save_model in GS_ModellList)):
                                                self.Manager.gs_turnaftermove = False
                                                self.Manager.changestate('runP2')
                                                game.run()
                                            self.selected_Model = self.Manager.save_model
                                            self.selected_tile = self.Manager.save_tile
                                for tile in checked:
                                    if(tile.occupand in BL_ModellList):
                                        self.Manager.rev_models.append(tile)
                                        checked.remove(tile)
                                if(self.Manager.rev_models.__len__() != 0):
                                    self.Manager.save_model = self.selected_Model
                                    self.Manager.save_tile = self.selected_tile
                                    self.reveal(self.Manager.rev_models[0])
                    self.clicked_model = None
                    self.clicked_tile = None
                if(self.selected_Model in BL_ModellList):
                    c = False
                    for row in map:
                        for tile in row:
                            if(tile.occupand in SM_ModellList):
                                seen = self.vision(tile.occupand, tile)
                                for model in seen:
                                    if(model == self.selected_tile):
                                        c = True
                    if(c):
                        if(a & b):
                            self.selected_Model.AP +=1
                        SB.problem = 'Cannot go into line of sight!'
                        self.selected_tile.is_occupied = False
                        self.Manager.save_tile.occupand = self.Manager.save_model
                        self.selected_tile.occupand = None
                        self.Manager.save_tile.is_occupied = True
                        self.selected_tile = self.Manager.save_tile
                        self.selected_Model = self.Manager.save_model
                        self.Manager.save_model = None
                        self.Manager.save_tile = None
                        c = False

    def run(self):
        self.states[self.Manager.givestate()].run()
        pygame.display.update()
        
game = Game()

class gamestateTurn:
    def __init__(self) -> None:
        self.gameStateManager = gameStateManager
    def run(self):
        self.turn_right_image = pygame.image.load('Pictures/Turn_right.png')
        self.turn_left_image = pygame.image.load('Pictures/Turn_left.png')
        self.noturn_image = pygame.image.load('Pictures/cease.png')
        self.fullturn_image = pygame.image.load('Pictures/Turn_half.png')
        self.face_image = pygame.image.load('Pictures/melee_face.png')

        self.turnright_button = Button(930, 500, self.turn_right_image, 1)
        self.turnleft_button = Button(810, 500, self.turn_left_image, 1)
        self.noturn_button = Button(870, 500, self.noturn_image, 1)
        self.fullturn_button = Button(990, 500, self.fullturn_image, 1)
        self.face_button = Button(930, 500, self.face_image, 1)

        while(True):
            pressed = False
            u = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit
                    sys.exit
                if event.type == pygame.MOUSEWHEEL:
                    for row in map:
                        for tile in row:
                            tile.size += event.y
                            tile.rect.topleft = ((tile.x * tile.size), (tile.y * tile.size))
                    screen.fill((50,50,50))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for row in map:
                            for tile in row:
                                tile.yb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_w:
                        for row in map:
                            for tile in row:
                                tile.yb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_a:
                        for row in map:
                            for tile in row:
                                tile.xb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_d:
                        for row in map:
                            for tile in row:
                                tile.xb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                                
                    screen.fill((50, 50, 50))
            for row in map:
                for tile in row: 
                    tile.render(screen)
            if(self.gameStateManager.melee_turn == True):
                SB.hint = 'Turn to attacker?'
            elif((self.gameStateManager.gs_moveturn == True) and (self.gameStateManager.turn == False)):
                SB.hint = 'You have a free Move.'
            elif(self.gameStateManager.turn == True):
                SB.hint = 'Choose the facing of the modell.'
            else:
                SB.hint = 'Turn the model using the buttons.'
            
            SB.display(screen)
            BB.display(screen)
            
            if(self.gameStateManager.melee_turn == True):
                if(self.face_button.draw(screen)):
                    match(game.selected_Model.face):
                        case(1,0): game.clicked_model.face = (-1,0)
                        case(0,1): game.clicked_model.face = (0,-1)
                        case(-1,0): game.clicked_model.face = (1,0)
                        case(0,-1): game.clicked_model.face = (0,1)
                    pressed = True
                    self.gameStateManager.melee_turn = False

            else:
                if(self.turnleft_button.draw(screen)):
                    if((game.is_playing == game.player1) and (game.selected_Model.AP + game.CP != 0)):
                        game.selected_Model.guard = False
                        game.selected_Model.overwatch = False
                        self.gameStateManager.SM_move = True
                        a = True
                    if((game.is_playing == game.player2) and (game.selected_Model.AP != 0) and (self.gameStateManager.gs_turnaftermove == False) and (self.gameStateManager.turn == False)):
                        self.gameStateManager.gs_moveturn = True
                        a = True
                    if((self.gameStateManager.turn == True) or (self.gameStateManager.gs_turnaftermove == True)):
                        a = True
                    if(a):
                        u = True
                        match(game.selected_Model.face):
                            case(1,0): game.selected_Model.face = (0,-1)
                            case(0,1): game.selected_Model.face = (1,0)
                            case(-1,0): game.selected_Model.face = (0,1)
                            case(0,-1): game.selected_Model.face = (-1,0)
                        if((self.gameStateManager.turn == False) and (self.gameStateManager.gs_turnaftermove == False)):
                            game.redAP(game.selected_Model,1)
                        else:
                            self.gameStateManager.gs_turnaftermove = False
                        a = False

                if(self.turnright_button.draw(screen)):
                    if((game.is_playing == game.player1) and (game.selected_Model.AP + game.CP != 0)):
                        game.selected_Model.guard = False
                        game.selected_Model.overwatch = False
                        self.gameStateManager.SM_move = True
                        a = True
                    if((game.is_playing == game.player2) and (game.selected_Model.AP != 0) and (self.gameStateManager.gs_turnaftermove == False) and (self.gameStateManager.turn == False)):
                        self.gameStateManager.gs_moveturn = True
                        a = True
                    if((self.gameStateManager.turn == True) or (self.gameStateManager.gs_turnaftermove == True)):
                        a = True
                    if(a):
                        u = True
                        match(game.selected_Model.face):
                            case(1,0): game.selected_Model.face = (0,1)
                            case(0,1): game.selected_Model.face = (-1,0)
                            case(-1,0): game.selected_Model.face = (0,-1)
                            case(0,-1): game.selected_Model.face = (1,0)
                        if((self.gameStateManager.turn == False) and (self.gameStateManager.gs_turnaftermove == False)):
                            game.redAP(game.selected_Model,1)
                        else:
                            self.gameStateManager.gs_turnaftermove = False
                        a = False

                if(((game.is_playing == game.player2) or (self.gameStateManager.turn == True)) and (self.gameStateManager.gs_turnaftermove == False)):
                    if(self.fullturn_button.draw(screen)):
                        if((game.selected_Model.AP != 0) or (self.gameStateManager.turn == True)):
                            u = True
                            match(game.selected_Model.face):
                                case(1,0): game.selected_Model.face = (-1,0)
                                case(0,1): game.selected_Model.face = (0,-1)
                                case(-1,0): game.selected_Model.face = (1,0)
                                case(0,-1): game.selected_Model.face = (0,1)
                            if(self.gameStateManager.turn == False):
                                game.redAP(game.selected_Model,1)

            if(self.noturn_button.draw(screen)):
                pressed = True
                if(self.gameStateManager.turn == True):
                    self.gameStateManager.turn = False
                    game.clicked_model = None
                    if(self.gameStateManager.rev_count == 0):
                        game.selected_Model = None
                        game.selected_tile = None
                        if(game.is_playing == game.player2):
                            self.gameStateManager.changestate('runP2')
                            game.run()
                        else:
                            if(self.gameStateManager.savestate == 'reroll'):
                                self.gameStateManager.changestate('reroll')
                                self.gameStateManager.savestate = None
                                game.run()
                            elif(self.gameStateManager.save_model in SM_ModellList):
                                game.selected_tile = self.gameStateManager.save_tile
                                game.selected_Model = self.gameStateManager.save_model
                                self.gameStateManager.changestate('actP1')
                                game.run()
                            else:
                                self.gameStateManager.changestate('runP1')
                                game.run()
                self.gameStateManager.melee_turn = False
            
            if(u):
                u = False
                if(game.is_playing == game.player1):
                    lis = game.vision(game.selected_Model, game.selected_tile)
                    for tile in lis:
                        if(tile.is_occupied == False):
                            lis.remove(tile)
                        elif(tile.occupand in SM_ModellList):
                            lis.remove(tile)
                        elif(tile.occupand in GS_ModellList):
                            lis.remove(tile)
                        elif(tile.occupand in BL_ModellList):
                            self.gameStateManager.rev_models.append(tile)
                            lis.remove(tile)
                    game.selected_Model.susf = False
                    if(self.gameStateManager.rev_models.__len__() != 0):
                        self.gameStateManager.save_model = game.selected_Model
                        self.gameStateManager.save_tile = game.selected_tile
                        game.reveal(self.gameStateManager.rev_models[0])

                elif(game.is_playing == game.player2):
                    game.clicked_model = game.selected_Model
                    game.clicked_tile = game.selected_tile
                    for row in map: 
                            for tile in row:
                                if(tile.occupand in SM_ModellList):
                                    checked = game.vision(tile.occupand, tile)
                                    if(game.selected_tile in checked):
                                        if(game.CP != 0):
                                            self.gameStateManager.ooc = True
                                            self.gameStateManager.ooc_models.append(tile.occupand)
                                    if(tile.occupand.overwatch == True):
                                        if((tile.occupand.jam == False) & (game.selected_tile in checked)):
                                            if(game.distance(tile, game.selected_tile) < 14):
                                                self.gameStateManager.save_tile = game.selected_tile
                                                self.gameStateManager.save_model = game.selected_Model
                                                game.selected_Model = tile.occupand
                                                game.selected_tile = tile
                                                game.clicked_tile = self.gameStateManager.save_tile
                                                game.clicked_model = self.gameStateManager.save_model
                                                game.shoot()
                                                if(not (self.gameStateManager.save_model in GS_ModellList)):
                                                    self.gameStateManager.gs_turnaftermove = None
                                                game.selected_Model = self.gameStateManager.save_model
                                                game.selected_tile = self.gameStateManager.save_tile
                                    for tile in checked:
                                        if(tile.occupand in BL_ModellList):
                                            self.gameStateManager.rev_models.append(tile)
                                            checked.remove(tile)
                                    if(self.gameStateManager.rev_models.__len__() != 0):
                                        self.gameStateManager.save_model = game.selected_Model
                                        self.gameStateManager.save_tile = game.selected_tile
                                        game.reveal(self.gameStateManager.rev_models[0])
                   
            if(pressed):
                if(self.gameStateManager.rev_count != 0):
                    self.gameStateManager.changestate('reveal')
                    game.run()
                elif(game.is_playing == game.player1):
                    if(self.gameStateManager.ooc == True):
                        game.is_playing = game.player2
                        self.gameStateManager.ooc = False
                        self.gameStateManager.ooc_models = []
                        game.selected_Model = None
                        game.selected_tile = None
                        game.clicked_tile = None
                        game.clicked_model = None
                        self.gameStateManager.changestate('runP2')
                        game.run()
                    elif(self.gameStateManager.savestate == 'reroll'):
                        self.gameStateManager.changestate('reroll')
                        self.gameStateManager.savestate = None
                        game.run()
                    else:
                        self.gameStateManager.changestate('actP1')
                        game.run()
                else:
                    self.gameStateManager.changestate('actP2')
                    game.run()

            pygame.display.update()
            
class gamestateNewGame:
    def __init__(self) -> None:
        self.gameStateManager = gameStateManager
    def run(self):
        p1 = True
        font = pygame.font.SysFont('Bahnschrift', 50)
        while (True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    # Check if the key is an alphanumeric character or space
                    if event.unicode.isalnum() or event.unicode.isspace() and not (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER):
                        if(p1):
                            game.player1 += event.unicode
                        else:
                            game.player2 += event.unicode
                    elif event.key == pygame.K_BACKSPACE:
                        if(p1):
                            game.player1 = game.player1[:-1]
                        else:
                            game.player2 = game.player2[:-1]
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if(p1 and game.player1 != ''):p1 = False
                        elif(((game.player2 != '') and (game.player2 != game.player1)) and (game.player2 != game.player1)):
                            game.is_playing = game.player1
                            self.gameStateManager.changestate('level')
                            screen.fill((50, 50, 50))
                            game.run()

            # Clear the screen
            screen.fill((50, 50, 50))

            # Render the input string
            if(p1):
                hint_surface = font.render('Spieler 1:',True, (0,0,0))
                text_surface = font.render(game.player1, True, (0, 0, 0))
            else:
                hint_surface = font.render('Spieler 2:', True, (0,0,0))
                text_surface = font.render(game.player2, True, (0,0,0))
            screen.blit(hint_surface, (50,50))
            screen.blit(text_surface, (50, 150))
            pygame.display.update()

class SM_win:
    def __init__(self) -> None:
        self.Manager = gameStateManager

    def run(self):
        screen.fill((50, 50, 50))
        cease_image = pygame.image.load('Pictures/cease.png')
        end_button = Button(50,150,cease_image,(1))
        font = pygame.font.SysFont('Bahnschrift', 50)
        hint_surface = font.render(game.player1 + ' Winns! Congratulations',True, (0,0,0))
        screen.blit(hint_surface, (50,50))
        while (True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        
            if(end_button.draw(screen)):
                self.Manager.changestate('main')
                game.run()
            pygame.display.update()

class GS_win:
    def __init__(self) -> None:
        self.Manager = gameStateManager

    def run(self):
        screen.fill((50, 50, 50))
        cease_image = pygame.image.load('Pictures/cease.png')
        end_button = Button(50,150,cease_image,(1))
        font = pygame.font.SysFont('Bahnschrift', 50)
        hint_surface = font.render(game.player2 + ' Winns! Congratulations',True, (0,0,0))
        screen.blit(hint_surface, (50,50))
        while (True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        
            if(end_button.draw(screen)):
                self.Manager.changestate('main')
                game.run()
            pygame.display.update()

class gamestate_level:
    def __init__(self) -> None:
        self.Manager = gameStateManager
        self.y = 50

    def run(self):
        lvl1_image = pygame.image.load('Pictures/cease.png')
        lvl1_button = Button(200,self.y,lvl1_image,1)

        lvl2_button = Button(200, self.y + 70, lvl1_image, 1)

        while(True):
            lvl1_button.rect.topleft = (200,self.y)
            lvl2_button.rect.topleft = (200,self.y + 70)

            screen.fill((50, 50, 50))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEWHEEL:
                    self.y -= event.y

            if(lvl1_button.draw(screen)):
                game.level = 1
                removetiles = []
                
                for tile in map[0]:
                    if(tile.x < 19) or (tile.x > 23):
                        removetiles.append(tile)
                    else:
                        tile.is_wall = True

                for tile in map[1]:
                    if(tile.x < 19) or (tile.x > 23):
                        removetiles.append(tile)
                    elif(tile.x == 19 or tile.x == 23):
                        tile.is_wall = True

                for tile in map[2]:
                    if(tile.x < 19) or (tile.x > 23):
                        removetiles.append(tile)
                    elif(tile.x == 19 or tile.x == 23):
                        tile.is_wall = True

                for tile in map[3]:
                    if(tile.x < 19) or (tile.x > 23):
                        removetiles.append(tile)
                    elif(tile.x == 19 or tile.x == 23):
                        tile.is_wall = True

                for tile in map[4]:
                    if(tile.x < 19) or (tile.x > 23):
                        removetiles.append(tile)
                    elif(tile.x != 21):
                        tile.is_wall = True
                    else:
                        tile.is_door = True
                        
                for tile in map[5]:
                    if(tile.x < 20) or (tile.x > 22 and tile.x < 25) or (tile.x > 29):
                        removetiles.append(tile)
                    elif(tile.x != 21):
                        tile.is_wall = True

                for tile in map[6]:
                    if(tile.x < 20) or (tile.x > 22 and tile.x < 25) or (tile.x > 29):
                        removetiles.append(tile)
                    elif(tile.x == 20 or tile.x == 22 or tile.x == 25 or tile.x == 29):
                        tile.is_wall = True
                    elif(tile.x > 25 and tile.x <29):
                        tile.is_lurkingpoint = True

                for tile in map[7]:
                    if(tile.x < 20) or (tile.x > 22 and tile.x < 25) or (tile.x > 29):
                        removetiles.append(tile)
                    elif(tile.x == 20 or tile.x == 22 or (tile.x > 24 and tile.x != 27)):
                        tile.is_wall = True
                    elif(tile.x == 27):
                        tile.is_entrypoint = True

                for tile in map[8]:
                    if(tile.x < 14) or (tile.x == 29) or (tile.x > 29):
                        removetiles.append(tile)
                    elif(tile.x != 21 and tile.x != 27):
                        tile.is_wall = True

                for tile in map[9]:
                    if(tile.x < 14) or (tile.x == 29) or (tile.x > 29):
                        removetiles.append(tile)
                    elif(tile.x == 14 or tile.x == 28):
                        tile.is_wall = True
                    elif(tile.x == 16):
                        tile.is_door = True

                for tile in map[10]:
                    if(tile.x < 6 or ( tile.x > 10 and tile.x < 14) or tile.x == 29) or (tile.x > 29):
                        removetiles.append(tile)
                    elif((tile.x > 5 and tile.x < 11) or tile.x == 14 or (tile.x > 15 and tile.x < 21) or (tile.x > 21 and tile.x <27) or tile.x ==28):
                        tile.is_wall = True
                        
                for tile in map[11]:
                    if(tile.x >= 29):
                        removetiles.append(tile)
                    elif(tile.x < 7 or (tile.x > 9 and tile.x < 15) or (tile.x > 15 and tile.x < 21) or (tile.x > 21 and tile.x <27) or tile.x ==28):
                        tile.is_wall = True

                for tile in map[12]:
                    if(tile.x >= 29):
                        removetiles.append(tile)
                    elif(tile.x == 0 or tile.x == 28):
                        tile.is_wall = True
                    elif(tile.x == 6 or tile.x == 10):
                        tile.is_door = True

                for tile in map[13]:
                    if(tile.x >= 29):
                        removetiles.append(tile)
                    elif(tile.x < 7 or (tile.x > 9 and tile.x < 21) or (tile.x > 21 and tile.x <27) or tile.x ==28):
                        tile.is_wall = True

                for tile in map[14]:
                    if(tile.x < 6 or (tile.x > 10 and tile.x < 20) or tile.x == 23 or tile.x == 24) or (tile.x > 29):
                        removetiles.append(tile)
                    elif(tile.x == 6 or tile.x == 7 or tile.x == 9 or tile.x == 10 or tile.x == 20 or tile.x == 22 or tile.x ==25 or tile.x == 26 or tile.x == 28 or tile.x == 29):
                        tile.is_wall = True
                    elif(tile.x == 8):
                        tile.is_door = True
                    elif(tile.x == 27):
                        tile.is_entrypoint = True

                for tile in map[15]:
                    if(tile.x < 7 or (tile.x > 9 and tile.x < 20) or tile.x == 23 or tile.x == 24) or (tile.x > 29):
                        removetiles.append(tile)
                    elif(tile.x == 7 or tile.x == 9 or tile.x == 20 or tile.x == 22 or tile.x == 25 or tile.x == 29):
                        tile.is_wall = True
                    elif(tile.x > 25 and tile.x < 29):
                        tile.is_lurkingpoint = True

                for tile in map[16]:
                    if(tile.x < 7 or (tile.x > 9 and tile.x < 20) or tile.x == 23 or tile.x == 24) or (tile.x > 29):
                        removetiles.append(tile)
                    elif(tile.x == 7 or tile.x == 9 or tile.x == 20 or tile.x == 22 or tile.x >24):
                        tile.is_wall = True
                    elif(tile.x > 25 and tile.x < 29):
                        tile.is_lurkingpoint = True

                for tile in map[17]:
                    if(tile.x < 7 or (tile.x > 14 and tile.x < 20) or tile.x > 22):
                        removetiles.append(tile)
                    elif(tile.x == 7 or (tile.x > 8 and tile.x < 15) or tile.x == 20 or tile.x == 22):
                        tile.is_wall = True

                for tile in map[18]:
                    if(tile.x < 7 or tile.x == 15 or tile.x == 16 or tile.x > 25):
                        removetiles.append(tile)
                    elif(tile.x == 7 or tile.x == 9 or tile.x == 10 or tile.x == 14 or (tile.x > 16 and  tile.x < 21) or (tile.x > 21 and tile.x < 26)):
                        tile.is_wall = True
                    elif(tile.x > 10 and tile.x < 14):
                        tile.is_lurkingpoint = True

                for tile in map[19]:
                    if(tile.x < 6 or tile.x == 15 or tile.x == 16 or tile.x > 25):
                        removetiles.append(tile)
                    elif(tile.x == 6 or tile.x == 7 or tile.x == 9 or tile.x == 10 or tile.x == 11 or tile.x == 13 or tile.x == 14 or tile.x == 17 or tile.x == 19 or tile.x == 20 or tile.x == 22 or tile.x == 23 or tile.x == 25):
                        tile.is_wall = True
                    elif(tile.x == 18 or tile.x == 24):
                        tile.is_lurkingpoint = True
                    elif(tile.x == 12): 
                        tile.is_entrypoint = True
                    elif(tile.x == 8): 
                        tile.is_door = True

                for tile in map[20]:
                    if(tile.x < 6 or tile.x == 14 or tile.x == 15 or tile.x == 16 or tile.x > 25):
                        removetiles.append(tile)
                    elif(tile.x == 6 or tile.x == 10 or tile.x == 11 or tile.x == 13 or tile.x == 17 or tile.x == 25):
                        tile.is_wall = True
                    elif(tile.x == 18 or tile.x == 24):
                        tile.is_lurkingpoint = True
                    elif(tile.x == 19 or tile.x == 23): 
                        tile.is_entrypoint = True

                for tile in map[21]:
                    if(tile.x < 6 or tile.x == 14 or tile.x == 15 or tile.x == 16 or tile.x > 25):
                        removetiles.append(tile)
                    elif(tile.x == 6 or tile.x == 13 or tile.x == 17 or tile.x == 19 or tile.x == 25 or (tile.x > 19 and tile.x < 24)):
                        tile.is_wall = True
                    elif(tile.x == 18 or tile.x == 24):
                        tile.is_lurkingpoint = True
                    elif(tile.x == 11):
                        tile.is_door = True

                for tile in map[22]:
                    if(tile.x < 6 or tile.x == 14 or tile.x == 15 or tile.x == 16 or tile.x > 25 or (tile.x > 19 and tile.x < 23)):
                        removetiles.append(tile)
                    elif(tile.x == 6 or tile.x == 10 or tile.x == 11 or tile.x == 13 or (tile.x > 16 and tile.x < 20) or (tile.x > 22 and tile.x < 28)):
                        tile.is_wall = True

                for tile in map[23]:
                    if(tile.x < 6 or tile.x > 14):
                        removetiles.append(tile)
                    elif((tile.x > 5 and tile.x < 12) or tile.x == 14 or tile.x == 13):
                        tile.is_wall = True
                    elif(tile.x == 12):
                        tile.is_entrypoint = True

                for tile in map[24]:
                    if(tile.x < 10 or tile.x > 14):
                        removetiles.append(tile)
                    elif(tile.x == 10 or tile.x == 14):
                        tile.is_wall = True
                    elif(tile.x > 10 and tile.x < 14):
                        tile.is_lurkingpoint = True

                for tile in map[25]:
                    if(tile.x < 10 or tile.x > 14):
                        removetiles.append(tile)
                    elif(tile.x > 9 and tile.x < 15):
                        tile.is_wall = True

                for tile in map[26]:
                    removetiles.append(tile)

                for tile in map[27]:
                    removetiles.append(tile)

                for tile in map[28]:
                    removetiles.append(tile)

                for tile in map[29]:
                    removetiles.append(tile)

                for tile in map[30]:
                    removetiles.append(tile)

                for tile in map[31]:
                    removetiles.append(tile)

                for tile in map[32]:
                    removetiles.append(tile)

                for tile in map[33]:
                    removetiles.append(tile)

                for tile in map[34]:
                    removetiles.append(tile)

                for ins in removetiles:
                    for row in map:
                        for tile in row:
                            if(tile == ins):
                                tile.is_used = False                                                                                                                                                           
                for tile in [map[12][1],map[12][2],map[12][3], map[12][4],map[12][5]]:
                    tile.is_SMentry = True
                for model in [SpaceMarine('flamer', 'Battlebrother'),SpaceMarine('powerSword','sergeant'),SpaceMarine('fist','Battlebrother'),SpaceMarine('fist','Battlebrother'),SpaceMarine('fist','Battlebrother')]:
                    SM_ModellList.append(model)

                game.reinforcement = 2
                game.gs_start = 2

                gameStateManager.sections = [[map[12][1],map[12][2],
                                              map[12][3],map[12][4],map[12][5]],
                                              [map[12][6],map[12][7],map[12][8],map[12][9],map[12][10],map[11][7],map[11][8],map[11][9],map[13][7],map[13][8],map[13][9],map[14][8]],
                                              [map[12][11],map[12][12],map[12][13]],
                                              [map[15][8],map[16][8],map[17][8],map[18][8]],
                                              [map[19][8],map[20][7],map[20][8],map[20][9],map[21][7],map[21][8],map[21][9],map[21][10],map[22][7],map[22][8],map[22][9]],
                                              [map[21][11],map[21][12],map[20][12],map[22][12]],
                                              [map[12][14],map[12][15],map[11][15],map[12][16]],
                                              [map[10][15],map[9][15],map[9][16]],
                                              [map[9][17],map[9][18],map[9][19]],
                                              [map[9][20],map[9][21],map[9][22],map[8][21],map[10][21]],
                                              [map[7][21],map[6][21],map[5][21]],
                                              [map[4][21],map[3][20],map[3][21],map[3][22],map[2][20],map[2][21],map[2][22],map[1][20],map[1][21],map[1][22]],
                                              [map[9][23],map[9][24],map[9][25]],
                                              [map[9][26],map[9][27],map[8][27],map[10][27]],
                                              [map[11][27],map[12][27],map[12][26],map[13][27]],
                                              [map[12][25],map[12][24],map[12][23]],
                                              [map[12][22],map[12][21],map[12][20],map[13][21],map[11][21]],
                                              [map[14][21],map[15][21],map[16][21],map[17][21],map[18][21]],
                                              [map[19][21],map[20][21],map[20][20],map[20][22]],
                                              [map[12][19],map[12][18],map[12][17]]]
                screen.fill((50,50,50))
                x = 0
                liste = [1,4,6,8,16,18,14,12,10]
                while (x < liste.__len__()):
                    for tile in gameStateManager.sections[liste[x]]:
                        tile.group = 'b'
                    x += 1

                self.Manager.changestate('cuts')
                game.run()

            if(lvl2_button.draw(screen)):
                game.level = 2
                removetiles = []

                for tile in map[0]:
                    if(tile.x < 2) or (tile.x > 6 and tile.x < 15) or (tile.x > 25):
                        removetiles.append(tile)
                    else:
                        tile.is_wall = True

                for tile in map[1]:
                    if(tile.x < 2) or (tile.x > 6 and tile.x < 15) or (tile.x > 25):
                        removetiles.append(tile)
                    elif(tile.x == 2) or (tile.x == 6) or (tile.x == 15) or (tile.x == 25):
                        tile.is_wall = True
                    elif(tile.x > 2 and tile.x < 6):
                        tile.is_lurkingpoint = True

                for tile in map[2]:
                    if(tile.x > 6 and tile.x < 15) or (tile.x > 25):
                        removetiles.append(tile)
                    elif(tile.x < 4) or (tile.x > 4 and tile.x < 7) or (tile.x == 15) or (tile.x > 16 and tile.x < 24) or (tile.x == 25):
                        tile.is_wall = True
                    elif(tile.x == 4):
                        tile.is_entrypoint = True

                for tile in map[3]:
                    if(tile.x > 5 and tile.x < 15) or (tile.x > 17 and tile.x < 23) or (tile.x > 25):
                        removetiles.append(tile)
                    elif(tile.x == 0) or (tile.x == 2) or (tile.x == 3) or (tile.x == 5) or (tile.x == 15) or (tile.x == 17) or (tile.x == 23) or (tile.x == 25):
                        tile.is_wall = True
                    elif(tile.x == 1):
                        tile.is_lurkingpoint = True

                for tile in map[4]:
                    if(tile.x > 5 and tile.x < 15) or (tile.x > 17 and tile.x < 23) or (tile.x > 25):
                        removetiles.append(tile)
                    elif(tile.x == 0) or (tile.x == 5) or (tile.x == 15) or (tile.x == 17) or (tile.x == 23) or (tile.x == 25):
                        tile.is_wall = True
                    elif(tile.x == 1):
                        tile.is_lurkingpoint = True
                    elif(tile.x == 2):
                        tile.is_entrypoint = True

                for tile in map[5]:
                    if(tile.x > 5 and tile.x < 15) or (tile.x > 30):
                        removetiles.append(tile)
                    elif(tile.x == 0) or (tile.x == 2) or (tile.x == 3) or (tile.x == 5) or (tile.x == 15) or (tile.x > 16 and tile.x < 24) or (tile.x > 24 and tile.x < 31):
                        tile.is_wall = True
                    elif(tile.x == 1):
                        tile.is_lurkingpoint = True

                for tile in map[6]:
                    if(tile.x > 30):
                        removetiles.append(tile)
                    elif(tile.x == 0) or (tile.x == 2) or (tile.x == 3) or (tile.x > 4 and tile.x < 16) or (tile.x == 17) or (tile.x == 18) or (tile.x == 22) or (tile.x == 23) or (tile.x == 25) or (tile.x == 26) or (tile.x == 30):
                        tile.is_wall = True
                    elif(tile.x == 1):
                        tile.is_lurkingpoint = True
                    elif(tile.x == 16):
                        tile.is_door = True

                for tile in map[7]:
                    if(tile.x > 30):
                        removetiles.append(tile)
                    elif(tile.x == 0) or (tile.x == 30):
                        tile.is_wall = True
                    elif(tile.x == 1):
                        tile.is_lurkingpoint = True
                    elif(tile.x == 2):
                        tile.is_entrypoint =True
                    elif(tile.x == 18) or (tile.x == 22) or (tile.x == 26):
                        tile.is_door = True

                for tile in map[8]:
                    if(tile.x > 30 and tile.x < 34) or (tile.x > 38):
                        removetiles.append(tile)
                    elif(tile.x == 0) or (tile.x == 2) or (tile.x == 3) or (tile.x > 4 and tile.x < 16) or (tile.x == 17) or (tile.x == 18) or (tile.x > 21 and tile.x < 27) or (tile.x == 30) or (tile.x > 33 and tile.x < 39):
                        tile.is_wall = True
                    elif(tile.x == 1):
                        tile.is_lurkingpoint = True
                    elif(tile.x == 16):
                        tile.is_door = True

                for tile in map[9]:
                    if(tile.x > 22 and tile.x < 26) or (tile.x > 30 and tile.x < 34) or (tile.x > 38):
                        removetiles.append(tile)
                    elif(tile.x == 0) or (tile.x == 2) or (tile.x == 3) or (tile.x > 4 and tile.x < 16) or (tile.x > 16 and tile.x < 20) or (tile.x == 21) or (tile.x == 22) or (tile.x == 26) or (tile.x == 27) or (tile.x == 29) or (tile.x == 30) or (tile.x == 34) or (tile.x == 38):
                        tile.is_wall = True
                    elif(tile.x == 1):
                        tile.is_lurkingpoint = True
                    elif(tile.x == 20) or (tile.x == 28):
                        tile.is_door = True

                for tile in map[10]:
                    if(tile.x == 18) or (tile.x > 21 and tile.x < 27) or (tile.x > 29 and tile.x < 34) or (tile.x > 38):
                        removetiles.append(tile)
                    elif(tile.x == 0) or (tile.x == 17) or (tile.x == 19) or (tile.x == 21) or (tile.x == 27) or (tile.x == 29) or (tile.x == 34) or (tile.x == 38):
                        tile.is_wall = True
                    elif(tile.x == 1):
                        tile.is_lurkingpoint = True
                    elif(tile.x == 2):
                        tile.is_entrypoint = True

                for tile in map[11]:
                    if(tile.x == 18) or (tile.x > 21 and tile.x < 27) or (tile.x > 29 and tile.x < 34) or (tile.x > 38):
                        removetiles.append(tile)
                    elif(tile.x == 0) or (tile.x == 2) or (tile.x == 3) or (tile.x == 5) or (tile.x == 6) or (tile.x > 7 and tile.x < 18) or (tile.x == 19) or (tile.x == 21) or (tile.x == 27) or (tile.x == 29) or (tile.x == 34) or (tile.x == 38):
                        tile.is_wall = True
                    elif(tile.x == 1):
                        tile.is_lurkingpoint = True

                for tile in map[12]:
                    if(tile.x > 8 and tile.x < 19) or (tile.x > 21 and tile.x < 26) or (tile.x > 30 and tile.x < 34) or (tile.x == 39) or (tile.x > 44):
                        removetiles.append(tile)
                    elif(tile.x >= 0 and tile.x < 4) or (tile.x > 4 and tile.x < 9) or (tile.x == 19) or (tile.x == 21) or (tile.x == 26) or (tile.x == 27) or (tile.x == 29) or (tile.x == 30) or (tile.x == 34) or (tile.x == 35) or (tile.x == 37) or (tile.x == 38) or (tile.x > 39 and tile.x < 45):
                        tile.is_wall = True
                    elif(tile.x == 4):
                        tile.is_entrypoint = True
                    elif(tile.x == 28):
                        tile.is_door = True

                for tile in map[13]:
                    if(tile.x < 2) or (tile.x > 6 and tile.x < 19) or (tile.x > 21 and tile.x < 26) or (tile.x > 44):
                        removetiles.append(tile)
                    elif(tile.x == 2) or (tile.x == 6) or (tile.x == 19) or (tile.x == 21) or (tile.x == 26) or (tile.x > 29 and tile.x < 36) or (tile.x > 36 and tile.x < 41) or (tile.x == 44):
                        tile.is_wall = True
                    elif(tile.x > 2 and tile.x < 6):
                        tile.is_lurkingpoint = True
                    elif(tile.x == 36):
                        tile.is_door = True

                for tile in map[14]:
                    if(tile.x < 2) or (tile.x > 6 and tile.x < 19) or (tile.x > 21 and tile.x < 26) or (tile.x > 44):
                        removetiles.append(tile)
                    elif(tile.x > 1 and tile.x < 7) or (tile.x == 19) or (tile.x == 21) or (tile.x == 26) or (tile.x == 44):
                        tile.is_wall = True
                    elif(tile.x == 30):
                        tile.is_door = True

                for tile in map[15]:
                    if(tile.x < 18) or (tile.x > 22 and tile.x < 26) or (tile.x > 44):
                        removetiles.append(tile)
                    elif(tile.x == 18) or (tile.x == 19) or (tile.x == 21) or (tile.x == 22) or (tile.x == 26) or (tile.x > 29 and tile.x < 36) or (tile.x > 36 and tile.x < 41) or (tile.x == 44):
                        tile.is_wall = True
                    elif(tile.x == 20) or (tile.x == 36):
                        tile.is_door = True

                for tile in map[16]:
                    if(tile.x < 15) or (tile.x > 22 and tile.x < 26) or (tile.x > 30 and tile.x < 35) or (tile.x == 38) or (tile.x == 39) or (tile.x > 44):
                        removetiles.append(tile)
                    elif(tile.x > 14 and tile.x < 19) or (tile.x == 22) or (tile.x == 26) or (tile.x == 27) or (tile.x == 29) or (tile.x == 30) or (tile.x == 35) or (tile.x == 37) or (tile.x == 40) or (tile.x == 41) or (tile.x == 43) or (tile.x == 44):
                        tile.is_wall = True
                    elif(tile.x == 28) or (tile.x == 42):
                        tile.is_door = True

                for tile in map[17]:
                    if(tile.x < 15) or (tile.x > 22 and tile.x < 27) or (tile.x > 29 and tile.x < 35) or (tile.x > 37 and  tile.x < 41) or (tile.x > 43):
                        removetiles.append(tile)
                    elif(tile.x == 15) or (tile.x == 22) or (tile.x == 27) or (tile.x == 29) or (tile.x == 35) or (tile.x == 37) or (tile.x == 41) or (tile.x == 43):
                        tile.is_wall = True
                    elif(tile.x == 18):
                        tile.is_door = True

                for tile in map[18]:
                    if(tile.x < 15) or (tile.x > 22 and tile.x < 27) or (tile.x > 29 and tile.x < 35) or (tile.x > 37 and  tile.x < 41) or (tile.x > 43):
                        removetiles.append(tile)
                    elif(tile.x == 15) or (tile.x == 17) or (tile.x == 18) or (tile.x == 22) or (tile.x == 27) or (tile.x == 29) or (tile.x == 35) or (tile.x == 37) or (tile.x == 41) or (tile.x == 43):
                        tile.is_wall = True

                for tile in map[19]:
                    if(tile.x < 15) or (tile.x > 22 and tile.x < 27) or (tile.x > 29 and tile.x < 35) or (tile.x > 37 and  tile.x < 41) or (tile.x > 43):
                        removetiles.append(tile)
                    elif(tile.x > 14 and tile.x < 23) or (tile.x == 27) or (tile.x == 29) or (tile.x == 35) or (tile.x == 37) or (tile.x == 41) or (tile.x == 43):
                        tile.is_wall = True

                for tile in map[20]:
                    if(tile.x < 27) or (tile.x > 29 and tile.x < 35) or (tile.x > 43):
                        removetiles.append(tile)
                    elif(tile.x == 27) or (tile.x == 29) or (tile.x == 35) or (tile.x > 36 and tile.x < 42) or (tile.x == 43):
                        tile.is_wall = True
                    elif(tile.x == 42):
                        tile.is_door = True

                for tile in map[21]:
                    if(tile.x < 27) or (tile.x > 29 and tile.x < 35) or (tile.x > 43):
                        removetiles.append(tile)
                    elif(tile.x == 27) or (tile.x == 29) or (tile.x == 35) or (tile.x == 43):
                        tile.is_wall = True
                    elif(tile.x == 37):
                        tile.is_door = True

                for tile in map[22]:
                    if(tile.x < 27) or (tile.x > 29 and tile.x < 35) or (tile.x > 43):
                        removetiles.append(tile)
                    elif(tile.x > 26 and tile.x < 30) or (tile.x == 35) or (tile.x > 36 and tile.x < 42) or (tile.x == 43):
                        tile.is_wall = True

                for tile in map[23]:
                    if(tile.x < 35) or (tile.x > 43):
                        removetiles.append(tile)
                    elif(tile.x == 35) or (tile.x > 36 and tile.x < 42) or (tile.x == 43):
                        tile.is_wall = True

                for tile in map[24]:
                    if(tile.x < 35) or (tile.x > 43):
                        removetiles.append(tile)
                    elif(tile.x == 35) or (tile.x == 43):
                        tile.is_wall = True

                for tile in map[25]:
                    if(tile.x < 35) or (tile.x > 43):
                        removetiles.append(tile)
                    elif(tile.x == 35) or (tile.x == 37) or (tile.x == 38) or (tile.x > 39 and tile.x < 44):
                        tile.is_wall = True
                    elif(tile.x == 39):
                        tile.is_door = True

                for tile in map[26]:
                    if(tile.x < 35) or (tile.x > 40):
                        removetiles.append(tile)
                    elif(tile.x == 35) or (tile.x == 37) or (tile.x == 38) or (tile.x == 40):
                        tile.is_wall = True

                for tile in map[27]:
                    if(tile.x < 35) or (tile.x > 40):
                        removetiles.append(tile)
                    elif(tile.x == 35) or (tile.x == 37) or (tile.x == 38) or (tile.x == 40):
                        tile.is_wall = True
                    elif(tile.x == 36):
                        tile.is_door = True

                for tile in map[28]:
                    if(tile.x < 32) or (tile.x > 40 and tile.x < 44) or (tile.x > 46):
                        removetiles.append(tile)
                    elif(tile.x > 31 and tile.x < 36) or (tile.x == 37) or (tile.x == 38) or (tile.x == 40) or (tile.x > 43 and tile.x < 47):
                        tile.is_wall = True

                for tile in map[29]:
                    if(tile.x < 32) or (tile.x > 46):
                        removetiles.append(tile)
                    elif(tile.x == 32) or (tile.x == 34) or (tile.x == 35) or (tile.x == 37) or (tile.x == 38) or (tile.x == 40) or (tile.x > 39 and tile.x < 45) or (tile.x == 46):
                        tile.is_wall = True
                    elif(tile.x == 33) or (tile.x == 45):
                        tile.is_lurkingpoint = True

                for tile in map[30]:
                    if(tile.x < 32) or (tile.x > 46):
                        removetiles.append(tile)
                    elif(tile.x == 32) or (tile.x == 46):
                        tile.is_wall = True
                    elif(tile.x == 33) or (tile.x == 45):
                        tile.is_lurkingpoint = True
                    elif(tile.x == 34) or (tile.x == 44):
                        tile.is_entrypoint = True

                for tile in map[31]:
                    if(tile.x < 32) or (tile.x > 46):
                        removetiles.append(tile)
                    elif(tile.x == 32) or (tile.x == 34) or (tile.x == 35) or (tile.x == 37) or (tile.x == 38) or (tile.x == 40) or (tile.x == 41) or (tile.x == 43) or (tile.x == 44) or (tile.x == 46):
                        tile.is_wall = True
                    elif(tile.x == 33) or (tile.x == 45):
                        tile.is_lurkingpoint = True

                for tile in map[32]:
                    if(tile.x < 32) or (tile.x > 46):
                        removetiles.append(tile)
                    elif(tile.x == 36) or (tile.x == 39) or (tile.x == 42):
                        tile.is_entrypoint = True
                    else:
                        tile.is_wall = True

                for tile in map[33]:
                    if(tile.x < 34) or (tile.x > 44):
                        removetiles.append(tile)
                    elif(tile.x == 34) or (tile.x == 44):
                        tile.is_wall = True
                    else:
                        tile.is_lurkingpoint = True

                for tile in map[34]:
                    if(tile.x < 34) or (tile.x > 44):
                        removetiles.append(tile)
                    else:
                        tile.is_wall = True

                for ins in removetiles:
                    for row in map:
                        for tile in row:
                            if(tile == ins):
                                tile.is_used = False  

                for model in [SpaceMarine('flamer', 'Battlebrother'),SpaceMarine('powerSword','sergeant'),SpaceMarine('fist','Battlebrother'),SpaceMarine('fist','Battlebrother'),SpaceMarine('fist','Battlebrother')]:
                    SM_ModellList.append(model)
                game.states['gsprep'].bl_list = [1,1,1,1,1,1,1,1,1,3,3,3,3,3,3,3,3,3]
                screen.fill((50,50,50))

                self.Manager.changestate('cuts')
                game.run()
            pygame.display.update()

class briefing:
    def __init__(self) -> None: 
        self.Manager = gameStateManager

    def run(self):
        self.continue_image = pygame.image.load('Pictures/continue.png')
        self.continue_button = Button(810, 650, self.continue_image,1)

        cutscene = True
        briefing = False

        my_font = pygame.font.SysFont('Bahnschrift', 40)
        texts = ['loading Briefing > ... complete','Mission > burn the controlroom ...','Enemy objective > launch escape pods ...','Deployment > west corridor of section 34C12H ...','Forces > ...requesting ... done','> sergeant with Powersword and Stormbolter','> Battlebrother with Heavy Flamer and Powerfist','> 3 Battlebrothers with Stormbolters and Powerfists','Enemys? > ... checking auspex ... pinging ...','> auspex_ping == 2','> enemy reinforcements ... chance of  survival > low','> let fury be your guide, let vengance be your song. For the Emperor!','>deployment commencing ....']
        text_1 = ''
        text_2 = ''
        text_3 = ''
        text_4 = ''
        text_5 = ''
        text_6 = ''
        text_7 = ''
        text_8 = ''
        text_9 = ''
        text_10 = ''
        text_11 = ''
        text_12 = ''
        text_13 = ''

        a = 0
        b = 0
        c = 0
        d = 0
        e = 0
        f = 0
        g = 0
        h = 0 
        i = 0
        j = 0
        k = 0
        l = 0
        m = 0

        screen.fill((50,50,50))
        while(True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            while(cutscene):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            text_1 = texts[0]
                            text_2 = texts[1]
                            text_3 = texts[2]
                            text_4 = texts[3]
                            text_5 = texts[4]
                            text_6 = texts[5]
                            text_7 = texts[6]
                            text_8 = texts[7]
                            text_9 = texts[8]
                            text_10 = texts[9]
                            text_11 = texts[10]
                            text_12 = texts[11]
                            text_13 = texts[12]

                line_1 = my_font.render(text_1, False, (0,0,0))
                line_2 = my_font.render(text_2, False, (0,0,0))
                line_3 = my_font.render(text_3, False, (0,0,0))
                line_4 = my_font.render(text_4, False, (0,0,0))
                line_5 = my_font.render(text_5, False, (0,0,0))
                line_6 = my_font.render(text_6, False, (0,0,0))
                line_7 = my_font.render(text_7, False, (0,0,0))
                line_8 = my_font.render(text_8, False, (0,0,0))
                line_9 = my_font.render(text_9, False, (0,0,0))
                line_10 = my_font.render(text_10, False, (0,0,0))
                line_11 = my_font.render(text_11, False, (0,0,0))
                line_12 = my_font.render(text_12, False, (0,0,0))
                line_13 = my_font.render(text_13, False, (0,0,0))
                screen.blit(line_1, (20,20))
                screen.blit(line_2, (20,70))
                screen.blit(line_3, (20,120))
                screen.blit(line_4, (20, 170))
                screen.blit(line_5, (20, 220))
                screen.blit(line_6, (20, 270))
                screen.blit(line_7, (20, 320))
                screen.blit(line_8, (20, 370))
                screen.blit(line_9, (20, 420))
                screen.blit(line_10, (20, 470))
                screen.blit(line_11, (20, 520))
                screen.blit(line_12, (20, 570))
                screen.blit(line_13, (20, 620))
                if(text_1 != texts[0]):
                    text_1 += texts[0][a]
                    a += 1
                    time.sleep(0.1)
                elif(text_2 != texts[1]):
                    text_2 += texts[1][b]
                    b += 1
                    time.sleep(0.1)
                elif(text_3 != texts[2]):
                    text_3 += texts[2][c]
                    c += 1
                    time.sleep(0.1)
                elif(text_4 != texts[3]):
                    text_4 += texts[3][d]
                    d += 1
                    time.sleep(0.1)
                elif(text_5 != texts[4]):
                    text_5 += texts[4][e]
                    e += 1
                    time.sleep(0.1)
                elif(text_6 != texts[5]):
                    text_6 += texts[5][f]
                    f += 1
                    time.sleep(0.1)
                elif(text_7 != texts[6]):
                    text_7 += texts[6][g]
                    g += 1
                    time.sleep(0.1)
                elif(text_8 != texts[7]):
                    text_8 += texts[7][h]
                    h += 1
                    time.sleep(0.1)
                elif(text_9 != texts[8]):
                    text_9 += texts[8][i]
                    i += 1
                    time.sleep(0.1)
                elif(text_10 != texts[9]):
                    text_10 += texts[9][j]
                    j += 1
                    time.sleep(0.1)
                elif(text_11 != texts[10]):
                    text_11 += texts[10][k]
                    k += 1
                    time.sleep(0.1)
                elif(text_12 != texts[11]):
                    text_12 += texts[11][l]
                    l += 1
                    time.sleep(0.1)
                elif(text_13 != texts[12]):
                    text_13 += texts[12][m]
                    m += 1
                    time.sleep(0.1)
                elif(self.continue_button.draw(screen)):
                    cutscene = False
                    briefing = True
                    screen.fill((50,50,50))
                    a = 0
                pygame.display.update()

            while(briefing):
                pictures = ['Pictures/map_1_SM_deploy.png','Pictures/map_1_GS_deploy.png','Pictures/map_1_SM_goal.png']
                texts = ['Player 1 deploys his 5 Space Marines on these squares','Player 2 Deploys his 2 Blips on these squares','Player 1 needs to shoot the heavy flamer here']
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                picture = pygame.image.load(pictures[a])
                picture = pygame.transform.scale(picture, (600,600))
                text = my_font.render(texts[a], False, (0,0,0))
                screen.blit(picture, (0,0))
                screen.blit(text, (20,600))
                if(self.continue_button.draw(screen)):
                    if(a < 2):
                        a += 1
                        screen.fill((50,50,50))
                    else:
                        briefing = False
                        self.Manager.changestate('smplace')
                        screen.fill((50,50,50))
                        game.run()

                pygame.display.update()
            pygame.display.update()

class CP_reroll:
    def __init__(self) -> None:
        self.Manager = gameStateManager

    def run(self):
        self.cease_image = pygame.image.load('Pictures/cease.png')
        self.reroll_image = pygame.image.load('Pictures/reroll.png')

        self.changeturn_button = Button(870, 500, self.cease_image, 1)
        self.reroll_button = Button(810, 500, self.reroll_image, 1)
        SB.hint = 'Reroll the amount of CP?'

        while(True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            for row in map:
                for tile in row:
                    tile.render(screen)
                    tile.interact()
            
            SB.display(screen)
            BB.display(screen)

            if(self.changeturn_button.draw(screen)):
                self.Manager.changestate('runP1')
                game.selected_Model = None
                game.run()

            if(self.reroll_button.draw(screen)):
                self.Manager.changestate('runP1')
                game.CP = random.randint(1,6)
                game.selected_Model = None
                game.run()
            
            pygame.display.update()

class Player1Turn:
    def __init__(self) -> None:
        self.Manager = gameStateManager

    def run(self):
        self.change_image = pygame.image.load('Pictures/end_turn.png')
        self.activate_image = pygame.image.load('Pictures/Activate.png')
        self.main_image = pygame.image.load('Pictures/quit.png')
        self.changeturn_button = Button(870, 500, self.change_image, 1)
        self.activate_button = Button(810, 500, self.activate_image, 1)
        self.main_button = Button(930, 500, self.main_image, 1)

        while(True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEWHEEL:
                    for row in map:
                        for tile in row:
                            tile.size += event.y
                            tile.rect.topleft = ((tile.x * tile.size), (tile.y * tile.size))
                    screen.fill((50,50,50))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for row in map:
                            for tile in row:
                                tile.yb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_w:
                        for row in map:
                            for tile in row:
                                tile.yb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_a:
                        for row in map:
                            for tile in row:
                                tile.xb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_d:
                        for row in map:
                            for tile in row:
                                tile.xb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                                
                    screen.fill((50, 50, 50))
                
            for row in map:
                for tile in row:
                    tile.render(screen)
                    tile.interact()
            if(game.selected_Model == None):
                SB.hint = 'Select a model.'
            elif(game.selected_Model.AP != 0):
                SB.hint = 'Activate model?'
            elif(game.selected_Model.AP == 0):
                SB.hint = 'Reactivate model? Every action now costs CP!'
            
            SB.display(screen)
            BB.display(screen)

            if(self.changeturn_button.safedraw(screen)):
                Player1Activation.activated_model = None
                game.selected_Model = None
                game.is_playing = game.player2
                game.GS_prep()
                self.Manager.changestate('gsprep')
                game.run()
            
            if(self.main_button.draw(screen)):
                self.Manager.savestate = self.Manager.givestate()
                self.Manager.changestate('main')
                game.run()
                
            if(((game.selected_Model in SM_ModellList) and (game.is_playing == game.player1)) and self.activate_button.draw(screen)):
                self.Manager.changestate('actP1')
                game.run()

            pygame.display.update()

class OOC_Activation:
    def __init__(self) -> None:
        self.Manager = gameStateManager

    def run(self):
        pressed = False
        self.move_image = pygame.image.load('Pictures/move.png')
        self.turn_image = pygame.image.load('Pictures/turn.png')
        self.change_image = pygame.image.load('Pictures/end_turn.png')
        self.shoot_image = pygame.image.load('Pictures/shoot.png')
        self.melee_image = pygame.image.load('Pictures/melee.png')
        self.oc_door_image = pygame.image.load('Pictures/interact.png')
        self.guard_image = pygame.image.load('Pictures/guard.png')
        self.overwatch_image = pygame.image.load('Pictures/overwatch.png')
        self.unjam_image = pygame.image.load('Pictures/unjam.png')
        self.reload_image = pygame.image.load('Pictures/Wall.png')

        self.turn_button = Button(870, 500, self.turn_image, 1)
        self.move_button = Button(810, 500, self.move_image, 1)
        self.changeturn_button = Button(930, 500, self.change_image, 1)
        self.shoot_button = Button(990, 500, self.shoot_image, 1)
        self.melee_button = Button(1050, 500, self.melee_image, 1)
        self.ocDoor_button = Button(1110, 500, self.oc_door_image, 1)
        self.guard_button = Button(1170, 500, self.guard_image, 1)
        self.overwatch_button = Button(1230, 500, self.overwatch_image, 1)
        self.un_jam_button = Button(810, 560, self.unjam_image, 1)
        self.reload_button = Button(810, 560, self.reload_image, 1)
        SB.hint = 'Use CP for an out of sequence activation?'
        
        while(True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEWHEEL:
                    for row in map:
                        for tile in row:
                            tile.size += event.y
                            tile.rect.topleft = ((tile.x * tile.size), (tile.y * tile.size))
                    screen.fill((50,50,50))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for row in map:
                            for tile in row:
                                tile.yb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_w:
                        for row in map:
                            for tile in row:
                                tile.yb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_a:
                        for row in map:
                            for tile in row:
                                tile.xb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_d:
                        for row in map:
                            for tile in row:
                                tile.xb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                                
                    screen.fill((50, 50, 50))

            for row in map:
                for tile in row:
                    tile.render(screen)
                    tile.interact()
            
            SB.display(screen)
            BB.display(screen)
            if(game.selected_Model != None):
                if(self.move_button.draw(screen)):
                    if(game.selected_Model in self.Manager.ooc_models):
                        if(game.CP != 0):
                            game.moveModel()
                            pressed = True

                if(self.turn_button.draw(screen)):
                    if(game.CP != 0):
                        self.Manager.changestate('turn')
                        game.run()

                if(self.shoot_button.draw(screen)):
                    if(game.selected_Model != None):
                        if((game.selected_Model.weapon != 'claws') and (game.selected_Model.weapon != 'hammer')):
                            if(((game.CP) > 1) and (game.selected_Model.weapon == 'flamer')):
                                self.Manager.changestate('shoot')
                                game.run()
                            elif(((game.CP) != 0) and (game.selected_Model.weapon != 'flamer')):
                                self.Manager.changestate('shoot')
                                game.run()
                            else: 
                                SB.problem = 'Not enough CP!'

                if(self.melee_button.draw(screen)):
                    if(game.selected_Model != None):
                        if((game.CP) != 0):
                            pressed = True
                            game.melee()
                                        
                if(self.ocDoor_button.draw(screen)):
                    pressed = True
                    game.ocDoor()

                if(self.guard_button.draw(screen)):
                    if((game.CP) > 1):
                        pressed = True
                        game.redAP(game.selected_Model, 2)
                        game.selected_Model.overwatch = False
                        game.selected_Model.guard = True

                if(self.overwatch_button.draw(screen)):
                    if((game.CP) > 1):
                        if((game.selected_Model.weapon != 'flamer') and (game.selected_Model.weapon != 'claws') and (game.selected_Model.weapon != 'hammer')):
                            game.redAP(game.selected_Model, 2)
                            game.selected_Model.overwatch = True
                            game.selected_Model.guard = False
                            pressed = True
                        else:
                            SB.problem = 'Equipped weapon cannot overwatch!'

                if(game.selected_Model.weapon == 'AssaultCanon'):
                    if(game.Assault_cannon_reload):
                        if(self.reload_button.draw(screen)):
                            if((game.selected_Model.AP + game.CP) > 3):
                                game.Assault_cannon_Ammo = 10
                                game.Assault_cannon_reload = False
                            else:
                                SB.problem = 'Not enough AP/CP'
                if((game.selected_Model.jam == True) and (game.selected_Model.overwatch == True)):
                    if(self.un_jam_button.draw(screen)):
                        if(game.CP != 0):
                            game.redAP(game.selected_Model, 1)
                            game.selected_Model.jam = False
                            pressed = True

            if(self.changeturn_button.draw(screen)):
                    pressed = True

            if(pressed):
                self.Manager.ooc = False
                self.Manager.ooc_models = []
                game.is_playing = game.player2
                self.Manager.changestate('runP2')
                game.selected_Model = None
                game.selected_tile = None
                game.clicked_tile = None
                game.clicked_model = None
                self.Manager.SM_move = False
                SB.problem = ''
                game.run()

            pygame.display.update()

class Player1Activation:
    def __init__(self) -> None:
        self.Manager = gameStateManager
        self.activated_model = None
        self.active_tile = None

    def run(self):
        if(self.activated_model == None):
            self.activated_model = game.selected_Model
            self.active_tile = game.selected_tile
        if(not (self.activated_model in SM_ModellList)):
            self.Manager.changestate('runP1')
            game.run()

        self.move_image = pygame.image.load('Pictures/move.png')
        self.turn_image = pygame.image.load('Pictures/turn.png')
        self.change_image = pygame.image.load('Pictures/cease.png')
        self.shoot_image = pygame.image.load('Pictures/shoot.png')
        self.melee_image = pygame.image.load('Pictures/melee.png')
        self.oc_door_image = pygame.image.load('Pictures/interact.png')
        self.guard_image = pygame.image.load('Pictures/guard.png')
        self.overwatch_image = pygame.image.load('Pictures/overwatch.png')
        self.reload_image = pygame.image.load('Pictures/Wall.png')

        self.turn_button = Button(870, 500, self.turn_image, 1)
        self.move_button = Button(810, 500, self.move_image, 1)
        self.changeturn_button = Button(930, 500, self.change_image, 1)
        self.shoot_button = Button(990, 500, self.shoot_image, 1)
        self.melee_button = Button(1050, 500, self.melee_image, 1)
        self.ocDoor_button = Button(1110, 500, self.oc_door_image, 1)
        self.guard_button = Button(1170, 500, self.guard_image, 1)
        self.overwatch_button = Button(1230, 500, self.overwatch_image, 1)
        self.reload_button = Button(810, 560, self.reload_image, 1)

        while(True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEWHEEL:
                    for row in map:
                        for tile in row:
                            tile.size += event.y
                            tile.rect.topleft = ((tile.x * tile.size), (tile.y * tile.size))
                    screen.fill((50,50,50))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for row in map:
                            for tile in row:
                                tile.yb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_w:
                        for row in map:
                            for tile in row:
                                tile.yb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_a:
                        for row in map:
                            for tile in row:
                                tile.xb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_d:
                        for row in map:
                            for tile in row:
                                tile.xb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                                
                    screen.fill((50, 50, 50))
            for row in map:
                for tile in row:
                    tile.render(screen)
                    tile.interact()
            
            SB.display(screen)
            BB.display(screen)
            if(SB.hint != ''):
                SB.hint = 'Press X-Button to finish model activation.'
            
            if(self.move_button.draw(screen)):
                if((game.is_playing == game.player1) and (game.selected_Model in SM_ModellList)):
                    if((self.activated_model != game.selected_Model) and (game.selected_Model in SM_ModellList)):
                        self.activated_model.AP = 0
                        self.activated_model = game.selected_Model
                    game.moveModel()

            if(self.turn_button.draw(screen)):
                if((game.is_playing == game.player1) and (game.selected_Model in SM_ModellList)):
                    if((self.activated_model != game.selected_Model) and (game.selected_Model in SM_ModellList)):
                        self.activated_model.AP = 0
                        self.activated_model = game.selected_Model
                    if((game.selected_Model.AP != 0) or ((game.is_playing == game.player1) and (game.CP != 0))):
                        self.Manager.changestate('turn')
                        game.run()
                    else: SB.problem = 'Not enough AP/CP!'
            
            if(self.changeturn_button.draw(screen)):
                self.activated_model.AP = 0
                self.activated_model = None
                game.selected_Model = None
                self.Manager.changestate('runP1')
                game.run()

            if(self.shoot_button.draw(screen)):
                if(game.selected_Model != None):
                    if((game.is_playing == game.player1) and (game.selected_Model in SM_ModellList)):
                        if((self.activated_model != game.selected_Model) and (self.activated_model in SM_ModellList)):
                            self.activated_model.AP = 0
                            self.activated_model = game.selected_Model
                        if((game.selected_Model.weapon != 'claws') and (game.selected_Model.weapon != 'hammer')):
                            if(((game.selected_Model.AP + game.CP) > 1) and (game.selected_Model.weapon == 'flamer')):
                                self.Manager.changestate('shoot')
                                game.run()
                            elif(((game.selected_Model.AP + game.CP) != 0) and (game.selected_Model.weapon != 'flamer')):
                                self.Manager.changestate('shoot')
                                game.run()
                            else: SB.problem = 'Not enough AP/CP!'

            if(self.melee_button.draw(screen)):
                if(game.selected_Model != None):
                    if((game.is_playing == game.player1) and (game.selected_Model in SM_ModellList)):
                        if((self.activated_model != game.selected_Model) and (self.activated_model in SM_ModellList)):
                            self.activated_model.AP = 0
                            self.activated_model = game.selected_Model
                        if((game.selected_Model.AP + game.CP) != 0):
                            game.melee()
                        else: SB.problem = 'Not enough AP/CP!'
            
            if(self.ocDoor_button.draw(screen)):
                if((game.is_playing == game.player1) and (game.selected_Model in SM_ModellList)):
                    if((self.activated_model != game.selected_Model) and (game.selected_Model in SM_ModellList)):
                        self.activated_model.AP = 0
                        self.activated_model = game.selected_Model
                    game.ocDoor()

            if(self.guard_button.draw(screen)):
                if((game.selected_Model.AP + game.CP) > 1):
                    if((game.is_playing == game.player1) and (game.selected_Model in SM_ModellList)):
                            if((self.activated_model != game.selected_Model) and (game.selected_Model in SM_ModellList)):
                                self.activated_model.AP = 0
                                self.activated_model = game.selected_Model
                            game.redAP(game.selected_Model, 2)
                            game.selected_Model.overwatch = False
                            game.selected_Model.guard = True
                else:
                    SB.problem = 'Not enough AP/CP!'

            if(self.overwatch_button.draw(screen)):
                if((game.selected_Model.AP + game.CP) > 1):
                    if((game.selected_Model.weapon != 'flamer') and (game.selected_Model.weapon != 'claws') and (game.selected_Model.weapon != 'hammer')):
                        if((game.is_playing == game.player1) and (game.selected_Model in SM_ModellList)):
                                if((self.activated_model != game.selected_Model) and (game.selected_Model in SM_ModellList)):
                                    self.activated_model.AP = 0
                                    self.activated_model = game.selected_Model
                                game.redAP(game.selected_Model, 2)
                                game.selected_Model.overwatch = True
                                game.selected_Model.guard = False
                    else:
                        SB.problem = 'Equipped weapon cannot overwatch!'
                else:
                    SB.problem = ' Not enough AP/CP!'

            if(game.selected_Model.weapon == 'AssaultCanon'):
                if(game.Assault_cannon_reload):
                    if(self.reload_button.draw(screen)):
                        if((game.selected_Model.AP + game.CP) > 3):
                                game.Assault_cannon_Ammo = 10
                                game.Assault_cannon_reload = False
                        else:
                            SB.problem = 'Not enough AP/CP'
            pygame.display.update()

class Player2Turn:
    def __init__(self) -> None:
        self.Manager = gameStateManager

    def run(self):
        self.change_image = pygame.image.load('Pictures/end_turn.png')
        self.activate_image = pygame.image.load('Pictures/Activate.png')
        self.main_image = pygame.image.load('Pictures/quit.png')
        self.amount_image = pygame.image.load('Pictures/Wall.png')
        self.changeturn_button = Button(810, 500, self.change_image, 1)
        self.activate_button = Button(870, 500, self.activate_image, 1)
        self.main_button = Button(930, 500, self.main_image, 1)
        self.amount_button = Button(1170, 500, self.amount_image, 1)

        while(True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEWHEEL:
                    for row in map:
                        for tile in row:
                            tile.size += event.y
                            tile.rect.topleft = ((tile.x * tile.size), (tile.y * tile.size))
                            print(event.y)
                    screen.fill((50,50,50))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for row in map:
                            for tile in row:
                                tile.yb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_w:
                        for row in map:
                            for tile in row:
                                tile.yb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_a:
                        for row in map:
                            for tile in row:
                                tile.xb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_d:
                        for row in map:
                            for tile in row:
                                tile.xb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                                
                    screen.fill((50, 50, 50))
            for row in map:
                for tile in row: 
                    tile.render(screen)
                    tile.interact()
            
            if(game.selected_Model == None):
                SB.hint = 'Select a model.'
            elif(game.selected_Model.AP != 0):
                SB.hint = 'Activate model?'
            
            SB.display(screen)
            BB.display(screen)

            if(self.Manager.ooc == True):
                self.Manager.changestate('ooc')
                game.is_playing = game.player1
                game.run()

            if(game.selected_Model in BL_ModellList):
                if(self.amount_button.draw(screen)):
                    if(SB.bl_count == 0):
                        SB.bl_count = game.selected_Model.count
                    else:
                        SB.bl_count = 0

            if(self.changeturn_button.safedraw(screen)):
                Player2Activation.activated_model = None
                game.checkwin()
                game.is_playing = game.player1
                game.SM_prep()
                self.Manager.changestate('runP1')
                SB.bl_count = 0
                game.run()

            if(self.main_button.draw(screen)):
                self.Manager.savestate = self.Manager.givestate()
                self.Manager.changestate('main')
                game.run()

            if((((game.selected_Model in GS_ModellList) or (game.selected_Model in BL_ModellList)) and (game.is_playing == game.player2)) and self.activate_button.draw(screen)):
                self.Manager.changestate('actP2')
                game.run()

            pygame.display.update()

class Player2Activation:
    def __init__(self) -> None:
        self.Manager = gameStateManager
        self.activated_model = None

    def run(self):
        if(self.activated_model != None):
            if(self.activated_model != game.selected_Model):
                self.activated_model.AP = 0
                self.activated_model = None
        if(self.activated_model == None):
            self.activated_model = game.selected_Model
        elif((self.activated_model not in GS_ModellList) or (self.activated_model not in BL_ModellList)):
            self.activated_model == None
            # self.Manager.changestate('runP2')
            # game.run()

        SB.hint = 'Press X-Button to finish model activation.'
                                                                                                                
        self.move_image = pygame.image.load('Pictures/move.png')
        self.turn_image = pygame.image.load('Pictures/turn.png')
        self.change_image = pygame.image.load('Pictures/cease.png')
        self.melee_image = pygame.image.load('Pictures/melee.png')
        self.oc_door_image = pygame.image.load('Pictures/interact.png')
        self.reveal_image = pygame.image.load('Pictures/reveal.png')
        self.amount_image = pygame.image.load('Pictures/Wall.png')

        self.turn_button = Button(870, 500, self.turn_image, 1)
        self.move_button = Button(810, 500, self.move_image, 1)
        self.changeturn_button = Button(930, 500, self.change_image, 1)
        self.melee_button = Button(1050, 500, self.melee_image, 1)
        self.ocDoor_button = Button(1110, 500, self.oc_door_image, 1)
        self.reveal_button = Button(990,500, self.reveal_image, 1)
        self.amount_button = Button(1170, 500, self.amount_image, 1)

        while(True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEWHEEL:
                    for row in map:
                        for tile in row:
                            tile.size += event.y
                            tile.rect.topleft = ((tile.x * tile.size), (tile.y * tile.size))
                            print(event.y)
                    screen.fill((50,50,50))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for row in map:
                            for tile in row:
                                tile.yb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_w:
                        for row in map:
                            for tile in row:
                                tile.yb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_a:
                        for row in map:
                            for tile in row:
                                tile.xb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_d:
                        for row in map:
                            for tile in row:
                                tile.xb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                                
                    screen.fill((50, 50, 50))
            for row in map:
                for tile in row: 
                    tile.render(screen)
                    tile.interact()
            SB.display(screen)
            BB.display(screen)

            if(self.Manager.ooc == True):
                self.Manager.changestate('ooc')
                game.selected_Model = None
                game.selected_tile = None
                game.clicked_model = None
                game.clicked_tile = None
                game.is_playing = game.player1
                game.run()
            
            
            if(game.selected_Model in BL_ModellList):
                if(self.amount_button.draw(screen)):
                    if(SB.bl_count == 0):
                        SB.bl_count = game.selected_Model.count
                    else:
                        SB.bl_count = 0

            if(self.Manager.gs_turnaftermove != None):
                SB.hint = 'You have a free Turn-Action!'

            if(self.move_button.draw(screen)):
                if((game.is_playing == game.player2) and ((game.selected_Model in GS_ModellList) or (game.selected_Model in BL_ModellList))):
                    game.moveModel()

            if(self.turn_button.draw(screen)):
                if(game.selected_Model != None):
                    if((game.is_playing == game.player2) and (game.selected_Model in GS_ModellList)):
                        if((self.activated_model != game.selected_Model) and ((game.selected_Model in GS_ModellList) or (game.selected_Model in BL_ModellList))):
                            self.activated_model.AP = 0
                            self.activated_model = game.selected_Model
                        if(game.selected_Model.AP != 0):
                            self.Manager.changestate('turn')
                            game.run()
                        SB.problem = 'Not enough CP'

            if(self.changeturn_button.draw(screen)):
                self.activated_model.AP = 0
                self.activated_model = None
                self.Manager.changestate('runP2')
                SB.bl_count = 0
                game.run()

            if(self.reveal_button.draw(screen)):
                if(game.selected_Model in BL_ModellList):
                    if(game.selected_tile.is_lurkingpoint == False):
                        self.Manager.rev_models.append(game.selected_tile)
                        game.reveal(game.selected_tile)

            if(self.melee_button.draw(screen)):
                if(game.selected_Model in GS_ModellList):
                    if((self.activated_model != game.selected_Model) and ((game.selected_Model in GS_ModellList) or (game.selected_Model in BL_ModellList))):
                        self.activated_model.AP = 0
                        self.activated_model = game.selected_Model
                    if(game.selected_Model.AP != 0):
                        game.melee()

            if(self.ocDoor_button.draw(screen)):
                if((self.activated_model != game.selected_Model) and ((game.selected_Model in GS_ModellList) or (game.selected_Model in BL_ModellList))):
                        self.activated_model.AP = 0
                        self.activated_model = game.selected_Model
                game.ocDoor()

            pygame.display.update()

class gamestate_shoot:
    def __init__(self) -> None:
        self.manager = gameStateManager
    
    def run(self):
        self.shoot_image = pygame.image.load('Pictures/shoot.png')
        self.shoot_button = Button(810, 600, self.shoot_image, 1)

        while(True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEWHEEL:
                    for row in map:
                        for tile in row:
                            tile.size += event.y
                            tile.rect.topleft = ((tile.x * tile.size), (tile.y * tile.size))
                            print(event.y)
                    screen.fill((50,50,50))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for row in map:
                            for tile in row:
                                tile.yb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_w:
                        for row in map:
                            for tile in row:
                                tile.yb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_a:
                        for row in map:
                            for tile in row:
                                tile.xb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_d:
                        for row in map:
                            for tile in row:
                                tile.xb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                                
                    screen.fill((50, 50, 50))

            for row in map:
                for tile in row: 
                    tile.render(screen)
                    tile.interact()
            
            if(game.clicked_model == None):
                SB.hint = 'Select a target.'
            else:
                SB.hint = ''
                
            SB.display(screen)
            BB.display(screen)

            if(self.shoot_button.draw(screen)):
                game.shoot()
                if(game.is_playing == game.player1):
                    if(self.manager.ooc == True):
                        self.manager.ooc = False
                        self.manager.ooc_models = []
                        game.selected_Model = None
                        game.selected_tile = None
                        game.is_playing = game.player2
                        if(not (self.manager.save_model in GS_ModellList)):
                            self.manager.gs_turnaftermove = None
                        self.manager.changestate('runP2')
                        game.run()
                    else:
                        self.manager.changestate('actP1')
                        game.run()
                else:
                    self.manager.changestate('actP2')
                    game.run()

            pygame.display.update()

class gamestate_reinforcement:
    def __init__(self) -> None:
        self.Manager = gameStateManager
        self.bl_list = []                       #list to store certain blips(Mission specific)

    def run(self):
        amount = game.reinforcement
        bl_count = 0
        match(game.level):
            case(1):
                bl_count = random.randint(1,3)
            case(2):
                if(self.bl_list.__len__() == 0):
                    amount = 0
                else:
                    bl_count = random.choice(self.bl_list)
                    self.bl_list.remove(bl_count)
        self.place_image = pygame.image.load('Pictures/placemodel.png')
        self.amount_image = pygame.image.load('Pictures/Wall.png')
        self.place_button = Button(810, 500, self.place_image, 1)
        self.amount_button = Button(870, 500, self.amount_image, 1)

        while(True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEWHEEL:
                    for row in map:
                        for tile in row:
                            tile.size += event.y
                            tile.rect.topleft = ((tile.x * tile.size), (tile.y * tile.size))
                            print(event.y)
                    screen.fill((50,50,50))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for row in map:
                            for tile in row:
                                tile.yb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_w:
                        for row in map:
                            for tile in row:
                                tile.yb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_a:
                        for row in map:
                            for tile in row:
                                tile.xb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_d:
                        for row in map:
                            for tile in row:
                                tile.xb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                                
                    screen.fill((50, 50, 50))

            for row in map:
                for tile in row: 
                    tile.render(screen)
                    tile.interact()

            SB.amount = str(amount)
            if(game.selected_tile == None):
                SB.hint = 'Select a lurkingpoint.'
            elif(game.selected_tile.is_lurkingpoint == False):
                SB.hint = 'Select a lurkingpoint.'
            else:
                SB.hint = ''
            SB.display(screen)
            BB.display(screen)

            if(self.amount_button.draw(screen)):
                if(SB.bl_count == 0):
                    SB.bl_count = bl_count
                else:
                    SB.bl_count = 0

            if(self.place_button.draw(screen)):
                if(amount != 0):
                    if((game.clicked_tile != None) and (game.clicked_tile.is_lurkingpoint) and (game.clicked_tile.is_occupied == False)):
                        game.clicked_tile.occupand = Blip()
                        game.clicked_tile.occupand.count = bl_count
                        match(game.level):
                            case(1):
                                bl_count = random.randint(1,3)
                            case(2):
                                if(self.bl_list.__len__() != 0):
                                    bl_count = random.choice(self.bl_list)
                                    self.bl_list.remove(bl_count)
                        game.clicked_tile.is_occupied = True
                        BL_ModellList.append(game.clicked_tile.occupand)
                        amount -= 1
            lis = []
            for row in map:
                for tile in row:
                    if((tile.is_lurkingpoint) and (tile.is_occupied == False)):
                        lis.append(tile)

            if((amount == 0) or (lis == [])):
                for row in map:
                    for tile in row:
                        if(tile.is_entrypoint == True):
                            for row in map:
                                for obj in row:
                                    if(obj.occupand in SM_ModellList):
                                        if(obj.is_path_within_distance(tile, 7)):
                                            for lkp in [map[tile.y][tile.x + 1],map[tile.y][tile.x - 1],map[tile.y + 1][tile.x],map[tile.y - 1][tile.x],map[tile.y +1][tile.x + 1],map[tile.y + 1][tile.x - 1],map[tile.y - 1][tile.x - 1],map[tile.y - 1][tile.x + 1]]:
                                                if lkp.is_lurkingpoint:
                                                    if lkp.is_occupied == True:
                                                        lkp.occupand.AP = 0
                self.Manager.changestate('runP2')
                SB.bl_count = 0
                game.run()
            pygame.display.update()

class gamestate_Main:
    def __init__(self) -> None:
        self.Manager = gameStateManager

    def run(self):
        main_image = pygame.image.load('pictures/Main_Screen.png')
        main_image = pygame.transform.scale(main_image, screen.get_size())
        screen.blit(main_image, (0,0))
        self.move_image = pygame.image.load('Pictures/Wall.png')
        self.new_image = pygame.image.load('Pictures/new_game.png')
        self.quit_image = pygame.image.load('Pictures/quit.png')
        self.continue_image = pygame.image.load('Pictures/continue.png')

        self.start_new_button = Button(560, 250, self.new_image, 1)
        self.start_saved_button = Button(560, 250, self.move_image, 1)
        self.options_button = Button(670, 250, self.move_image, 1)
        self.quit_button = Button(670, 250, self.quit_image, 1)
        self.continue_button = Button(450, 250,self.continue_image, 1) 
        while(True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if(self.start_new_button.draw(screen)):
                self.Manager.changestate('start')
                game.run()

            if(self.continue_button.draw(screen)):
                state = gameStateManager.savestate
                if(state != None):
                    screen.fill((50,50,50))
                    gameStateManager.changestate(state)
                    game.run()
            
            if(self.quit_button.draw(screen)):
                pygame.quit()
                sys.exit()
            
            pygame.display.update()

class gamestate_SMplace:
    def __init__(self) -> None:
        self.Manager = gameStateManager

    def run(self):
        self.place_image = pygame.image.load('Pictures/placemodel.png')
        self.place_button = Button(810, 500, self.place_image, 1)
        x = 0

        while(True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEWHEEL:
                    for row in map:
                        for tile in row:
                            tile.size += event.y
                            tile.rect.topleft = ((tile.x * tile.size), (tile.y * tile.size))
                            print(event.y)
                    screen.fill((50,50,50))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for row in map:
                            for tile in row:
                                tile.yb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_w:
                        for row in map:
                            for tile in row:
                                tile.yb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_a:
                        for row in map:
                            for tile in row:
                                tile.xb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_d:
                        for row in map:
                            for tile in row:
                                tile.xb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                                
                    screen.fill((50, 50, 50))
            for row in map:
                for tile in row: 
                    tile.render(screen)
                    tile.interact()

            SB.amount = str(SM_ModellList.__len__() - x)
            if(game.selected_tile == None):
                SB.hint = 'Select an Entrypoint.'
            elif(game.selected_tile.is_SMentry == False):
                SB.hint = 'Select an Entrypoint.'
            elif(game.selected_tile.is_SMentry == True):
                SB.hint = 'Click the place-Button to place the model.'
            else:
                SB.hint = ''

            game.selected_Model = SM_ModellList[x]
            SB.display(screen)
            BB.display(screen)

            if(self.place_button.draw(screen)):
                if(game.clicked_tile != None):
                    if(game.clicked_tile.is_SMentry == True):
                        if(game.clicked_tile.is_occupied == False):
                            game.clicked_tile.occupand = SM_ModellList[x]
                            x += 1
                            game.clicked_tile.is_occupied = True

            if(len(SM_ModellList) == x):
                self.Manager.changestate('gsplace')
                for row in map:
                    for tile in row:
                        if(tile.is_SMentry == True):
                            tile.is_SMentry = False
                game.is_playing = game.player2
                game.selected_Model = None
                game.run()
            pygame.display.update()

class gamestate_gsplace:
    def __init__(self) -> None:
        self.Manager = gameStateManager

    def run(self):
        amount = game.gs_start
        bl_count = 0
        match(game.level):
            case(1):
                bl_count = random.randint(1,3)
            case(2):
                bl_count = 0
        self.amount_image = pygame.image.load('Pictures/Wall.png')
        self.place_image = pygame.image.load('Pictures/placemodel.png')
        self.place_button = Button(810, 500, self.place_image, 1)
        self.amount_button = Button(870, 500, self.amount_image, 1)
        while(True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEWHEEL:
                    for row in map:
                        for tile in row:
                            tile.size += event.y
                            tile.rect.topleft = ((tile.x * tile.size), (tile.y * tile.size))
                            print(event.y)
                    screen.fill((50,50,50))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for row in map:
                            for tile in row:
                                tile.yb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_w:
                        for row in map:
                            for tile in row:
                                tile.yb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_a:
                        for row in map:
                            for tile in row:
                                tile.xb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_d:
                        for row in map:
                            for tile in row:
                                tile.xb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                                
                    screen.fill((50, 50, 50))
            for row in map:
                for tile in row: 
                    tile.render(screen)
                    tile.interact()

            SB.amount = str(amount)
            if(game.selected_tile == None):
                SB.hint = 'Select an Entrypoint.'
            elif(game.selected_tile.is_lurkingpoint == False):
                SB.hint = 'Select an Entrypoint.'
            elif(game.selected_tile.is_lurkingpoint == True):
                SB.hint = 'Click the place-Button to place the model.'
            else:
                SB.hint = ''

            SB.display(screen)
            BB.display(screen)
            if(self.amount_button.draw(screen)):
                if(SB.bl_count == 0):
                    SB.bl_count = bl_count
                else:
                    SB.bl_count = 0
            if(self.place_button.draw(screen)):
                if(amount != 0):
                    if((game.clicked_tile != None) and (game.clicked_tile.is_lurkingpoint) and (game.clicked_tile.is_occupied == False)):
                        game.clicked_tile.occupand = Blip()
                        game.clicked_tile.occupand.count = bl_count
                        match(game.level):
                            case(1):
                                bl_count = random.randint(1,3)
                        game.clicked_tile.is_occupied = True
                        BL_ModellList.append(game.clicked_tile.occupand)
                        amount -= 1
            lis = []
            for row in map:
                for tile in row:
                    if((tile.is_lurkingpoint) and (tile.is_occupied == False)):
                        lis.append(tile)

            if((amount == 0) or (lis == [])):
                for row in map:
                    for bl in row:
                        if(bl.occupand in BL_ModellList):
                            for row in map:
                                for tile in row:
                                    if(tile.occupand in SM_ModellList):
                                        d = game.distance(bl, tile)
                                        if(d < 7):
                                            bl.occupand.AP = 0
                game.is_playing = game.player1
                SB.bl_count = 0
                if game.CP != 6:
                    self.Manager.changestate('reroll')
                    game.run()
                else:
                    self.Manager.changestate('runP1')
                    game.run()
            pygame.display.update()

class gamestate_reveal:
    def __init__(self) -> None:
        self.Manager = gameStateManager
        self.active = False
        self.origin_tile = None

    def run(self):
        self.place_image = pygame.image.load('Pictures/placemodel.png')
        self.place_button = Button(810, 500, self.place_image, 1)
        lis = []

        if(self.Manager.rev_count == 0):

            self.revModel = game.selected_Model
            self.Manager.rev_count = self.revModel.count
            tile = game.selected_tile
            self.origin_tile = tile

            tile.is_occupied = False
            BL_ModellList.remove(tile.occupand)
            if(tile.occupand.AP == 6):
                tile.occupand = Genestealer()
                self.active = True
            else:
                tile.occupand = Genestealer()
                tile.occupand.AP = 0

            tile.is_occupied = True
            GS_ModellList.append(tile.occupand)
            self.Manager.rev_count -= 1
            print(self.Manager.rev_count)
            self.Manager.rev_models.remove(tile)
            self.Manager.turn = True
            game.selected_Model = tile.occupand
            self.Manager.changestate('turn')
            game.run()

        while(True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEWHEEL:
                    for row in map:
                        for tile in row:
                            tile.size += event.y
                            tile.rect.topleft = ((tile.x * tile.size), (tile.y * tile.size))
                            print(event.y)
                    screen.fill((50,50,50))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        for row in map:
                            for tile in row:
                                tile.yb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_w:
                        for row in map:
                            for tile in row:
                                tile.yb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_a:
                        for row in map:
                            for tile in row:
                                tile.xb += 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                    if event.key == pygame.K_d:
                        for row in map:
                            for tile in row:
                                tile.xb -= 1
                                tile.rect.topleft = ((tile.xb * tile.size),(tile.yb * tile.size))
                                
                    screen.fill((50, 50, 50))
            for row in map:
                for tile in row: 
                    tile.render(screen)
                    tile.interact()
            
            SB.amount = str(self.Manager.rev_count)
            if(game.selected_tile == None):
                SB.hint = 'Select a Tile.'
            else:
                SB.hint = ''
            
            SB.display(screen)
            BB.display(screen)

            if(self.place_button.draw(screen)):
                if(game.clicked_tile != None):
                    if(((game.clicked_tile.x == game.selected_tile.x) or (game.clicked_tile.x == (game.selected_tile.x -1)) or (game.clicked_tile.x == (game.selected_tile.x +1))) and ((game.clicked_tile.y == game.selected_tile.y) or (game.clicked_tile.y == (game.selected_tile.y -1)) or (game.clicked_tile.y == (game.selected_tile.y +1)))):
                        if((game.clicked_tile.is_occupied == False) and (game.clicked_tile.is_wall == False) and (game.clicked_tile.is_entrypoint == False)):
                            game.clicked_tile.occupand = Genestealer()
                            if(self.active == False):
                                game.clicked_tile.occupand.AP = 0
                            GS_ModellList.append(game.clicked_tile.occupand)
                            game.clicked_tile.is_occupied = True
                            self.Manager.rev_count -= 1
                            self.Manager.turn = True
                            game.selected_Model = game.clicked_tile.occupand
                            self.Manager.changestate('turn')
                            game.run()

            lis = []

            for row in map:
                for tile in row:
                    if(((tile.x == self.origin_tile.x) or (tile.x == (self.origin_tile.x -1)) or (tile.x == (self.origin_tile.x +1))) and ((tile.y == self.origin_tile.y) or (tile.y == (self.origin_tile.y -1)) or (tile.y == (self.origin_tile.y +1)))):
                        if((tile.is_occupied == False) & (((tile.is_door == True) & (tile.is_open == True)) or (tile.is_door == False)) & (tile.is_wall == False) & (tile.is_entrypoint == False)):
                            lis.append(tile)
        
            if((self.Manager.rev_count == 0) or (lis == [])):
                self.Manager.rev_count = 0
                if(self.Manager.rev_models == []):
                    if(game.is_playing == game.player1):
                        game.selected_tile = self.Manager.save_tile
                        game.selected_Model = self.Manager.save_model
                        if(self.Manager.savestate == 'reroll'):
                            self.Manager.changestate('reroll')
                            self.Manager.savestate = None
                            game.selected_tile = None
                            game.selected_Model = None
                            game.run()
                        else:
                            self.Manager.changestate('actP1')
                            game.run()
                    else: 
                        self.Manager.changestate('runP2')
                        game.selected_Model = None
                        game.selected_tile = None
                        game.run()
                else:
                    game.reveal(self.Manager.rev_models[0])

            pygame.display.update()
        
class Tile:
    def __init__(self, x, y, size):
        self.x = x                      # x position on the grid
        self.y = y                      # y position on the grid
        self.xb = x
        self.yb = y
        image = pygame.image.load('Pictures/Floor_1.png')     # image of the floor tiles
        self.image = pygame.transform.scale(image, (int(size), int(size)))
        self.size = size # size of the tile in pixels
        self.is_occupied = False # true if occupied by any miniature
        self.occupand = Model # equals the modell which occupies this tile
        self.rect = self.image.get_rect()
        self.rect.topleft = (x*size,y*size) #positions the rect to th right coordinates
        self.clicked = False    #if the tile has been clicked(importnt later)
        self.is_wall = False    #if the tile is a wall-segment thus having a diffrent picture and function
        self.is_entrypoint = False  #if the tile is an entrypoint for reinforcing blips
        self.is_lurkingpoint = False    #if the tile is a lurkingpoint for blips
        self.is_door = False    
        self.is_open = False
        self.is_buring = False
        self.is_SMentry = False
        self.is_used = True
        self.group = 'a'

    def render(self, screen):
        if(self.is_used):
            if(self.is_wall): 
                image = pygame.image.load('Pictures/Wall.png')
                self.image = pygame.transform.scale(image,(self.size,self.size))
            elif(self.is_door):
                if((map[self.y+1][self.x].is_wall == True) and (map[self.y-1][self.x].is_wall == True)):
                    #path = if self.is_open == False "" else ""
                    if(self.group == 'a'):
                        if(self.is_open == False):
                            image = pygame.image.load('Pictures/Door.png')
                            self.image = pygame.transform.scale(image,(self.size,self.size))
                        elif(self.is_buring == True):
                            image = pygame.image.load('Pictures/Door_burning.png')
                            self.image = pygame.transform.scale(image, (self.size,self.size))
                        else:
                            image = pygame.image.load('Pictures/Door_open.png')
                            self.image = pygame.transform.scale(image,(self.size,self.size))
                    else:
                        if(self.is_open == False):
                            image = pygame.image.load('Pictures/Door_2.png')
                            self.image = pygame.transform.scale(image,(self.size,self.size))
                        elif(self.is_buring == True):
                            image = pygame.image.load('Pictures/Door_2_burning.png')
                            self.image = pygame.transform.scale(image, (self.size,self.size))
                        else:
                            image = pygame.image.load('Pictures/Door_open_2.png')
                            self.image = pygame.transform.scale(image,(self.size,self.size))
                else:
                    if(self.group == 'a'):
                        if(self.is_open == False):
                            image = pygame.image.load('Pictures/Door.png')
                            imagen = pygame.transform.scale(image,(self.size,self.size))
                            self.image = pygame.transform.rotate(imagen,90)
                        elif(self.is_buring == True):
                            image = pygame.image.load('Pictures/Door_burning.png')
                            imagen = pygame.transform.scale(image,(self.size,self.size))
                            self.image = pygame.transform.rotate(imagen,90)
                        else:
                            image = pygame.image.load('Pictures/Door_open.png')
                            imagen = pygame.transform.scale(image,(self.size,self.size))
                            self.image = pygame.transform.rotate(imagen,90)
                    else:
                        if(self.is_open == False):
                            image = pygame.image.load('Pictures/Door_2.png')
                            imagen = pygame.transform.scale(image,(self.size,self.size))
                            self.image = pygame.transform.rotate(imagen,90)
                        elif(self.is_buring == True):
                            image = pygame.image.load('Pictures/Door_2_burning.png')
                            imagen = pygame.transform.scale(image,(self.size,self.size))
                            self.image = pygame.transform.rotate(imagen,90)
                        else:
                            image = pygame.image.load('Pictures/Door_open_2.png')
                            imagen = pygame.transform.scale(image,(self.size,self.size))
                            self.image = pygame.transform.rotate(imagen,90)

            elif(self.is_entrypoint):
                image = pygame.image.load('Pictures/entrypoint.PNG')
                if((map[self.y][self.x - 1].is_lurkingpoint == False) and (map[self.y][self.x - 1].is_wall == False)):
                    self.image = pygame.transform.scale(image,(self.size,self.size))
                elif((map[self.y + 1][self.x].is_lurkingpoint == False) and (map[self.y + 1][self.x].is_wall == False)):
                    imager = pygame.transform.scale(image,(self.size,self.size))
                    self.image = pygame.transform.rotate(imager,90)
                elif((map[self.y][self.x + 1].is_lurkingpoint == False) and (map[self.y][self.x + 1].is_wall == False)):
                    imager = pygame.transform.scale(image,(self.size,self.size))
                    self.image = pygame.transform.rotate(imager,180)
                else:
                    imager = pygame.transform.scale(image,(self.size,self.size))
                    self.image = pygame.transform.rotate(imager,270)
            elif(self.is_buring):
                if(self.group == 'a'):
                    image = pygame.image.load('Pictures/Floor_burning.png')
                    self.image = pygame.transform.scale(image, (int(self.size),int(self.size)))
                else:
                    image = pygame.image.load('Pictures/Floor_2_burning.png')
                    self.image = pygame.transform.scale(image, (int(self.size),int(self.size)))
            elif(self.is_lurkingpoint == True):
                image = pygame.image.load('Pictures/lurking.png')
                self.image = pygame.transform.scale(image,(int(self.size),int(self.size)))
            elif(self.is_SMentry == True):
                image = pygame.image.load('Pictures/SM_entry.png')
                self.image = pygame.transform.scale(image, (int(self.size),int(self.size)))
            else:
                if(self.group == 'a'):
                    image = pygame.image.load('Pictures/Floor.png')
                    self.image = pygame.transform.scale(image, (int(self.size), int(self.size)))
                else:
                    image = pygame.image.load('Pictures/Floor_2.png')
                    self.image = pygame.transform.scale(image, (int(self.size), int(self.size)))
            screen.blit(self.image, (self.xb*self.size, self.yb*self.size))
            if(self == game.clicked_tile):
                image = pygame.image.load('Pictures/clicked_tile.png')
                screen.blit(pygame.transform.scale(image, (int(self.size), int(self.size))),(self.xb*self.size, self.yb * self.size))

            if(self.is_occupied):
                if(self.occupand == game.selected_Model):
                    if((self.occupand in SM_ModellList)):
                        image = pygame.image.load('Pictures/Models/SM_select.png')
                    elif((self.occupand in GS_ModellList)):
                        image = pygame.image.load('Pictures/Models/GS_select.png')
                    elif((self.occupand in BL_ModellList)):
                        image = pygame.image.load('Pictures/Models/Blip-select.png')

                elif(self.occupand == game.clicked_model):
                    if(self.occupand in SM_ModellList):
                        image = pygame.image.load('Pictures/Models/SM_clicked.png')
                    elif(self.occupand in GS_ModellList):
                        image = pygame.image.load('Pictures/Models/GS_clicked.png')
                    elif(self.occupand in BL_ModellList):
                        image = pygame.image.load('Pictures/Models/Blip_clicked.png')

                elif(self.occupand in SM_ModellList):
                    if(self.occupand.guard == True):
                        image = pygame.image.load('Pictures/Models/guard.png')
                    elif((self.occupand.overwatch == True) and (self.occupand.jam == False)):
                        image = pygame.image.load('Pictures/Models/overwatch.png')
                    else:
                        image = self.occupand.image
                else:   
                    image = self.occupand.image      

                match(self.occupand.face):
                        case((1,0)):
                            imaget = pygame.transform.scale(image, (int(self.size), int(self.size)))
                        
                        case(-1,0):
                            imaget = pygame.transform.scale(image, (int(self.size), int(self.size)))
                            imaget = pygame.transform.rotate(imaget,180)
                        
                        case((0,1)):
                            imaget = pygame.transform.scale(image, (int(self.size), int(self.size)))
                            imaget = pygame.transform.rotate(imaget,270)

                        case((0,-1)):
                            imaget = pygame.transform.scale(image, (int(self.size), int(self.size)))
                            imaget = pygame.transform.rotate(imaget,90)
        
                screen.blit(imaget, (self.xb*self.size, self.yb*self.size))
    
    def interact(self):
        if(self.is_used):
            pos = pygame.mouse.get_pos()
            if(self.rect.collidepoint(pos)) and (pygame.mouse.get_pressed()[0] == 1):
                self.clicked = True
            if(pygame.mouse.get_pressed()[0] == 0 and self.clicked):
                if((gameStateManager.givestate() == 'ooc') and (self.occupand in gameStateManager.ooc_models)):
                    game.selected_Model = self.occupand
                    game.selected_tile = self
                elif((gameStateManager.givestate() == 'ooc') and (self.occupand not in SM_ModellList)):
                    game.clicked_model = self.occupand
                    game.clicked_tile = self

                elif(gameStateManager.givestate() == 'shoot'):
                    if(self.is_occupied == True):
                        if self.occupand in GS_ModellList:
                            game.clicked_tile = self
                            game.clicked_model = self.occupand
                    elif(self.is_door == True and self.is_open == False):
                        game.clicked_tile = self
                elif(gameStateManager.givestate() == 'actP1'):
                    if(self.is_occupied == True):
                        if self.occupand in GS_ModellList:
                            game.clicked_tile = self
                            game.clicked_model = self.occupand
                    else:
                        game.clicked_tile = self
                elif(gameStateManager.givestate() == 'actP2'):
                    if(self.is_occupied == True):
                        if self.occupand in SM_ModellList:
                            game.clicked_tile = self
                            game.clicked_model = self.occupand
                    else:
                        game.clicked_tile = self
                elif(((self.is_occupied) and (self.occupand in SM_ModellList) and (game.is_playing == game.player1)) or ((self.is_occupied) and ((self.occupand in GS_ModellList) or (self.occupand in BL_ModellList)) and (game.is_playing == game.player2))):
                    game.selected_Model = self.occupand
                    game.selected_tile = self
                elif(self.is_occupied):
                        game.clicked_model = self.occupand
                        print(self.occupand)
                        game.clicked_tile = self
                else:
                    game.clicked_tile = self
                self.clicked = False

    def is_path_within_distance(self, target_tile, max_distance):
        visited = set()
        queue = deque([(self.x, self.y, 0)])

        while queue:
            current_x, current_y, distance = queue.popleft()
            current_tile = map[current_y][current_x]

            if current_tile == target_tile:
                return True  # Path found within distance

            if distance < max_distance:
                neighbors = [(current_x + 1, current_y), (current_x - 1, current_y),
                             (current_x, current_y + 1), (current_x, current_y - 1)]

                for nx, ny in neighbors:
                    if 0 <= nx < map_width and 0 <= ny < map_height:
                        neighbor_tile = map[ny][nx]
                        if not neighbor_tile.is_wall and (nx, ny) not in visited:
                            visited.add((nx, ny))
                            queue.append((nx, ny, distance + 1))

        return False  # No path found within distance
    
# class Model:
#     def __init__(self, AP, image):
#         self.AP = AP
#         self.image = pygame.image.load(image)
#         self.face = (1,0)

# class SpaceMarine(Model):
#     def __init__(self, weapon, rank):
#         super().__init__(4,'Pictures/Models/SM.png')
#         self.weapon = weapon
#         self.rank = rank
#         self.susf = False
#         self.overwatch = False
#         self.guard = False
#         self.jam = False

# class Genestealer(Model):
#     def __init__(self):
#         super().__init__(6, 'Pictures/Models/Gs.png')
#         self.is_broodlord = False

# class Blip(Model):
#     def __init__(self):
#         super().__init__(6, 'Pictures/Models/Blip.PNG')
#         self.count = random.randint(1,3)

# #generate a Map of tiles
map_width = 47
map_height = 35
tile_size = 27

map = [[Tile(x, y, tile_size, ) for x in range(map_width)] for y in range(map_height)]

class Sidebar():
    def __init__(self):
        self.SM_Modelcount = len(SM_ModellList)
        self.timer = int
        self.pos = (810,0)
        self.hint = ''
        self.roll = ''
        self.amount = ''
        self.bl_count = 0
        self.problem = ''

    def display(self,screen):

        my_font = pygame.font.SysFont('Bahnschrift', 20)
        image = pygame.image.load('Pictures/Sidebar.png')
        image2 = pygame.transform.scale(image, (int(470), int(500)))
        screen.blit(image2, self.pos)

        smodel = game.selected_Model
        cmodel = game.clicked_model
        state = gameStateManager.givestate()

        state_Text = my_font.render(str(gameStateManager.givestate()), False, (0,0,0))
        CP_Text = my_font.render('CP: '+str(game.CP), False, (0,0,0))
        round_Text = my_font.render('Round: '+str(game.round), False, (0, 0, 0))
        player1_Text = my_font.render('SM: '+game.player1,False,(0,0,0))
        player2_Text = my_font.render('GS: '+game.player2, False, (0,0,0))
        GS_count_Text = my_font.render('GS Models: '+str((len(GS_ModellList)+len(BL_ModellList))),False,(0,0,0))
        SM_count_Text = my_font.render('SM Models: '+str(len(SM_ModellList)),False,(0,0,0))
        hint_Text = my_font.render('Hint: ' + str(self.hint), False, (0,0,0))
        roll_Text = my_font.render('Last Roll: ' + str(self.roll), False, (0,0,0))
        amount_Text = my_font.render('Remaining Modells: ' + self.amount, False, (0,0,0))
        clicked_text = my_font.render('CLicked Model:', False, (0,0,0))
        problem_text = my_font.render(self.problem, False, (255,0,0))
        flamer_ammo_text = my_font.render('Ammo: '+str(game.Heavy_flamer_ammo), False, (0,0,0))
        assault_ammo_text = my_font.render('Ammo: '+str(game.Assault_cannon_Ammo), False, (0,0,0))
        assault_reload_text = my_font.render('Reload: '+str(game.Assault_cannon_reload),False, (0,0,0))

        if(state == 'ooc'):
            is_playing_text = my_font.render('playing: '+ game.player1,False, (0,0,0))
        else:
            is_playing_text = my_font.render('playing: '+ game.is_playing, False, (0,0,0))
        if(smodel != None):
            active_model_AP = my_font.render('AP: '+str(game.selected_Model.AP), False,(0,0,0))
            if(smodel in SM_ModellList):
                match(smodel.weapon):
                    case('fist'):
                        wpn = 'Powerfist & Stormbolter'
                    case('AssaultCanon'):
                        wpn = 'Powerfist & Assault Cannon'
                    case('powerSword'):
                        wpn = 'Powersword & Stormbolter'
                    case('flamer'):
                        wpn = 'Powerfist & Heavy Flamer'
                    case('chainFist'):
                        wpn = 'Chainfist & Stormbolter'
                    case('claws'):
                        wpn = 'Lightning Claws'
                    case('hammer'):
                        wpn = 'Thunderhammer and Stormshield'
                active_model_weapon = my_font.render('weapon: '+ wpn, False,(0,0,0))
                active_model_rank = my_font.render('rank: '+ (smodel.rank), False,(0,0,0))

        if(cmodel != None):
            if(cmodel != None):
                if(cmodel in SM_ModellList):
                    match(cmodel.weapon):
                        case('fist'):
                            wpn = 'Powerfist & Stormbolter'
                        case('AssaultCanon'):
                            wpn = 'Powerfist & Assault Cannon'
                        case('powerSword'):
                            wpn = 'Powersword & Stormbolter'
                        case('flamer'):
                            wpn = 'Powerfist & Heavy Flamer'
                        case('chainFist'):
                            wpn = 'Chainfist & Stormbolter'
                        case('claws'):
                            wpn = 'Lightning Claws'
                    clicked_model_weapon = my_font.render('weapon: '+ str(wpn), False, (0,0,0))
                    clicked_model_rank = my_font.render('rank: '+ str(cmodel.rank),False,(0,0,0))
                    
        match(state):
            case('turn'):
                screen.blit(is_playing_text, (810,30))
                screen.blit(active_model_AP, (810,60))
                screen.blit(hint_Text, (810,120))
                screen.blit(CP_Text, (810,90)) 
                if(smodel in SM_ModellList):
                    screen.blit(active_model_weapon, (810,150))
                    screen.blit(active_model_rank, (810,180)) 
                screen.blit(problem_text, (810,450))  

            case('runP1'):
                screen.blit(problem_text, (810,450))  
                if(smodel != None):
                    if(smodel in SM_ModellList):
                        screen.blit(is_playing_text, (810,30))
                        screen.blit(active_model_AP, (810,60))
                        screen.blit(CP_Text, (810,90))
                        screen.blit(hint_Text, (810,120))
                        screen.blit(roll_Text, (810,150))
                        screen.blit(active_model_weapon, (810,180))
                        screen.blit(active_model_rank, (810,210)) 
                        if(smodel.weapon == 'flamer'):
                            screen.blit(flamer_ammo_text, (810,240))
                        elif(smodel.weapon == 'AssaultCanon'):
                            screen.blit(assault_ammo_text, (810,240))
                            screen.blit(assault_reload_text, (810,270))
                else:
                    screen.blit(is_playing_text, (810,30))
                    screen.blit(CP_Text, (810,60))
                    screen.blit(hint_Text, (810,90))
                    screen.blit(roll_Text, (810,120))

            case('actP1'):
                screen.blit(problem_text, (810,450))  
                if(smodel != None):
                    if(smodel in SM_ModellList):
                        screen.blit(is_playing_text, (810,30))
                        screen.blit(active_model_AP, (810,60))
                        screen.blit(CP_Text, (810,90))
                        screen.blit(hint_Text, (810,120))
                        screen.blit(active_model_weapon, (810,150))
                        screen.blit(active_model_rank, (810,180)) 
                        screen.blit(roll_Text, (810,210))
                        if(smodel.weapon == 'flamer'):
                            screen.blit(flamer_ammo_text, (810,240))
                        elif(smodel.weapon == 'AssaultCanon'):
                            screen.blit(assault_ammo_text, (810,240))
                            screen.blit(assault_reload_text, (810,270))

            case('reroll'):
                screen.blit(is_playing_text, (810,30))
                screen.blit(CP_Text, (810,60))
                screen.blit(hint_Text, (810,90))

            case('ooc'):
                screen.blit(problem_text, (810,450)) 
                screen.blit(CP_Text, (810,60)) 
                screen.blit(is_playing_text, (810,30))
                screen.blit(hint_Text, (810,120))
                if(smodel != None):
                    if(smodel in SM_ModellList):
                        screen.blit(active_model_AP, (810,90))
                        screen.blit(hint_Text, (810,120))
                        screen.blit(active_model_weapon, (810,150))
                        screen.blit(active_model_rank, (810,180)) 
                        screen.blit(roll_Text, (810,210))
                        if(smodel.weapon == 'flamer'):
                            screen.blit(flamer_ammo_text, (810,240))
                        elif(smodel.weapon == 'AssaultCanon'):
                            screen.blit(assault_ammo_text, (810,240))
                            screen.blit(assault_reload_text, (810,270))
                        elif(smodel.jam == True):
                            t = my_font.render('Weapon jammed!', False, (0,0,0))
                            screen.blit(t, (810,240))

            case('runP2'):
                screen.blit(problem_text, (810,450))
                if(smodel != None):
                    if(self.bl_count != 0):
                        bl_c = my_font.render('Value: '+str(self.bl_count),False,(0,0,0))
                        screen.blit(bl_c, (810, 180))
                    screen.blit(is_playing_text, (810,30))
                    screen.blit(active_model_AP, (810,60))
                    screen.blit(CP_Text, (810,90))
                    screen.blit(hint_Text, (810,120))
                    screen.blit(roll_Text, (810,150))
                    if(cmodel != None):
                        if(cmodel in SM_ModellList):
                            if(cmodel.weapon == 'flamer'):
                                screen.blit(clicked_text, (810,330))
                                screen.blit(clicked_model_weapon,(810,360))
                                screen.blit(clicked_model_rank, (810, 390))
                                screen.blit(flamer_ammo_text, (810,420))
                            elif(cmodel.weapon == 'AssaultCanon'):
                                screen.blit(clicked_text, (810,300))
                                screen.blit(clicked_model_weapon,(810,330))
                                screen.blit(clicked_model_rank, (810, 360))
                                screen.blit(assault_ammo_text, (810,390))
                                screen.blit(assault_reload_text, (810,420))
                            else:
                                screen.blit(clicked_text, (810,360))
                                screen.blit(clicked_model_weapon,(810,390))
                                screen.blit(clicked_model_rank, (810, 420))
                                if(cmodel.jam == True):
                                    t = my_font.render('Weapon jammed!', False, (0,0,0))
                                    screen.blit(t, (810,330))
                else:
                    screen.blit(is_playing_text, (810,30))
                    screen.blit(CP_Text, (810,60))
                    screen.blit(hint_Text, (810,90))
                    screen.blit(roll_Text, (810,120))
                    if(cmodel != None):
                        if(cmodel in SM_ModellList):
                            if(cmodel.weapon == 'flamer'):
                                screen.blit(clicked_text, (810,330))
                                screen.blit(clicked_model_weapon,(810,360))
                                screen.blit(clicked_model_rank, (810, 390))
                                screen.blit(flamer_ammo_text, (810,420))
                            elif(cmodel.weapon == 'AssaultCanon'):
                                screen.blit(clicked_text, (810,300))
                                screen.blit(clicked_model_weapon,(810,330))
                                screen.blit(clicked_model_rank, (810, 360))
                                screen.blit(assault_ammo_text, (810,390))
                                screen.blit(assault_reload_text, (810,420))
                            else:
                                screen.blit(clicked_text, (810,360))
                                screen.blit(clicked_model_weapon,(810,390))
                                screen.blit(clicked_model_rank, (810, 420))

            case('actP2'):
                screen.blit(problem_text, (810,450))
                if(smodel != None):
                    if(self.bl_count != 0):
                        bl_c = my_font.render('Value: '+str(self.bl_count),False,(0,0,0))
                        screen.blit(bl_c, (810, 180))
                    screen.blit(is_playing_text, (810,30))
                    screen.blit(active_model_AP, (810,60))
                    screen.blit(CP_Text, (810,90))
                    screen.blit(hint_Text, (810,120)) 
                    screen.blit(roll_Text, (810,150))
                if(cmodel != None):
                    if(cmodel in SM_ModellList):
                        if(cmodel.weapon == 'flamer'):
                            screen.blit(clicked_text, (810,330))
                            screen.blit(clicked_model_weapon,(810,360))
                            screen.blit(clicked_model_rank, (810, 390))
                            screen.blit(flamer_ammo_text, (810,420))
                        elif(cmodel.weapon == 'AssaultCanon'):
                            screen.blit(clicked_text, (810,300))
                            screen.blit(clicked_model_weapon,(810,330))
                            screen.blit(clicked_model_rank, (810, 360))
                            screen.blit(assault_ammo_text, (810,390))
                            screen.blit(assault_reload_text, (810,420))
                        else:
                            screen.blit(clicked_text, (810,360))
                            screen.blit(clicked_model_weapon,(810,390))
                            screen.blit(clicked_model_rank, (810, 420))
                            if(cmodel.jam == True):
                                t = my_font.render('Weapon jammed!', False, (0,0,0))
                                screen.blit(t, (810,330))

            case('shoot'):
                screen.blit(problem_text, (810,450))
                if(smodel in SM_ModellList):
                    if(smodel.susf == True):
                        sus = my_font.render('Sustained', False, (0,0,0))
                        screen.blit(sus,(810,210))
                if(smodel != None):
                    if(smodel in SM_ModellList):
                        screen.blit(active_model_AP, (810,60))
                        screen.blit(active_model_weapon, (810,150))
                        screen.blit(active_model_rank, (810,180)) 
                        if(smodel.weapon == 'flamer'):
                            screen.blit(flamer_ammo_text, (810,240))
                        elif(smodel.weapon == 'AssaultCanon'):
                            screen.blit(assault_ammo_text, (810,240))
                            screen.blit(assault_reload_text, (810,270))
                screen.blit(is_playing_text, (810,30))
                screen.blit(CP_Text, (810,90))
                screen.blit(hint_Text, (810,120))

            case('gsprep'):
                screen.blit(problem_text, (810,450))
                screen.blit(hint_Text, (810,30))
                screen.blit(amount_Text, (810,90))
                screen.blit(CP_Text, (810,60))
                if(self.bl_count != 0):
                    bl_c = my_font.render('Value: '+str(self.bl_count),False,(0,0,0))
                    screen.blit(bl_c, (810, 120))
                if(cmodel != None):
                    if(cmodel in SM_ModellList):
                            screen.blit(clicked_text, (810,360))
                            screen.blit(clicked_model_weapon,(810,390))
                            screen.blit(clicked_model_rank, (810, 420))

            case('smplace'):
                screen.blit(problem_text, (810,450))
                screen.blit(is_playing_text, (810,30))
                screen.blit(CP_Text, (810,60))
                screen.blit(amount_Text, (810,90))
                screen.blit(hint_Text, (810,180))
                screen.blit(active_model_weapon, (810,120))
                screen.blit(active_model_rank, (810,150)) 

            case('gsplace'):
                screen.blit(problem_text, (810,450))
                if(self.bl_count != 0):
                    bl_c = my_font.render('Value: '+str(self.bl_count),False,(0,0,0))
                    screen.blit(bl_c, (810, 150))
                screen.blit(is_playing_text, (810,30))
                screen.blit(CP_Text, (810,60))
                screen.blit(amount_Text, (810,90))
                screen.blit(hint_Text, (810,120))

            case('reveal'):
                screen.blit(problem_text, (810,450))
                screen.blit(is_playing_text, (810,30))
                screen.blit(CP_Text, (810,60))
                screen.blit(amount_Text, (810,90))
                screen.blit(hint_Text, (810,120))

        screen.blit(round_Text, (810,0))
SB = Sidebar()  #initiates an Object of Sidebar(singelton)

class Bottombar():
    def __init__(self):
        self.pos = (810,500)
        image = pygame.image.load('Pictures/Bottombar.png')
        self.image = pygame.transform.scale(image, (int(470), int(410)))
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.pressed = False
        self.slots = [(810,500),(870,500),(930,500),(990,500),(1050,500),(1110,500),(1170,500),(1230,500),(810,560)]
    
    def display(self,screen):
        screen.blit(self.image, self.pos)

BB = Bottombar()    #initiates an object of Bottombar(singelton)