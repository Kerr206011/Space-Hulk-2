import json
import random

class Game():
    def __init__(self) -> None:
        self.map = []
        self.blipList = ()
        self.cp = int
        self.player1 = "";self.player2 = ""
        self.gsModelList = [];self.smModelList = [];self.blipList = []
        self.level = int

    def load_level(self,levelFile):
        file_path = levelFile+".json"
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        self.level = data["level"]
        self.blipList = data["bliplist"]
        
game = Game()
game.load_level("data")
print(game.level)