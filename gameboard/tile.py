import pygame
from collections import OrderedDict

class Tile():
    def __init__(self, doubleCoord: tuple, loc: list, blocked=False):
        self.neighbors = OrderedDict()
        self.blocked = blocked
        self.CP = doubleCoord
        self.mouse_loc = loc
        self.x = loc[0]
        self.y = loc[1]

    def getPixelCoord(self):
        return self.mouse_loc

    def getCP(self):
        return self.CP

    def __repr__(self):
        return f"{self.blocked}"
