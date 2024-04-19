from UI import *
# from Models import *
class Tile:
    def __init__(self, picture, x, y, sector) -> None:
        self.scale = 1
        self.picture = pygame.image.load(picture)
        self.graphicOFS = self.picture.get_width()
        # self.picture = pygame.transform.scale(self.picture,(self.scale, self.scale))
        self.button = Button(x,y,self.picture,self.scale)
        self.button.rect.topleft = ((x * self.graphicOFS),(y * self.graphicOFS))
        self.x = x
        self.y = y
        self.sector = sector
        self.isOccupied = False
        self.occupand = None

    def render(self, screen):
        self.button.show(screen)
        if self.isOccupied:
            image = pygame.transform.scale(self.occupand.picture,self.scale,)

class Wall(Tile):
    def __init__(self, picture, x, y) -> None:
        super().__init__(picture, x, y, None)

class Door(Tile):
    def __init__(self, picture, picture_cosed, x, y, sector, isOpen) -> None:
        super().__init__(picture, x, y, sector)
        self.isOpen = isOpen
        self.picture_closed = picture_cosed