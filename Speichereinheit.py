import json
from Board import *
from Models import * 

# Data to be written to the JSON file
# map = []
# map.append(((0,0),"tile","Floor_1.png",1))
# map.append(((1,1),"wall","Floor_1.png"))
# map.append(((2,2),"door","Floor_1.png",1,"Pictures/Models/SM.png",True))
a = []
i = 0
while i < 9:
    a.append(1)
    i+=1
i = 0
while i<4:
    a.append(2)
    i+= 1
i = 0
while i < 9:
    a.append(3)
    i+=1

saveMap = []

map = []
map.append(Wall("Pictures/Tiles/Wall.png", 0, 11))
map.append(Wall("Pictures/Tiles/Wall.png", 0, 12))
map.append(Wall("Pictures/Tiles/Wall.png", 0, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 1, 11))
map.append(ControlledArea("Pictures/Tiles/SM_entry.png", "Pictures/Tiles/Floor_burning.png", 1, 12, 0))
map.append(Wall("Pictures/Tiles/Wall.png", 1, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 2, 11))
map.append(ControlledArea("Pictures/Tiles/SM_entry.png", "Pictures/Tiles/Floor_burning.png", 2, 12, 0))
map.append(Wall("Pictures/Tiles/Wall.png", 2, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 3, 11))
map.append(ControlledArea("Pictures/Tiles/SM_entry.png", "Pictures/Tiles/Floor_burning.png", 3, 12, 0))
map.append(Wall("Pictures/Tiles/Wall.png", 3, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 4, 11))
map.append(ControlledArea("Pictures/Tiles/SM_entry.png", "Pictures/Tiles/Floor_burning.png", 4, 12, 0))
map.append(Wall("Pictures/Tiles/Wall.png", 4, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 5, 11))
map.append(ControlledArea("Pictures/Tiles/SM_entry.png", "Pictures/Tiles/Floor_burning.png", 5, 12, 0))
map.append(Wall("Pictures/Tiles/Wall.png", 5, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 6, 10))
map.append(Wall("Pictures/Tiles/Wall.png", 6, 11))
map.append(Door("Pictures/Tiles/Door_open_V.png", "Pictures/Tiles/Door_V.png", "Pictures/Tiles/Door_burning_V.png", 6, 12, 1, False))
map.append(Wall("Pictures/Tiles/Wall.png", 6, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 6, 14))
map.append(Wall("Pictures/Tiles/Wall.png", 7, 10))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 7, 11, 1))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 7, 12, 1))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 7, 13, 1))
map.append(Wall("Pictures/Tiles/Wall.png", 7, 14))
map.append(Wall("Pictures/Tiles/Wall.png", 8, 10))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 8, 11, 1))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 8, 12, 1))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 8, 13, 1))
map.append(Door("Pictures/Tiles/Door_open_H.png", "Pictures/Tiles/Door_H.png", "Pictures/Tiles/Door_burning_H.png", 8, 14, 1, False))
map.append(Wall("Pictures/Tiles/Wall.png", 9, 10))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 9, 11, 1))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 9, 12, 1))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 9, 13, 1))
map.append(Wall("Pictures/Tiles/Wall.png", 9, 14))
map.append(Wall("Pictures/Tiles/Wall.png", 10, 10))
map.append(Wall("Pictures/Tiles/Wall.png", 10, 11))
map.append(Door("Pictures/Tiles/Door_open_V.png", "Pictures/Tiles/Door_V.png", "Pictures/Tiles/Door_burning_V.png", 10, 12, 1, False))
map.append(Wall("Pictures/Tiles/Wall.png", 10, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 10, 14))
map.append(Wall("Pictures/Tiles/Wall.png", 7, 15))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 8, 15, 2))
map.append(Wall("Pictures/Tiles/Wall.png", 9, 15))
map.append(Wall("Pictures/Tiles/Wall.png", 7, 16))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 8, 16, 2))
map.append(Wall("Pictures/Tiles/Wall.png", 9, 16))
map.append(Wall("Pictures/Tiles/Wall.png", 7, 17))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 8, 17, 2))
map.append(Wall("Pictures/Tiles/Wall.png", 9, 17))
map.append(Wall("Pictures/Tiles/Wall.png", 7, 18))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 8, 18, 2))
map.append(Wall("Pictures/Tiles/Wall.png", 9, 18))
map.append(Wall("Pictures/Tiles/Wall.png", 6, 19))
map.append(Wall("Pictures/Tiles/Wall.png", 7, 19))
map.append(Door("Pictures/Tiles/Door_open_H.png", "Pictures/Tiles/Door_H.png", "Pictures/Tiles/Door_burning_H.png", 8, 19, 3, False))
map.append(Wall("Pictures/Tiles/Wall.png", 9, 19))
map.append(Wall("Pictures/Tiles/Wall.png", 10, 19))
map.append(Wall("Pictures/Tiles/Wall.png", 6, 20))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 7, 20, 3))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 8, 20, 3))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 9, 20, 3))
map.append(Wall("Pictures/Tiles/Wall.png", 10, 20))
map.append(Wall("Pictures/Tiles/Wall.png", 6, 21))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 7, 21, 3))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 8, 21, 3))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 9, 21, 3))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 10, 21, 3))
map.append(Wall("Pictures/Tiles/Wall.png", 6, 22))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 7, 22, 3))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 8, 22, 3))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 9, 22, 3))
map.append(Wall("Pictures/Tiles/Wall.png", 10, 22))
map.append(Wall("Pictures/Tiles/Wall.png", 6, 23))
map.append(Wall("Pictures/Tiles/Wall.png", 7, 23))
map.append(Wall("Pictures/Tiles/Wall.png", 8, 23))
map.append(Wall("Pictures/Tiles/Wall.png", 9, 23))
map.append(Wall("Pictures/Tiles/Wall.png", 10, 23))
map.append(Wall("Pictures/Tiles/Wall.png", 11, 20))
map.append(Door("Pictures/Tiles/Door_open_V.png", "Pictures/Tiles/Door_V.png", "Pictures/Tiles/Door_burning_V.png", 11, 21, 4, False))
map.append(Wall("Pictures/Tiles/Wall.png", 11, 22))
map.append(EntryPoint("Pictures/Tiles/lurking.png", 12, 19, (0,1)))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 12, 20, 4))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 12, 21, 4))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 12, 22, 4))
map.append(EntryPoint("Pictures/Tiles/lurking.png", 12, 23, (0, -1)))
map.append(Wall("Pictures/Tiles/Wall.png", 13, 20))
map.append(Wall("Pictures/Tiles/Wall.png", 13, 21))
map.append(Wall("Pictures/Tiles/Wall.png", 13, 22))
map.append(Wall("Pictures/Tiles/Wall.png", 11, 11))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 11, 12, 5))
map.append(Wall("Pictures/Tiles/Wall.png", 11, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 12, 11))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 12, 12, 5))
map.append(Wall("Pictures/Tiles/Wall.png", 12, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 13, 11))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 13, 12, 5))
map.append(Wall("Pictures/Tiles/Wall.png", 13, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 14, 11))
map.append(Wall("Pictures/Tiles/Wall.png", 14, 10))
map.append(Wall("Pictures/Tiles/Wall.png", 14, 9))
map.append(Wall("Pictures/Tiles/Wall.png", 14, 8))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 14, 12, 6))
map.append(Wall("Pictures/Tiles/Wall.png", 14, 13))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 15, 12, 6))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 16, 12, 6))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 15, 11, 6))
map.append(Wall("Pictures/Tiles/Wall.png", 15, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 15, 8))
map.append(Wall("Pictures/Tiles/Wall.png", 16, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 16, 11))
map.append(Wall("Pictures/Tiles/Wall.png", 16, 10))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 15, 10, 7))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 15, 9, 7))
map.append(Door("Pictures/Tiles/Door_open_V.png", "Pictures/Tiles/Door_V.png", "Pictures/Tiles/Door_burning_V.png", 16, 9, 7, False))
map.append(Wall("Pictures/Tiles/Wall.png", 16, 8))
map.append(Wall("Pictures/Tiles/Wall.png", 17, 11))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 17, 12, 8))
map.append(Wall("Pictures/Tiles/Wall.png", 17, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 18, 11))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 18, 12, 8))
map.append(Wall("Pictures/Tiles/Wall.png", 18, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 19, 11))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 19, 12, 8))
map.append(Wall("Pictures/Tiles/Wall.png", 19, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 17, 8))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 17, 9, 9))
map.append(Wall("Pictures/Tiles/Wall.png", 17, 10))
map.append(Wall("Pictures/Tiles/Wall.png", 18, 8))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 18, 9, 9))
map.append(Wall("Pictures/Tiles/Wall.png", 18, 10))
map.append(Wall("Pictures/Tiles/Wall.png", 19, 8))
map.append(Tile("Pictures/Tiles/Floor_1.png", "Pictures/Tiles/Floor_burning.png", 19, 9, 9))
map.append(Wall("Pictures/Tiles/Wall.png", 19, 10))

