import json
import random
from Board import *

class Game():
    def __init__(self) -> None:
        self.map = []
        self.blipSack = []
        self.blipReserve = []
        self.cp = random.randint(1,6)
        self.player1 = "";self.player2 = ""
        self.isPlaying = self.player1
        self.gsModelList = [];self.smModelList = [];self.blipSack = [];self.blModelList = []
        self.level = int
        self.reinforcement = int 
        self.selectedTile = None
        self.clickedTile = None
        self.selectedModel = None
        self.clickedModel = None

    def load_level(self,levelFile):
        file_path = "Levels/"+levelFile+".json"
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        self.level = data["level"]
        self.blipSack = data["blipList"]
        self.reinforcement = data["reinforcement"]

        bluePrint = data["map"]
        for entry in bluePrint:

            if entry[1] == "tile":
                newTile = Tile(entry[2],entry[0][0],entry[0][1],entry[3])
                self.map.append(newTile)

            elif entry[1] == "door":
                newDoor = Door(entry[2], entry[4], entry[0][0], entry[0][1], entry[3], entry[5])
                self.map.append(newDoor)

            elif entry[1] == "wall":
                newWall = Wall(entry[2],entry[0][0],entry[0][1])
                self.map.append(newWall)

    def turn_model(self, model, dir):
        match dir:
            case "left":
                model.picture = pygame.transform.rotate(model.picture, 90)
                if model.face == (1,0):
                    model.face = (0,-1)
                elif model.face == (0,-1):
                    model.face = (-1,0)
                elif model.face == (-1,0):
                    model.face = (0,1)
                elif model.face == (0,1):
                    model.face = (1,0)

            case "right":
                model.picture = pygame.transform.rotate(model.picture, -90)
                if model.face == (1,0):
                    model.face = (0,1)
                elif model.face == (0,-1):
                    model.face = (1,0)
                elif model.face == (-1,0):
                    model.face = (0,-1)
                elif model.face == (0,1):
                    model.face = (-1,0)

            case _:
                model.picture = pygame.transform.rotate(model.picture, 180)
                if model.face == (1,0):
                    model.face = (-1,0)
                elif model.face == (0,-1):
                    model.face = (0,1)
                elif model.face == (-1,0):
                    model.face = (1,0)
                elif model.face == (0,1):
                    model.face = (0,-1)

    def move_model(self, model, tile, target):
        tile.isOccupied = False
        tile.occupand = None
        target.occupand = model
        target.isOccupied = True

    def set_guard(self, model):
        model.guard = True

    def set_overwatch(self, model):
        model.overwatch = True

    def destroy_model(self, model, tile):
        if model == self.selectedModel:
            self.selectedModel = None
        elif model == self.clickedModel:
            self.clickedModel = None
        if model in self.smModelList:
            self.smModelList.remove(model)
            tile.isOccupied = False
            tile.occupand = None
        elif model in self.gsModelList:
            self.gsModelList.remove(model) 
            tile.isOccupied = False
            tile.occupand = None
        if model in self.blModelList:
            self.blipReserve.append(model.count)
            self.blModelList.remove(model)
            tile.isOccupied = False
            tile.occupand = None

    def is_facing(self, attacker, defender):
        facing = False
        match attacker.face:
            case (1,0):
                if defender.face == (-1,0):
                    facing = True
            case (0,1):
                if defender.face == (0,-1):
                    facing = True
            case (-1,0):
                if defender.face == (1,0):
                    facing = True
            case (0,-1):
                if defender.face == (0,1):
                    facing = True
        
        return facing

    def melee(self, attacker, defender, roll_1, roll_2, roll_3, roll_4, roll_5, pyscic):
        facing = self.is_facing(attacker, defender)
        winner = None
        if attacker in self.gsModelList:
            if attacker.isBroodlord:
                if defender.weapon == "Thunderhammer":
                    roll_1 = roll_1 + roll_2
                else:
                    if roll_1 >= roll_2 and roll_2 >= roll_3:
                        roll_1 = roll_1 + roll_3
                    elif roll_1 >= roll_3 and roll_3 >= roll_2:
                        roll_1 = roll_1 + roll_2
                    elif roll_2 >= roll_3 and roll_3 >= roll_1:
                        roll_2 = roll_2 + roll_1
                    elif roll_2 >= roll_1 and roll_1 >= roll_3:
                        roll_2 = roll_2 + roll_3
                    elif roll_3 >= roll_2 and roll_2 >= roll_1:
                        roll_3 = roll_3 + roll_1
                    else:
                        roll_3 = roll_3 + roll_2

            if defender.weapon == "Thunderhammer":
                if facing:
                    roll_4 +=2
                    if roll_1 > roll_4 or roll_2 > roll_4:
                        winner = attacker
                    elif roll_1 == roll_4 or roll_2 == roll_4:
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
            
            elif defender.weapon == "Powersword":
                if facing:
                    roll_4 +=1
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

            elif defender.weapon == "Lightningclaws":
                if facing:
                    if roll_4 > roll_5:
                        roll_4 +=1
                    else:
                        roll_5 +=1

                    if (roll_1 > roll_4 or roll_2 > roll_4 or roll_3 > roll_4) and (roll_1 > roll_5 and roll_2 > roll_5 and roll_3 > roll_5):
                        winner = attacker
                    elif (roll_1 == roll_4 or roll_2 == roll_4 or roll_3 == roll_4 and roll_4 > roll_5) or (roll_1 == roll_5 or roll_2 == roll_5 or roll_3 == roll_5 and roll_4 < roll_5):
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

            elif defender.weapon == "Axe":
                if facing:
                    roll_4 +=1
                    roll_4 += pyscic
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
            
            else:
                if roll_1 > roll_4 or roll_2 > roll_4 or roll_3 > roll_4:
                    winner = attacker
                elif roll_1 == roll_4 or roll_2 == roll_4 or roll_3 == roll_4:
                    winner = None
                else:
                    winner = defender

        else:
            if defender.isBroodlord:
                if attacker.weapon == "Thunderhammer":
                    roll_1 = roll_1 + roll_2
                else:
                    if roll_1 >= roll_2 and roll_2 >= roll_3:
                        roll_1 = roll_1 + roll_3
                    elif roll_1 >= roll_3 and roll_3 >= roll_2:
                        roll_1 = roll_1 + roll_2
                    elif roll_2 >= roll_3 and roll_3 >= roll_1:
                        roll_2 = roll_2 + roll_1
                    elif roll_2 >= roll_1 and roll_1 >= roll_3:
                        roll_2 = roll_2 + roll_3
                    elif roll_3 >= roll_2 and roll_2 >= roll_1:
                        roll_3 = roll_3 + roll_1
                    else:
                        roll_3 = roll_3 + roll_2

            if attacker.weapon == "Thunderhammer":
                roll_4 +=2
                if roll_1 > roll_4 or roll_2 > roll_4:
                    winner = defender
                elif roll_1 == roll_4 or roll_2 == roll_4:
                    winner = None
                else:
                    winner = attacker
            
            elif attacker.weapon == "Powersword":
                roll_4 +=1
                if roll_1 > roll_4 or roll_2 > roll_4 or roll_3 > roll_4:
                    winner = defender
                elif roll_1 == roll_4 or roll_2 == roll_4 or roll_3 == roll_4:
                    winner = None
                else:
                    winner = attacker

            elif attacker.weapon == "Lightningclaws":
                if roll_4 > roll_5:
                    roll_4 +=1
                else:
                    roll_5 +=1

                if (roll_1 > roll_4 or roll_2 > roll_4 or roll_3 > roll_4) and (roll_1 > roll_5 or roll_2 > roll_5 or roll_3 > roll_5):
                    winner = defender
                elif (roll_1 == roll_4 or roll_2 == roll_4 or roll_3 == roll_4 and roll_4 > roll_5) or (roll_1 == roll_5 or roll_2 == roll_5 or roll_3 == roll_5 and roll_4 < roll_5):
                    winner = None
                else:
                    winner = attacker

            elif attacker.weapon == "Axe":
                roll_4 +=1
                roll_4 += pyscic
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
    
    def shoot_bolter(self, shooter, targetTile, roll_1, roll_2):
        if shooter.susf == True:
            roll_1 += 1
            roll_2 += 1

        if targetTile.isOccupied:
            if targetTile.occupand.isBroodlord == True:
                if roll_1 > 5 and roll_2 > 5:
                    self.destroy_model(targetTile.occupand, targetTile)
            else:
                if roll_1 > 5 or roll_2 > 5:
                    self.destroy_model(targetTile.occupand, targetTile)

        elif isinstance(targetTile, Door):
            if targetTile.isOpen == False:
                if roll_1 > 5 or roll_2 > 5:      
                    self.map.remove(targetTile)
                    self.map.append(targetTile.get_destroyed())
        if roll_1 == roll_2:
            return True
        else:
            return False
        
    
    def shoot_assaultCannon(self, shooter, targetTile, roll_1, roll_2, roll_3):
        if shooter.susf == True:
            roll_1 +=1
            roll_2 +=1
            roll_3 +=1

        if targetTile.isBroodlord == False:
            if roll_1 > 4 or roll_2 > 4 or roll_3 > 4:
                self.destroy_model(targetTile.occupand, targetTile)

        else:
            if (roll_1 > 4 and roll_2 > 4) or (roll_2 > 4 and roll_3 > 4) or (roll_1 > 4 and roll_3 > 4):
                self.destroy_model(targetTile.occupand, targetTile)

    def shoot_flamer(self, targetTile):
        x = targetTile.sector
        for tile in self.map:
            if isinstance(tile, Tile):
                if self.isOpen == True:
                    tile.isBurning = True
game = Game()
game.load_level("level1")
print(game.map)