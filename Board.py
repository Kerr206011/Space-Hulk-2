from UI import *
# from Models import *
class Tile:
    def __init__(self, picture, x, y, sector) -> None:
        self.picture = pygame.image.load(picture)
        self.x = x
        self.y = y
        self.sector = sector
        self.isOccupied = False
        self.occupand = None

    def render(self, screen):
        pass

class Wall(Tile):
    def __init__(self, picture, x, y) -> None:
        super().__init__(picture, x, y, None)

class Door(Tile):
    def __init__(self, picture_cosed, x, y, sector, isOpen) -> None:
        super().__init__(picture, x, y, sector)
        self.isOpen = isOpen
        self.picture_closed = picture_cosed