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
        if self.color == (150, 50, 40):
            sprite = pygame.Surface((tile_size, tile_size))
            sprite.fill((90, 90, 90))
            brick_h = tile_size // 4
            brick_w = tile_size // 2
            for r in range(4):
                offset = (brick_w // 2) if r % 2 else 0
                for c in range(-1, 3):
                    x = c * brick_w + offset
                    pygame.draw.rect(sprite, (150, 50, 40),
                                     (x + 1, r * brick_h + 1, brick_w - 2, brick_h - 2))
            return sprite

        sprite = pygame.Surface((tile_size, tile_size))
        sprite.fill(self.color)
        return sprite

