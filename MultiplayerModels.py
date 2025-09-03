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

    def __init__(self, ap: int, face: Facing = Facing.NORTH, item=None):
        self.ap = ap
        self.face = face
        self.item = item
        self.position = None

    def __repr__(self):
        return f"<Model ap={self.ap}, pos={self.position}, face={self.face}>"
    
class SpaceMarine(Model):
    def __init__(self, weapon: str, rank: str):
        super().__init__(ap=4)
        self.weapon = Weapon[weapon.upper()]
        self.rank = rank
        self.sustained_fire = False
        self.overwatch = False
        self.guard = False
        self.jam = False

    def __repr__(self):
        return (f"<SpaceMarine rank={self.rank}, weapon={self.weapon.name}, "
                f"ap={self.ap}, overwatch={self.overwatch}, jam={self.jam}>")
    
    def to_dict(self):
        return {"ap":self.ap,
                "pos":self.position,
                "weapon":self.weapon.value,
                "rank":self.rank,
                "susf":self.sustained_fire,
                "overwatch":self.overwatch,
                "guard":self.guard,
                "jam":self.jam}

class Blip(Model):
    def __init__(self, ap, count, face = Facing.NORTH, item=None):
        super().__init__(ap, face, item)
        self.count = count

    def __repr__(self):
        return f"<Blip ap={self.ap}, amount={self.amount}>"
    
    def to_dict(self):
        return {"ap" : self.ap,
                "pos":self.position,
                "amount" : self.amount}

class Genstealer(Model):
    def __init__(self, ap, broodlord, face = Facing.NORTH, item=None):
        super().__init__(ap, face, item)
        self.broodlord = broodlord

    def __repr__(self):
        return f"<Genstealer ap={self.ap}, face={self.face}, Broodlord={self.broodlord}>"
    
    def to_dict(self):
        return {"ap" : self.ap,
                "pos": self.position,
                "face" : self.face.value,
                "broodlord" : self.broodlord}