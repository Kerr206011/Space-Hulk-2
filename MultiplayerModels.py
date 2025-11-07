from enum import Enum

class Facing(Enum):
    NORTH = (0,-1)
    EAST = (1,0)
    SOUTH = (0,1)
    WEST = (-1,0)

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

    def __init__(self, face: Facing = Facing.NORTH, activated = False, position_x = None, position_y = None):
        self.activated = activated
        self.face = face
        self.position_x = position_x
        self.position_y = position_y

    def __repr__(self):
        return f"<Model ap={self.ap}, pos={(self.position_x, self.position_y)}, face={self.face}>"
    
class SpaceMarine(Model):
    def __init__(self, weapon: str, rank: str, item = None):
        super().__init__()
        self.weapon = Weapon[weapon.upper()]
        self.rank = rank
        self.sustained_fire = False
        self.overwatch = False
        self.guard = False
        self.jam = False
        self.item = item

    def __repr__(self):
        return (f"<SpaceMarine rank={self.rank}, weapon={self.weapon.name}, "
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
                "item":self.item}
    
    def send(self):
        match self.weapon:
            case _:
                picture_path = "Pictures/Models/Brother.png"

        return{
            "pos_x":self.position_x,
            "pos_y":self.position_y,
            "face":self.face.value,
            "picture":picture_path
        }

class Blip(Model):
    def __init__(self, count):
        super().__init__()
        self.count = count

    def __repr__(self):
        return f"<Blip ap={self.activated}, amount={self.count}>"
    
    def to_dict(self):
        return {"ap" : self.activated,
                "pos_x":self.position_x,
                "pos_y":self.position_y,
                "count" : self.count}
    
    def send(self):
        return{
            "x":self.position_x,
            "y":self.position_y,
        }

class Genstealer(Model):
    def __init__(self, broodlord):
        super().__init__()
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
        return Tile(data["x"], data["y"], data["sector"], data["picture"], data["is_burning"], data["has_item"], data["item"], data["is_occupied"], data["occupant"])

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
        return Door(data["x"], data["y"], data["sector"], data["picture"], data["is_burning"], data["has_item"], data["item"], data["is_occupied"], data["occupant"], data["is_open"])


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
        return Wall(data["x"], data["y"], data["sector"], data["picture"])
    
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
        self.face = face

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
            "face": self.face
        }

class Ladder:
    pass