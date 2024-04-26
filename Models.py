import pygame

class Model:
    def __init__(self, AP, picture):
        self.AP = AP
        self.picture = pygame.image.load(picture)
        self.face = (1,0)

class SpaceMarine(Model):
    def __init__(self, weapon, rank):
        super().__init__(4,'Pictures/Models/SM.png')
        self.weapon = weapon
        self.rank = rank
        self.susf = False
        self.overwatch = False
        self.guard = False
        self.jam = False

class Genestealer(Model):
    def __init__(self):
        super().__init__(6, 'Pictures/Models/Gs.png')
        self.isBroodlord = False

class Blip(Model):
    def __init__(self, count):
        super().__init__(6, 'Pictures/Models/Blip.PNG')
        self.count = count