from UI import *
# from Models import *
class Tile:
    def __init__(self, picture, x, y, sector) -> None:
        self.scale = 1
        self.picture = pygame.image.load(picture)
        self.picture = pygame.transform.scale(self.picture,(self.scale, self.scale))
        self.x = x
        self.y = y
        self.sector = sector
        self.isOccupied = False
        self.occupand = None
        self.rect = self.picture.get_rect()

    def render(self, screen):
        pass

class Wall(Tile):
    def __init__(self, picture, x, y) -> None:
        super().__init__(picture, x, y, None)

class Door(Tile):
    def __init__(self, picture, picture_cosed, x, y, sector, isOpen) -> None:
        super().__init__(picture, x, y, sector)
        self.isOpen = isOpen
        self.picture_closed = picture_cosed