from enum import Enum
import random

class Facing(Enum):
    _order_ = "NORTH EAST SOUTH WEST"

    NORTH = (0, -1)
    EAST  = (1, 0)
    SOUTH = (0, 1)
    WEST  = (-1, 0)

    def turn_right(self):
        members = list(Facing)
        idx = members.index(self)
        return members[(idx + 1) % 4]

    def turn_left(self):
        members = list(Facing)
        idx = members.index(self)
        return members[(idx - 1) % 4]

class Weapon(Enum):
    THUNDERHAMMER = "Thunderhammer"
    POWERSWORD = "Powersword"
    LIGHTNINGCLAWS = "Lightningclaws"
    BOLTER = "Bolter"
    ASSAULTCANNON = "Assaultcannon"
    FLAMER = "Flamer"
    AXE = "Axe"
    CHAINFIST = "Chainfist"

class Model:

    def __init__(self, face: Facing = Facing.NORTH, activated = False, position_x = None, position_y = None, ID = None):
        self.activated = activated
        self.face = face
        self.position_x = position_x
        self.position_y = position_y
        self.ID = ID

    def __repr__(self):
        return f"<Model ap={self.ap}, pos={(self.position_x, self.position_y)}, face={self.face}>"
    
class SpaceMarine(Model):
    def __init__(self, id, weapon: str, rank: str, item = None):
        super().__init__(ID = id)
        self.weapon = Weapon[weapon.upper()]
        self.rank = rank
        self.sustained_fire = False
        self.overwatch = False
        self.guard = False
        self.jam = False
        self.item = item

    def __repr__(self):
        return (f"<SpaceMarine id: {self.ID}, rank={self.rank}, weapon={self.weapon.name}, "
                f"overwatch={self.overwatch}, jam={self.jam}>")
    
    def to_dict(self):
        return {"activated":self.activated,
                "face":self.face.value,
                "pos_x":self.position_x,
                "pos_y":self.position_y,
                "weapon":self.weapon.value,
                "rank":self.rank,
                "susf":self.sustained_fire,
                "overwatch":self.overwatch,
                "guard":self.guard,
                "jam":self.jam,
                "item":self.item,
                "id": self.ID}
    
    def send(self):
        match self.weapon:
            case _:
                picture_path = "Pictures/Models/SM.png"

        return{
            "pos_x":self.position_x,
            "pos_y":self.position_y,
            "face":self.face.value,
            "picture":picture_path,
            "id": self.ID
        }

class Blip(Model):
    def __init__(self, count, id):
        super().__init__(ID = id)
        self.count = count

    def __repr__(self):
        return f"<Blip ap={self.activated}, amount={self.count}>"
    
    def to_dict(self):
        return {"ap" : self.activated,
                "pos_x":self.position_x,
                "pos_y":self.position_y,
                "count" : self.count,
                "id": self.ID}
    
    def send(self):
        return{
            "pos_x":self.position_x,
            "pos_y":self.position_y,
            "id": self.ID
        }

class Genstealer(Model):
    def __init__(self, broodlord, id):
        super().__init__(ID = id)
        self.broodlord = broodlord

    def __repr__(self):
        return f"<Genstealer ap={self.activated}, face={self.face}, Broodlord={self.broodlord}>"
    
    def to_dict(self):
        return {"ap" : self.activated,
                "pos_x": self.position_x,
                "pos_y":self.position_y,
                "face" : self.face.value,
                "broodlord" : self.broodlord}
    
    def send(self):
        return{
            "pos_x": self.position_x,
            "pos_y":self.position_y,
            "face" : self.face.value,
            "broodlord" : self.broodlord
        }
    
class OccupantType(Enum):
    NONE = 0
    SPACEMARINE = 1
    GENESTEALER = 2
    BLIP = 3
    
class Tile:
    def __init__(self, x, y, sector, picture = "Pictures/Tiles/Floor_1", is_burning = False, has_item = False, item = None, is_occupied = False, occupant = 0, tile_type = "tile"):
        self.x = x
        self.y = y
        self.sector = sector
        self.is_burning = is_burning
        self.has_item = has_item
        self.item = item
        self.is_occupied:bool = is_occupied
        self.occupant:OccupantType = OccupantType(occupant)
        self.picture = picture
        self.type = tile_type

    @classmethod
    def from_data(cls, data):
        return Tile(data["pos_x"], data["pos_y"], data["sector"], data["picture"], data["is_burning"], data["has_item"], data["item"], data["is_occupied"], data["occupant"])

    def to_dict(self):
        return {
            "pos_x": self.x,
            "pos_y": self.y,
            "sector": self.sector,
            "is_burning": self.is_burning,
            "has_item": self.has_item,
            "item": self.item,
            "is_occupied": self.is_occupied,
            "occupant": self.occupant.value,  # z.B. Model-ID oder None
            "picture": self.picture,
            "type": self.type
        }
    
    def send(self):
        return{
            "pos_x": self.x,
            "pos_y": self.y,
            "is_burning": self.is_burning,
            "has_item": self.has_item,
            "picture":  self.picture,
            "type": self.type
        }
    