for tile in map:
    if isinstance(tile, Door):
        saveMap.append(((tile.x, tile.y), "door", tile.picturePath, tile.sector, tile.pictureClosedPath, tile.isOpen, tile.burningPictureFilePath))
    elif isinstance(tile, Wall):
        saveMap.append(((tile.x, tile.y), "wall", tile.picturePath))
    elif isinstance(tile, EntryPoint):
        saveMap.append(((tile.x, tile.y), "entry", tile.picturePath, tile.face))
    elif isinstance(tile, ControlledArea):
        saveMap.append(((tile.x, tile.y), "control", tile.picturePath, tile.sector, tile.burningPictureFilePath))
    elif isinstance(tile, Tile):
        saveMap.append(((tile.x, tile.y), "tile", tile.picturePath, tile.sector, tile.burningPictureFilePath))

smModelList = []
smModelSaveList = []
smModelList.append(SpaceMarine("Powersword", "sergant"))
smModelList.append(SpaceMarine("Flamer", "brother"))
smModelList.append(SpaceMarine("Bolter", "brother"))
smModelList.append(SpaceMarine("Bolter", "brother"))
smModelList.append(SpaceMarine("Bolter", "brother"))

for model in smModelList:
    smModelSaveList.append((model.weapon, model.rank))

data = {
    "level": 1,
    "blipList" : a,
    "map" : saveMap,
    "startBlip": 2,
    "reinforcement" : 2,
    "smModelList" : smModelSaveList,
    "broodLord": False
}

# File path to save the JSON file
file_path = "Levels/level_1.json"

# Writing data to the JSON file
with open(file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)

with open(file_path, 'r') as json_file:
    data = json.load(json_file)

# Printing loaded data
print(data)