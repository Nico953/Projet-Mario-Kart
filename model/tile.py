import random
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
        self.sprite = None

    def get_sprite(self, tile_size=TILE_SIZE):
        if self.sprite is None:
            self.sprite = self.build_sprite(tile_size)
        return self.sprite
    
    def build_sprite(self, tile_size):

        # Route, herbe, terre : images du pack
        if self.color == (80, 80, 90) or self.color == (50, 140, 60) or self.color == (155, 118, 83):
            return load_image(TERRAIN_IMAGES[self.terrain])
        
        # Mur : briques
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
        
        # Vide : trou avec dégradé
        if self.color == (10, 10, 10):
            sprite = pygame.Surface((tile_size, tile_size))
            for i in range(tile_size // 2):
                shade = max(0, 60 - i * 4)
                pygame.draw.rect(sprite, (shade, shade, shade + 10),
                                 (i, i, tile_size - 2 * i, tile_size - 2 * i))
            return sprite
        
        # Ligne d'arrivée : damier
        if self.color == (240, 240, 240):
            sprite = pygame.Surface((tile_size, tile_size))
            n = 8
            size = tile_size // n
            for r in range(n):
                for c in range(n):
                    color = (240, 240, 240) if (r + c) % 2 == 0 else (20, 20, 20)
                    pygame.draw.rect(sprite, color, (c * size, r * size, size, size))
            return sprite
        
        # Boost : rectangles roses de plus en plus foncés vers le centre
        if self.color == (255, 60, 200):
            sprite = pygame.Surface((tile_size, tile_size))
            for i in range(0, tile_size // 2, 4):
                pink = (255 - i * 3, 90 - i, 200 - i * 2)
                pygame.draw.rect(sprite, pink, (i, i, tile_size - 2 * i, tile_size - 2 * i))
            return sprite

        # Glace : lisse avec petites fissures
        if self.color == (120, 190, 240):
            sprite = pygame.Surface((tile_size, tile_size))
            sprite.fill((200, 230, 245))
            rng = random.Random(self.col * 100 + self.row)
            for _ in range(4):
                x = rng.randint(5, tile_size - 5)
                y = rng.randint(5, tile_size - 5)
                end = (x + rng.randint(-10, 10), y + rng.randint(-10, 10))
                pygame.draw.line(sprite, (255, 255, 255), (x, y), end, 1)
            return sprite

        # Checkpoint : cercle jaune 
        if self.color == (230, 200, 60):
            sprite = load_image("road.png").copy()
            center = (tile_size // 2, tile_size // 2)
            pygame.draw.circle(sprite, (255, 200, 0), center, tile_size // 2 - 4)
            return sprite

        # Autres cases : couleur simple
        sprite = pygame.Surface((tile_size, tile_size))
        sprite.fill(self.color)
        return sprite