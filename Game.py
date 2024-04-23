import json
import random
from Board import *

class Game():
    def __init__(self) -> None:
        self.map = []
        self.blipList = ()
        self.cp = random.randint(1,6)
        self.player1 = "";self.player2 = ""
        self.gsModelList = [];self.smModelList = [];self.blipSack = [];self.blModelList = []
        self.level = int

    def load_level(self,levelFile):
        file_path = "Levels/"+levelFile+".json"
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        self.level = data["level"]
        self.blipSack = data["blipList"]

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
        if dir == "right":
            model.picture = pygame.transform.rotate(model.picture, 90)
            if model.face == (1,0):
                model.face = (0,-1)
            elif model.face == (0,-1):
                model.face = (-1,0)
            elif model.face == (-1,0):
                model.face = (0,1)
            elif model.face == (0,1):
                model.face = (1,0)

        else:
            model.picture = pygame.transform.rotate(model.picture, -90)
            if model.face == (1,0):
                model.face = (0,1)
            elif model.face == (0,-1):
                model.face = (1,0)
            elif model.face == (-1,0):
                model.face = (0,-1)
            elif model.face == (0,1):
                model.face = (-1,0)

    def move_model(self, model, tile, target):
        tile.isOccupied = False
        tile.occupand = None
        target.occupand = model
        target.isOccupied = True

game = Game()
game.load_level("level1")
print(game.map)