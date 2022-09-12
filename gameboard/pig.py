import pygame

class Pig():
    def __init__(self, tile):
        self.pos = tile.getCP()

    def move(self, point):
        self.pos = point
