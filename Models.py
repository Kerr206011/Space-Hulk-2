import pygame

class Item:
    def __init__(self, picture) -> None:
        self.picture = pygame.image.load(picture)
        self.carrier = None

class Model:
    def __init__(self, AP, picture):
        self.AP = AP
        self.picture = pygame.image.load(picture)
        self.pictureFilePath = picture
        self.face = (1,0)
        self.item = None
        
class SpaceMarine(Model):
    def __init__(self, weapon, rank, picture):
        super().__init__(4, picture)
        self.weapon = weapon
        self.rank = rank
        self.susf = False
        self.overwatch = False
        self.guard = False
        self.jam = False

    def __str__(self):
        return f"Spacemarine: {self.rank}, {self.weapon}"
    
    def __repr__(self):
        return f"<Spacemarine: Rank = {self.rank}, weapon = {self.weapon}>"

class Genestealer(Model):
    def __init__(self):
        super().__init__(6, 'Pictures/Models/Gs.png')
        self.isBroodlord = False
        self.lurking = False

class Blip(Model):
    def __init__(self, count):
        super().__init__(6, 'Pictures/Models/Blip.PNG')
        self.count = count
        self.lurking = False