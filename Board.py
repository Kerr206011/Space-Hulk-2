from UI import *

class Tile:
    def __init__(self, picture, x, y, sector) -> None:
        self.sector = sector
        self.scale = 1
        self.picture = pygame.image.load(picture)
        self.graphicOFS = self.picture.get_width()
        self.button = Button(x,y,self.picture,self.scale)
        self.button.rect.topleft = ((x * self.graphicOFS),(y * self.graphicOFS))
        self.x = x
        self.y = y
        self.sector = sector
        self.isOccupied = False
        self.occupand = None
        self.isBurning = False

    def render(self, screen):
        if self.isOccupied:
            self.button.show(screen, self.occupand.picture)
        else: 
            self.button.show(screen)

class Wall:
    def __init__(self, picture, x, y) -> None:
        self.scale = 1
        self.picture = pygame.image.load(picture)
        self.graphicOFS = self.picture.get_width()
        self.button = Button(x,y,self.picture,self.scale)
        self.button.rect.topleft = ((x * self.graphicOFS),(y * self.graphicOFS))
        self.x = x
        self.y = y

    def render(self, screen):
        self.button.show(screen)

class Door(Tile):
    def __init__(self, picture, picture_cosed, x, y, sector, isOpen) -> None:
        super().__init__(picture, x, y, sector)
        self.isOpen = isOpen
        self.picture_closed = picture_cosed

class ControlledArea(Tile):
    def __init__(self, picture, x, y, sector) -> None:
        super().__init__(picture, x, y, sector)

class EntryPoint:
    def __init__(self, picture, x, y) -> None:
        self.scale = 1
        self.picture = pygame.image.load(picture)
        self.graphicOFS = self.picture.get_width()
        self.button = Button(x,y,self.picture,self.scale)
        self.button.rect.topleft = ((x * self.graphicOFS),(y * self.graphicOFS))
        self.x = x
        self.y = y
        self.blips = []

    def render(self, screen):
        self.button.show(screen)
        #show the number of blips!