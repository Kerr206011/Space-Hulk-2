import json
from Board import *

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
map.append(ControlledArea("Pictures/Tiles/SM_entry.png", 1, 12, 0))
map.append(Wall("Pictures/Tiles/Wall.png", 1, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 2, 11))
map.append(ControlledArea("Pictures/Tiles/SM_entry.png", 2, 12, 0))
map.append(Wall("Pictures/Tiles/Wall.png", 2, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 3, 11))
map.append(ControlledArea("Pictures/Tiles/SM_entry.png", 3, 12, 0))
map.append(Wall("Pictures/Tiles/Wall.png", 3, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 4, 11))
map.append(ControlledArea("Pictures/Tiles/SM_entry.png", 4, 12, 0))
map.append(Wall("Pictures/Tiles/Wall.png", 4, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 5, 11))
map.append(ControlledArea("Pictures/Tiles/SM_entry.png", 5, 12, 0))
map.append(Wall("Pictures/Tiles/Wall.png", 5, 13))
map.append(Wall("Pictures/Tiles/Wall.png", 6, 10))
map.append(Wall("Pictures/Tiles/Wall.png", 6, 11))
map.append(Door("Pictures/Tiles/Door_open.png", "Pictures/Tiles/Door.png", 6, 12, 1, False))

for tile in map:
    if isinstance(tile, Door):
        saveMap.append(((tile.x, tile.y), "door", tile.picturePath, tile.sector, tile.pictureClosedPath, tile.isOpen))
    elif isinstance(tile, Wall):
        saveMap.append(((tile.x, tile.y), "wall", tile.picturePath))
    elif isinstance(tile, EntryPoint):
        saveMap.append(((tile.x, tile.y), "entry", tile.picturePath))
    elif isinstance(tile, ControlledArea):
        saveMap.append(((tile.x, tile.y), "control", tile.picturePath, tile.sector))

data = {
    "level": 1,
    "blipList" : a,
    "map" : saveMap,
    "reinforcement" : 2
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
