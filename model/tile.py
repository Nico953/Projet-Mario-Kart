import pygame
from constants import TILE_SIZE
from model.terrain_tempo import ROAD, GRASS, DIRT

IMAGES = {}

def load_image(name):
    if name not in IMAGES:
        img = pygame.image.load("assets/tiles/" + name)
        IMAGES[name] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    return IMAGES[name]

TERRAIN_IMAGES = {ROAD: "road.png", GRASS: "grass.png", DIRT: "dirt.png"}


class Tile:

    def __init__(self, col, row, terrain, color):
        self.col = col
        self.row = row
        self.terrain = terrain
        self.color = color

    def get_sprite(self, tile_size=TILE_SIZE):
        if self.color == (80, 80, 90) or self.color == (50, 140, 60) or self.color == (155, 118, 83):
            return load_image(TERRAIN_IMAGES[self.terrain])
        sprite = pygame.Surface((tile_size, tile_size))
        sprite.fill(self.color)
        return sprite