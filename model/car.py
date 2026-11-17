import math
import pygame
from model.terrain_tempo import ROAD 
from constants import (
    CAR_ACCELERATION, CAR_TURN_RATE, CAR_AIR_DRAG,
    CAR_WIDTH, CAR_HEIGHT, TILE_SIZE
)


class Car:
    """Voiture pilotée par un joueur.

    La position et la vitesse sont des vecteurs en pixels, vitesse en pixels
    par image. L'angle est en degrés, en convention trigonométrique 0 = vers la droite, 90 = vers le haut de l'écran.
    """

    def __init__(self, start_col: int, start_row: int,
                 color: tuple[int, int, int] = (255, 0, 0)):
        self.position = pygame.Vector2(start_col * TILE_SIZE + TILE_SIZE / 2,start_row * TILE_SIZE + TILE_SIZE / 2)
        self.velocity = pygame.Vector2(0, 0)
        self.angle = 270.0
        self.throttle = 0    
        self.steering = 0   
        self.terrain = ROAD
        self.drifting = False
        self.color = color
        self.effects = []
        self.acceleration_factor = 1.0
        self.invincible = False
        self.sprite = self.build_sprite()

    def accelerate(self) -> None:
        """Demande une acceleration pour la prochaine mise a jour."""
        self.throttle = 1

    def brake(self) -> None:
        """Demande un freinage ou une marche arriere si la voiture est arretee."""
        self.throttle = -1

    def turn_left(self) -> None:
        """Augmente l'angle de braquage sens trigonométrique."""
        self.steering = 1

    def turn_right(self) -> None:
        """Diminue l'angle de braquage."""
        self.steering = -1

    def add_effect(self, effect) -> None:
        """Ajoute un effet à la voiture, sauf s'il est negatif et qu'elle est invincible."""
        if effect.harmful and self.invincible:
            return
        effect.on_start(self)
        self.effects.append(effect)

    def update_effects(self) -> None:
        """Applique les effets actifs pour cette image et retire ceux qui sont finis."""
        self.acceleration_factor = 1.0
        self.invincible = False
        for effect in self.effects:
            effect.apply(self)
            effect.tick()
        self.effects = [e for e in self.effects if not e.is_finished()]

    def forward(self) -> pygame.Vector2:
        """Vecteur unitaire dans la direction où pointe la voiture.
        Le signe moins vient de l'axe y de l'écran, qui va vers le bas.
        """
        rad = math.radians(self.angle)
        return pygame.Vector2(math.cos(rad), -math.sin(rad))
    
    def update_position(self) -> None:
        """Met a jour l'orientation, la vitesse et la position pour une image.
        La vitesse est décomposee en une partie longitudinale, dans l'axe de
        la voiture et une partie latérale. La partie laterale
        décide si la voiture adhere ou derape, selon le terrain.
        """
        self.update_effects()
        speed = self.velocity.dot(self.forward())
        self.angle += self.steering * CAR_TURN_RATE * speed
        front = self.forward()
        side = pygame.Vector2(-front.y, front.x)
        v_long = self.velocity.dot(front)
        v_lat = self.velocity.dot(side)
        v_long += (self.throttle * CAR_ACCELERATION * self.terrain.traction * self.acceleration_factor)
        self.drifting = abs(v_lat) > self.terrain.drift_threshold
        if self.drifting:
            v_lat *= 1 - self.terrain.drift_friction
        else:
            v_lat = 0
        self.velocity = front * v_long + side * v_lat
        self.velocity *= 1 - CAR_AIR_DRAG
        self.position += self.velocity
        self.throttle = 0
        self.steering = 0

    def build_sprite(self) -> pygame.Surface:
        """Dessine la voiture pointee vers la droite (angle 0)."""
        surf = pygame.Surface((CAR_HEIGHT, CAR_WIDTH), pygame.SRCALPHA)
        pygame.draw.rect(surf, self.color, surf.get_rect(), border_radius=5)
        pygame.draw.rect(surf, (255, 255, 255),
                         (CAR_HEIGHT - 10, 5, 6, CAR_WIDTH - 10))
        return surf

    def get_rotated_sprite(self) -> tuple[pygame.Surface, pygame.Rect]:
        """Renvoie l'image tournée selon l'angle et son rectangle centré."""
        rotated = pygame.transform.rotate(self.sprite, self.angle)
        rect = rotated.get_rect(center=(int(self.position.x), int(self.position.y)))
        return rotated, rect