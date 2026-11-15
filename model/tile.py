import pygame
from constants import TILE_SIZE


class Tile:

    def __init__(self, col, row, terrain, color):
        self.col = col
        self.row = row
        self.terrain = terrain
        self.color = color

    def get_sprite(self, tile_size=TILE_SIZE):
        sprite = pygame.Surface((tile_size, tile_size))
        sprite.fill(self.color)
        return sprite