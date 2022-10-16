import pygame

from .tile import Tile

class Pig():
    def __init__(self, tile: Tile):
        self.pos = tile.getCP()

    def move(self, point: tuple):
        self.pos = point
