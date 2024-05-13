from UI import *

class Tile:
    def __init__(self, picture, x, y, sector) -> None:

        self.picturePath = picture
        self.sector = sector
        self.scale = 0.7
        self.picture = pygame.image.load(picture)

        self.graphicOFS = self.picture.get_width() * self.scale
        self.graphicsX = x
        self.graphicsY = y

        self.button = Button(self.graphicsX, self.graphicsY, self.picture, self.scale)

        self.button.rect.topleft = ((self.graphicsX * self.graphicOFS),(self.graphicsY * self.graphicOFS))

        self.x = x
        self.y = y
        self.sector = sector
        self.isOccupied = False
        self.occupand = None
        self.isBurning = False
        self.hasItem = False
        self.item = None

    def scroll(self, input):
        self.graphicsX += input[0]
        self.graphicsY += input[1]
        self.button.rect.topleft = ((self.graphicsX * self.graphicOFS),(self.graphicsY * self.graphicOFS))

    def render(self, screen):
        if self.isOccupied:
            self.button.show(screen, self.occupand.picture)
        else: 
            self.button.show(screen)

    def change_picture(self, imagePath):
        self.picture = pygame.image.load(imagePath)
        self.button.change_picture(self.picture)

class Wall:
    def __init__(self, picture, x, y) -> None:
        self.picturePath = picture
        self.scale = 0.7
        self.picture = pygame.image.load(picture)
        self.graphicOFS = self.picture.get_width() * self.scale
        self.graphicsX = x
        self.graphicsY = y

        self.button = Button(self.graphicsX, self.graphicsY, self.picture, self.scale)

        self.button.rect.topleft = ((self.graphicsX * self.graphicOFS),(self.graphicsY * self.graphicOFS))

        self.x = x
        self.y = y

    def scroll(self, input):
        self.graphicsX += input[0]
        self.graphicsY += input[1]
        self.button.rect.topleft = ((self.graphicsX * self.graphicOFS),(self.graphicsY * self.graphicOFS))

    def render(self, screen):
        self.button.show(screen)

class Door(Tile):
    def __init__(self, picture, picture_cosed, x, y, sector, isOpen) -> None:
        super().__init__(picture, x, y, sector)
        self.isOpen = isOpen
        self.pictureClosedPath = picture_cosed
        # self.picture_closed = pygame.image.load(picture_cosed)

    def get_destroyed(self):
        newTile = Tile("Pictures/Tiles/Floor_1.png", self.x, self.y, self.sector)
        return newTile

class ControlledArea(Tile):
    def __init__(self, picture, x, y, sector) -> None:
        super().__init__(picture, x, y, sector)

    def convert_to_tile(self):
        tile = Tile("Pictures/Tiles/Floor_1.png", self.x, self.y, self.sector)
        if self.isOccupied:
            tile.isOccupied = True
            tile.occupand = self.occupand
        tile.graphicsX = self.graphicsX
        tile.graphicsY = self.graphicsY
        tile.button.rect.topleft = ((self.graphicsX * self.graphicOFS),(self.graphicsY * self.graphicOFS))
        return tile

class EntryPoint:
    def __init__(self, picture, x, y, face) -> None:
        self.picturePath = picture
        self.scale = 0.7
        self.picture = pygame.image.load(picture)
        self.graphicOFS = self.picture.get_width() * self.scale
        self.graphicsX = x
        self.graphicsY = y

        self.button = Button(self.graphicsX, self.graphicsY, self.picture, self.scale)

        self.button.rect.topleft = ((self.graphicsX * self.graphicOFS),(self.graphicsY * self.graphicOFS))

        self.face = face

        self.x = x
        self.y = y
        self.blips = []

    def scroll(self, input):
        self.graphicsX += input[0]
        self.graphicsY += input[1]
        self.button.rect.topleft = ((self.graphicsX * self.graphicOFS),(self.graphicsY * self.graphicOFS))

    def render(self, screen):
        self.button.show(screen)
        #show the number of blips!