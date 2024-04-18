import json
import random
from Board import *

class Game():
    def __init__(self) -> None:
        self.map = []
        self.blipList = ()
        self.cp = int
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

game = Game()
game.load_level("level1")
print(game.map)