class Door(Tile):
    def __init__(self, x, y, sector, picture="Pictures/Tiles/Door_V", is_burning=False, has_item=False, item=None, is_occupied=False, occupant=0, is_open = True, tile_type = "door"):
        super().__init__(x, y, sector, picture, is_burning, has_item, item, is_occupied, occupant, tile_type)
        self.is_open = is_open
    
    @classmethod
    def from_data(cls, data):
        return Door(data["pos_x"], data["pos_y"], data["sector"], data["picture"], data["is_burning"], data["has_item"], data["item"], data["is_occupied"], data["occupant"], data["is_open"])


    def to_dict(self):
        return {
            "pos_x": self.x,
            "pos_y": self.y,
            "sector": self.sector,
            "is_burning": self.is_burning,
            "has_item": self.has_item,
            "item": self.item,
            "is_occupied": self.is_occupied,
            "occupant": self.occupant.value,  # z.B. Model-ID oder None
            "picture": self.picture,
            "type": self.type,
            "is_open": self.is_open
        }
    
    def send(self):
        return{
            "pos_x": self.x,
            "pos_y": self.y,
            "is_burning": self.is_burning,
            "has_item": self.has_item,
            "picture":  self.picture,
            "type": self.type,
            "is_open": self.is_open
        }

class Wall(Tile):
    def __init__(self, x, y, sector, picture="Pictures/Tiles/Wall", is_burning=False, has_item=False, item=None, is_occupied=False, occupant=0, tile_type="wall"):
        super().__init__(x, y, sector, picture, is_burning, has_item, item, is_occupied, occupant, tile_type)

    @classmethod
    def from_data(cls, data):
        return Wall(data["pos_x"], data["pos_y"], data["sector"], data["picture"])
    
    def to_dict(self):
        return {
            "pos_x": self.x,
            "pos_y": self.y,
            "sector": self.sector,
            "picture": self.picture,
            "type": self.type
        }
    
    def send(self):
        return{
            "pos_x": self.x,
            "pos_y": self.y,
            "picture":  self.picture,
            "type": self.type
        }

class EntryPoint:
    def __init__(self, x, y, picture="Pictures/Tiles/lurking", tile_type="entry", face = (1,0)):
        self.x = x
        self.y = y
        self.picture = picture
        self.type = tile_type
        self.blips = []
        self.genstealer = []
        self.face = face

    @classmethod
    def from_data(cls, data):
        return EntryPoint(data["pos_x"], data["pos_y"], data["picture"], data["type"], data["face"])
    
    def send(self):
        return{
            "pos_x": self.x,
            "pos_y": self.y,
            "picture":  self.picture,
            "type": self.type,
            "blips": self.blips.__len__(),
            "face": self.face
        }
    
    def to_dict(self):
        bliplist = []
        for blip in self.blips:
            bliplist.append(blip.count)
        return {
            "pos_x": self.x,
            "pos_y": self.y,
            "picture": self.picture,
            "type": self.type,
            "bliplist": bliplist,
            "face": self.face,
            "genstealer": self.genstealer.__len__()
        }

class Ladder(Tile):
    def __init__(self, x, y, sector, partner, picture="Pictures/Tiles/Floor_1", is_burning=False, has_item=False, item=None, is_occupied=False, occupant=0, tile_type="ladder"):
        super().__init__(x, y, sector, picture, is_burning, has_item, item, is_occupied, occupant, tile_type)
        self.partner = partner

    @classmethod
    def from_data(cls, data):
        return Ladder(data["pos_x"], data["pos_y"], data["sector"], data["partner"], data["picture"], data["is_burning"], data["has_item"], data["item"], data["is_occupied"], data["occupant"])

    def to_dict(self):
        return {
            "pos_x": self.x,
            "pos_y": self.y,
            "sector": self.sector,
            "partner": self.partner,
            "is_burning": self.is_burning,
            "has_item": self.has_item,
            "item": self.item,
            "is_occupied": self.is_occupied,
            "occupant": self.occupant.value,  # z.B. Model-ID oder None
            "picture": self.picture,
            "type": self.type
        }
    
    def send(self):
        return{
            "pos_x": self.x,
            "pos_y": self.y,
            "is_burning": self.is_burning,
            "has_item": self.has_item,
            "picture":  self.picture,
            "type": self.type
        }
    
