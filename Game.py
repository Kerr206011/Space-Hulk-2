import json
import random
from Board import *
from Models import *
import logging

logging.basicConfig(
    level=logging.DEBUG,  # Set to INFO, WARNING, or ERROR as needed
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("game.log"),  # Save logs to a file
        logging.StreamHandler()          # Also log to console
    ]
)

logger = logging.getLogger(__name__)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow keyboard interrupts to exit silently
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

# Override the default exception handler
sys.excepthook = handle_exception

class Game():
    def __init__(self) -> None:
        self.map = []       #A list to save all the board tiles
        self.blipSack = []      #A list of integers to represent the Stack of bips that can still be drawn from 
        self.blipReserve = []   #A list of integers to represent the already used blips
        self.cp = random.randint(1,6)   #An integer to represent the CP available to the SM player
        self.player1 = "Player_1"; self.player2 = "Player_2"    #Names of player 1/2
        self.isPlaying = self.player1   #depricated for now, can be important if the game goes online
        self.gsModelList = [];self.smModelList = [];self.blModelList = []   #Lists to represent the three diffrent types of models 
        self.level = int    #Integer to save the levelnumber, important for saving and loading
        self.startBlip = int    #Amount of blips given at the start of the game
        self.reinforcement = int    #Amount of blips given each round
        self.selectedTile:Tile = None    #Saved tiles/models. Most of the time for internal logic
        self.clickedTile:Tile = None
        self.selectedModel:Model = None
        self.clickedModel:Model = None
        self.assaultCannonAmmo = 10 #Self explainatory
        self.assaultCannonReload = True 
        self.psykerPhase = False
        self.flamerAmmo = 6
        self.psyPoints = 20
        self.broodLord = False
        self.maxGS = 23 #including Broodlord as he is classified as a Genstealer
        self.reuseBlips = -1

    def make_save(self, name, phase):
        # perhaps split into autosave and manualsave
        """
        Method that makes a .json savefile. Right now many of the parameters are depricated, but that may change if i decide to 
        add saving during the round.

        Args:
            name: String
            phase: String (Current gamephase)

        Returns:
            None
        """
        saveMap = []
        smSaveList = []
        gsSaveList = []
        blSaveList = []
        burningTiles = []
        lurkers = []
        
        
        for tile in self.map:
            if isinstance(tile, Door):
                saveMap.append(((tile.x, tile.y), "door", tile.picturePath, tile.sector, tile.pictureClosedPath, tile.isOpen, tile.burningPictureFilePath))
            elif isinstance(tile, Wall):
                saveMap.append(((tile.x, tile.y), "wall", tile.picturePath))
            elif isinstance(tile, EntryPoint):
                saveMap.append(((tile.x, tile.y), "entry", tile.picturePath, tile.face))
                if tile.blips.__len__() != 0:
                    for blip in tile.blips:
                        lurkers.append(("bl",(tile.x, tile.y), blip.count, blip.lurking, blip.AP))
                if tile.genstealers.__len__() != 0:
                    for entry in tile.genstealers:
                        lurkers.append(("gs", (tile.x, tile.y), entry.lurking, entry.isBroodlord, entry.AP))
            elif isinstance(tile, ControlledArea):
                saveMap.append(((tile.x, tile.y), "control", tile.picturePath, tile.sector, tile.burningPictureFilePath))
            elif isinstance(tile, Tile):
                saveMap.append(((tile.x, tile.y), "tile", tile.picturePath, tile.sector, tile.burningPictureFilePath))

            if isinstance(tile, Tile):

                if tile.isOccupied:
                    if isinstance(tile.occupand, SpaceMarine):
                        smSaveList.append(((tile.x, tile.y), tile.occupand.weapon, tile.occupand.rank, tile.occupand.AP, tile.occupand.face, tile.occupand.guard, tile.occupand.jam, tile.occupand.overwatch, tile.occupand.susf, tile.occupand.pictureFilePath))

                    elif isinstance(tile.occupand, Genestealer):
                        gsSaveList.append(((tile.x, tile.y), tile.occupand.isBroodlord, tile.occupand.AP, tile.occupand.face))

                    elif isinstance(tile.occupand, Blip):
                        blSaveList.append(((tile.x, tile.y), tile.occupand.count, tile.occupand.AP))

                if tile.isBurning:
                    burningTiles.append((tile.x, tile.y))

        phase = phase

        data = { 
            "map" : saveMap,
            "smList" : smSaveList,
            "gsList" : gsSaveList,
            "blList" : blSaveList,
            "burning" : burningTiles,
            "level" : self.level,
            "blipsack" : self.blipSack,
            "blipreserve" : self.blipReserve,
            "player1" : self.player1,
            "player2" : self.player2,
            "reinforcement" : self.reinforcement,
            "assaultcannonammo" : self.assaultCannonAmmo,
            "reload" : self.assaultCannonReload,
            "flamer" : self.flamerAmmo,
            "psypoints" : self.psyPoints,
            "broodlord" : self.broodLord,
            "maxGS" : self.maxGS,
            "reuse" : self.reuseBlips,
            "cp" : self.cp,
            "lurkers" : lurkers,
            "startBlip" : self.startBlip,
            "phase" : phase
        }

        # File path to save the JSON file
        file_path = "Levels/"+name+".json"

        # Writing data to the JSON file
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        logger.debug(f"Sucessfully created save {name}.")

    def load_save(self, name):
        file_path = "Levels/"+name+".json"

        logger.info(file_path)

        with open(file_path, 'r') as json_file:
            data = json.load(json_file)

        self.level = data["level"]
        self.blipSack = data["blipsack"]
        self.blipReserve = data["blipreserve"]
        self.reinforcement = data["reinforcement"]
        smList = data["smList"]
        gsList = data["gsList"]
        blList = data["blList"]
        bluePrint = data["map"]
        lurkers = data["lurkers"]
        burning = data["burning"]
        phase = data["phase"]
        self.startBlip = data["startBlip"]
        self.player1 = data["player1"]
        self.player2 = data["player2"]
        self.cp = data["cp"]
        self.reuseBlips = data["reuse"]
        self.broodLord = data["broodlord"]
        self.maxGS = data["maxGS"]
        self.psyPoints = data["psypoints"]
        self.flamerAmmo = data["flamer"]
        self.assaultCannonReload = data["reload"]
        self.assaultCannonAmmo = data["assaultcannonammo"]
        self.reinforcement = data["reinforcement"]

        for entry in bluePrint:

            if entry[1] == "tile":
                newTile = Tile(entry[2], entry[4], entry[0][0],entry[0][1],entry[3])
                self.map.append(newTile)

            elif entry[1] == "door":
                newDoor = Door(entry[2], entry[4], entry[6], entry[0][0], entry[0][1], entry[3], entry[5])
                if entry[5] == False:
                    newDoor.change_picture(newDoor.pictureClosedPath)
                self.map.append(newDoor)

            elif entry[1] == "wall":
                newWall = Wall(entry[2],entry[0][0],entry[0][1])
                self.map.append(newWall)

            elif entry[1] == "entry":
                newEntry = EntryPoint(entry[2],entry[0][0],entry[0][1],entry[3])
                self.map.append(newEntry)

            elif entry[1] == "control":
                newControl = ControlledArea(entry[2],entry[4],entry[0][0],entry[0][1],entry[3])
                self.map.append(newControl)

        for entry in smList:
            newMarine = SpaceMarine(entry[1], entry[2], entry[9])
            newMarine.AP = entry[3]
            face = entry[4]
            match face:
                case (1,0): 
                    pass
                case (0,1):
                    self.turn_model(newMarine, "right")
                case(-1,0):
                    self.turn_model(newMarine, "full")
                case(0,-1):
                    self.turn_model(newMarine, "left")  
            #add rotation
            newMarine.guard = entry[5]
            newMarine.jam = entry[6]
            newMarine.overwatch = entry[7]
            newMarine.susf = entry[8]

            self.smModelList.append(newMarine)

            for tile in self.map:
                if tile.x == entry[0][0] and tile.y == entry[0][1]:
                    target = tile
            target.isOccupied = True
            target.occupand = newMarine

        for entry in gsList:
            newGenstealer = Genestealer()
            newGenstealer.AP = entry[2]
            newGenstealer.isBroodlord = entry[1]

            self.gsModelList.append(newGenstealer)

            face = entry[3]
            match face:
                case (1,0): 
                    pass
                case (0,1):
                    self.turn_model(newGenstealer, "right")
                case(-1,0):
                    self.turn_model(newGenstealer, "full")
                case(0,-1):
                    self.turn_model(newGenstealer, "left")  

            for tile in self.map:
                if tile.x == entry[0][0] and tile.y == entry[0][1]:
                    target = tile
            target.isOccupied = True
            target.occupand = newGenstealer

        for entry in blList:
            newBlip = Blip(entry[1])
            newBlip.AP = entry[2]

            self.blModelList.append(newBlip)

            for tile in self.map:
                if tile.x == entry[0][0] and tile.y == entry[0][1]:
                    target = tile
            target.isOccupied = True
            target.occupand = newBlip

        for entry in lurkers:
            if entry[0] == "gs":
                for tile in self.map:
                    if tile.x == entry[1][0] and tile.y == entry[1][1]:
                        target = tile
                lurkerGS = Genestealer()
                lurkerGS.AP = entry[4]
                lurkerGS.lurking = entry[2]
                lurkerGS.isBroodlord = entry[3]
                target.genstealers.append(lurkerGS)
                
                self.gsModelList.append(lurkerGS)
                
            elif entry[0] == "bl":
                for tile in self.map:
                    if tile.x == entry[1][0] and tile.y == entry[1][1]:
                        target = tile
                lurkerBlip = Blip(entry[2])
                lurkerBlip.lurking = entry[3]
                lurkerBlip.AP = entry[4]
                target.blips.append(lurkerBlip)

                self.blModelList.append(lurkerBlip)

        for entry in burning:
            for tile in self.map:
                if tile.x == entry[0][0] and tile.y == entry[0][1]:
                    target = tile

            target.change_picture(target.burningPictureFilePath)
            target.isBurning = True
        
        logger.info(f"Phase: {phase}")

    def load_level(self,levelFile):
        file_path = "Levels/"+levelFile+".json"

        logger.info(file_path)

        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            
        self.level = data["level"]
        self.blipSack = data["blipList"]
        self.reinforcement = data["reinforcement"]
        smList = data["smModelList"]
        self.broodLord = data["broodLord"]
        self.startBlip = data["startBlip"]

        bluePrint = data["map"]
        for entry in smList:
            self.smModelList.append(SpaceMarine(entry[0],entry[1], entry[2]))
            
        for entry in bluePrint:

            if entry[1] == "tile":
                newTile = Tile(entry[2], entry[4], entry[0][0],entry[0][1],entry[3])
                self.map.append(newTile)

            elif entry[1] == "door":
                newDoor = Door(entry[2], entry[4], entry[6], entry[0][0], entry[0][1], entry[3], entry[5])
                if entry[5] == False:
                    newDoor.change_picture(newDoor.pictureClosedPath)
                self.map.append(newDoor)

            elif entry[1] == "wall":
                newWall = Wall(entry[2],entry[0][0],entry[0][1])
                self.map.append(newWall)

            elif entry[1] == "entry":
                newEntry = EntryPoint(entry[2],entry[0][0],entry[0][1],entry[3])
                self.map.append(newEntry)

            elif entry[1] == "control":
                newControl = ControlledArea(entry[2],entry[4],entry[0][0],entry[0][1],entry[3])
                self.map.append(newControl)

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

    def reset_select(self):
        self.selectedModel = None
        self.selectedTile = None
        logger.debug(f"Reset selectedModel and Tile to None")

    def reset_clicked(self):
        self.clickedModel = None
        self.clickedTile = None
        logger.debug(f"Reset ClickedModel and Tile to None")

    def destroy_model(self, model, tile):
        if model == self.selectedModel:
            self.selectedModel = None
            self.selectedTile = None
        elif model == self.clickedModel:
            self.clickedModel = None
        if model in self.smModelList:
            self.smModelList.remove(model)
            tile.isOccupied = False
            tile.occupand = None
        if model in self.gsModelList:
            self.gsModelList.remove(model) 
            tile.isOccupied = False
            tile.occupand = None
        if model in self.blModelList:
            self.blipReserve.append(model.count)
            self.blModelList.remove(model)
            tile.isOccupied = False
            tile.occupand = None
        if model.item != None:
            tile.occupand = model.item

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

    def melee(self, attacker, defender, roll_1, roll_2, roll_3, roll_4, roll_5, pyscic):       #depricated, oly here for reference 
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
    
    def melee_door(self, attacker, roll_1, roll_2, roll_3, psycic):
        if roll_3 == 0:
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

        elif attacker.isBroodlord:
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

        if roll_1 > 5 or roll_2 > 5 or roll_3 > 5:
            return True

    def overwatch_bolter(self, shooter, targetTile):
        hit = False

        if shooter.susf == True:
            roll_1 += 1
            roll_2 += 1

        if targetTile.isOccupied:
            if targetTile.occupand.isBroodlord == True:
                if roll_1 > 5 and roll_2 > 5:
                    hit = True
            else:
                if roll_1 > 5 or roll_2 > 5:
                    hit = True

        shooter.susf = True

        if roll_1 == roll_2:
            shooter.jam = True

        return hit
    

    def get_tile(self, x, y):
        for tile in self.map:
            if tile.x == x and tile.y == y:
                return tile
            
    def check_vision(self, model, tile):
        checkedtile = None
        isBlocked = False 
        visionList = []
        runMiddle = True
        runLeft1 = True
        runLeft2 = True
        runRight1 = True
        runRight2 = True

        ofsX = int
        ofsY = int
        x = tile.x
        y = tile.y
        i = 0

        match model.face:
            case (1, 0):
                ofsX = 0
                ofsY = 1
            case (-1, 0):
                ofsX = 0
                ofsY = 1
            case (0, 1):
                ofsX = 1
                ofsY = 0
            case (0, -1):
                ofsX = 1
                ofsY =0

        while runMiddle:
            if abs(x) > 100 or abs(y) > 100:
                logger.debug(f"Checked Distance over 100!")
                isBlocked = True
            x += model.face[0]
            y += model.face[1]
            checkedtile = self.get_tile(x, y)

            if isinstance(checkedtile, Tile):
                visionList.append(checkedtile)

                if isinstance(checkedtile, Door):
                    if checkedtile.isOpen == False:
                        isBlocked = True

                if checkedtile.isOccupied:
                    isBlocked = True

                if checkedtile.isBurning:
                    isBlocked = True

            if isinstance(checkedtile, Wall):
                isBlocked = True

            if isinstance(checkedtile, EntryPoint):
                isBlocked = True

            if isBlocked:
                if i == 0:
                    runMiddle = False
                    runLeft1 = False
                    runLeft2 = False
                    runRight1 = False
                    runRight2 = False
    
                else:
                    runMiddle = False
                    i = 0
                    x = tile.x + ofsX + model.face[0]
                    y = tile.y + ofsY + model.face[1]
                    isBlocked = False
            
            else:
                i +=1

        while runLeft1:
            if abs(x) > 100 or abs(y) > 100:
                logger.critical(f"Checked Distance over 100!")
                pygame.quit()
                sys.exit()
            checkedtile = self.get_tile(x, y)

            if isinstance(checkedtile, Tile):
                visionList.append(checkedtile)

                if isinstance(checkedtile, Door):
                    if checkedtile.isOpen == False:
                        isBlocked = True

                if checkedtile.isOccupied:
                    isBlocked = True

                if checkedtile.isBurning:
                    isBlocked = True

            if isinstance(checkedtile, Wall):
                isBlocked = True

            if isinstance(self.get_tile(checkedtile.x + ofsX, checkedtile.y + ofsY), Wall) and isinstance(self.get_tile(checkedtile.x - ofsX, checkedtile.y - ofsY), Wall):
                isBlocked = True

            if isinstance(checkedtile, EntryPoint):
                isBlocked = True

            if isBlocked:
                if i == 0:
                    runLeft1 = False
                    runLeft2 = False
    
                else:
                    runLeft1 = False
                    i = 0
                    x = tile.x + 2 * ofsX + 2 * model.face[0]
                    y = tile.y + 2 * ofsY + 2 * model.face[1]
                    isBlocked = False
            
            else:
                i +=1   
                x += model.face[0]
                y += model.face[1]

        while runLeft2:
            if abs(x) > 100 or abs(y) > 100:
                logger.critical(f"Checked Distance over 100!")
                pygame.quit()
                sys.exit()
            checkedtile = self.get_tile(x, y)

            if isinstance(checkedtile, Tile):
                visionList.append(checkedtile)

                if isinstance(checkedtile, Door):
                    if checkedtile.isOpen == False:
                        isBlocked = True

                if checkedtile.isOccupied:
                    isBlocked = True

                if checkedtile.isBurning:
                    isBlocked = True

            if isinstance(self.get_tile(checkedtile.x + ofsX, checkedtile.y + ofsY), Wall) and isinstance(self.get_tile(checkedtile.x - ofsX, checkedtile.y - ofsY), Wall):
                isBlocked = True

            if isinstance(checkedtile, EntryPoint):
                isBlocked = True

            if isinstance(checkedtile, Wall):
                isBlocked = True

            if isBlocked:
                runLeft2 = False
                i = 0
                x = tile.x - ofsX + model.face[0]
                y = tile.y - ofsY + model.face[1]
                isBlocked = False
            
            else:
                i +=1   
                x += model.face[0]
                y += model.face[1]

        while runRight1:
            if abs(x) > 100 or abs(y) > 100:
                logger.critical(f"Checked Distance over 100!")
                pygame.quit()
                sys.exit()
            checkedtile = self.get_tile(x, y)

            if isinstance(checkedtile, Tile):
                visionList.append(checkedtile)

                if isinstance(checkedtile, Door):
                    if checkedtile.isOpen == False:
                        isBlocked = True

                if checkedtile.isOccupied:
                    isBlocked = True

                if checkedtile.isBurning:
                    isBlocked = True

            if isinstance(self.get_tile(checkedtile.x + ofsX, checkedtile.y + ofsY), Wall) and isinstance(self.get_tile(checkedtile.x - ofsX, checkedtile.y - ofsY), Wall):
                isBlocked = True

            if isinstance(checkedtile, EntryPoint):
                isBlocked = True

            if isinstance(checkedtile, Wall):
                isBlocked = True

            if isBlocked:
                if i == 0:
                    runRight1 = False
                    runRight2 = False
    
                else:
                    runRight1 = False
                    i = 0
                    x = tile.x - 2 * ofsX + 2 * model.face[0]
                    y = tile.y - 2 * ofsY + 2 * model.face[1]
                    isBlocked = False
            
            else:
                i +=1   
                x += model.face[0]
                y += model.face[1]

        while runRight2:
            if abs(x) > 100 or abs(y) > 100:
                logger.critical(f"Checked Distance over 100!")
                pygame.quit()
                sys.exit()
            checkedtile = self.get_tile(x, y)

            if isinstance(checkedtile, Tile):
                visionList.append(checkedtile)

                if isinstance(checkedtile, Door):
                    if checkedtile.isOpen == False:
                        isBlocked = True

                if checkedtile.isOccupied:
                    isBlocked = True

                if checkedtile.isBurning:
                    isBlocked = True

            if isinstance(self.get_tile(checkedtile.x + ofsX, checkedtile.y + ofsY), Wall) and isinstance(self.get_tile(checkedtile.x - ofsX, checkedtile.y - ofsY), Wall):
                isBlocked = True

            if isinstance(checkedtile, EntryPoint):
                isBlocked = True

            if isinstance(checkedtile, Wall):
                isBlocked = True

            if isBlocked:
                runRight2 = False
            
            else:
                i +=1   
                x += model.face[0]
                y += model.face[1]

        return visionList
                    
    def interact_door(self, door):
        if door.isOpen:
            door.isOpen = False
            door.change_picture(door.pictureClosedPath)
        else:
            door.isOpen = True
            door.change_picture(door.picturePath)

    def check_full_vision(self):
        fullVisionList = []
        visionlist = []
        for tile in self.map:
            if isinstance(tile, Tile):
                if tile.isOccupied:
                    if tile.occupand in self.smModelList:
                        fullVisionList.append(self.check_vision(tile.occupand, tile))
        for vlist in fullVisionList:
            for tile in vlist:
                if tile not in visionlist:
                    visionlist.append(tile)
        return visionlist
    
    def check_overwatch(self, activationType = "normal", target = None):
        overwatchingModels = []

        if activationType == "door":

            for tile in self.map:
                if isinstance(tile, Tile):
                    if tile.isOccupied:
                        if tile.occupand in self.smModelList:
                            if self.selectedTile in self.check_vision(tile.occupand, tile) or self.clickedTile in self.check_vision(tile.occupand, tile):
                                if tile.occupand.weapon != "Thunderhammer" and tile.occupand.weapon != "Lightningclaws" and tile.occupand.weapon != "Flamer":
                                    if tile.occupand.overwatch and (not tile.occupand.jam) and not ((tile.occupand.weapon == "Assaultcannon") and (self.assaultCannonAmmo == 0)):
                                        overwatchingModels.append(tile)

        elif activationType == "reveal":
            for tile in self.map:
                if isinstance(tile, Tile):
                    if tile.isOccupied:
                        if tile.occupand in self.smModelList:
                            if target in self.check_vision(tile.occupand, tile):
                                if tile.occupand.weapon != "Thunderhammer" and tile.occupand.weapon != "Lightningclaws" and tile.occupand.weapon != "Flamer":
                                    if tile.occupand.overwatch and (not tile.occupand.jam) and not ((tile.occupand.weapon == "Assaultcannon") and (self.assaultCannonAmmo == 0)):
                                        overwatchingModels.append(tile)

        else:
            for tile in self.map:
                if isinstance(tile, Tile):
                    if tile.isOccupied:
                        if tile.occupand in self.smModelList:
                            if self.selectedTile in self.check_vision(tile.occupand, tile):
                                if tile.occupand.weapon != "Thunderhammer" and tile.occupand.weapon != "Lightningclaws" and tile.occupand.weapon != "Flamer":
                                    if tile.occupand.overwatch and (not tile.occupand.jam) and not ((tile.occupand.weapon == "Assaultcannon") and (self.assaultCannonAmmo == 0)):
                                        overwatchingModels.append(tile)

        logger.debug(f"Found {overwatchingModels.__len__()} overwatching models!")
        return overwatchingModels
    
    def check_path(self,startTile, targetTile, maxDist):
        visited = [startTile]
        x = 0

        while x < maxDist:
            for start in visited[:]:
                for tile in self.map:
                    if ((tile.x + 1 == start.x) or (tile.x - 1 == start.x) or (tile.x == start.x)) and ((tile.y + 1 == start.y) or (tile.y - 1 == start.y) or (tile.y == start.y)):
                        if isinstance(tile, Tile):
                            if tile not in visited:
                                visited.append(tile)
            x += 1
            if targetTile in visited:
                logger.info(f"TargetTile {targetTile} in distance of {x}.")
                return True
        logger.info(f"TargetTile not within {maxDist}.")
        return False
    
    def center_tile(self, tile:Tile, screen):
        screen.fill('black')

        ofs_x = 0
        ofs_y = 0

        center_x = screen.get_width()/2
        center_y = screen.get_height()/2

        org_pos_x = tile.graphicsX * tile.graphicOFS
        org_pos_y = tile.graphicsY * tile.graphicOFS

        ofs_x = (center_x - org_pos_x) / tile.graphicOFS
        ofs_y = (center_y - org_pos_y) / tile.graphicOFS

        for tile in self.map:
            tile.scroll((ofs_x, ofs_y))
            tile.render(screen)
        
        pygame.display.flip()


# game = Game()
# game.load_level("level_1")
# print(game.map)