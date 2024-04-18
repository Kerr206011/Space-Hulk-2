import pygame

class Tile:
    def __init__(self, picture, x, y, sector) -> None:
        self.picture = picture
        self.x = x
        self.y = y
        self.sector = sector

class Door(Tile):
    def __init__(self, picture, x, y, isOpen) -> None:
        super().__init__(picture, x, y)
        self.isOpen = isOpen