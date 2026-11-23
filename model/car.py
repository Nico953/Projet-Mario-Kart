import math
import pygame
from model.terrain_tempo import ROAD 
from constants import (
    CAR_ACCELERATION, CAR_TURN_RATE, CAR_AIR_DRAG,
    CAR_WIDTH, CAR_HEIGHT, TILE_SIZE
)


def build_car_surface(color: tuple[int, int, int], design: str = "sport") -> pygame.Surface:
    """Dessine la voiture pointée vers la droite selon le design choisi dans le menu."""
    surf = pygame.Surface((CAR_HEIGHT, CAR_WIDTH), pygame.SRCALPHA)
    w, h = CAR_HEIGHT, CAR_WIDTH
    dark = tuple(max(0, c - 70) for c in color)
    light = tuple(min(255, c + 65) for c in color)
    wheel = (25, 25, 30)
    cockpit = (35, 45, 65)

    # Dessine les 4 roues communes à tous les modèles
    for wx, wy in [(6, 0), (w - 16, 0), (6, h - 4), (w - 16, h - 4)]:
        pygame.draw.rect(surf, wheel, (wx, wy, 10, 4), border_radius=2)

    if design == "formula":
        # Formule 1 : aileron arrière, nez pointu et aileron avant
        pygame.draw.rect(surf, dark, (1, 3, 5, h - 6), border_radius=1)
        pygame.draw.polygon(surf, color, [
            (6, 6), (w - 14, 8), (w - 2, h // 2), (w - 14, h - 8), (6, h - 6)
        ])
        pygame.draw.rect(surf, light, (w - 6, 3, 5, h - 6), border_radius=1)
        pygame.draw.ellipse(surf, cockpit, (18, 9, 12, h - 18))
    elif design == "muscle":
        # Dragster : carrosserie massive avec double bande blanche
        pygame.draw.rect(surf, color, (2, 2, w - 4, h - 4), border_radius=3)
        pygame.draw.rect(surf, (245, 245, 245), (4, h // 2 - 4, w - 10, 3))
        pygame.draw.rect(surf, (245, 245, 245), (4, h // 2 + 1, w - 10, 3))
        pygame.draw.rect(surf, cockpit, (16, 6, 11, h - 12), border_radius=2)
        pygame.draw.rect(surf, dark, (w - 12, 7, 7, h - 14), border_radius=1)
    elif design == "compact":
        # Agile : châssis plus court et arrondi
        pygame.draw.rect(surf, color, (6, 3, w - 10, h - 6), border_radius=9)
        pygame.draw.rect(surf, light, (12, 6, w - 22, h - 12), border_radius=6)
        pygame.draw.ellipse(surf, cockpit, (20, 6, 13, h - 12))
    else:
        # Équilibrée ("sport") : carrosserie profilée avec pare-brise et phares
        pygame.draw.rect(surf, color, (3, 3, w - 6, h - 6), border_radius=6)
        pygame.draw.rect(surf, dark, (3, 4, 4, h - 8), border_radius=2)
        pygame.draw.polygon(surf, cockpit, [
            (24, 6), (34, 8), (34, h - 8), (24, h - 6)
        ])
        pygame.draw.rect(surf, (255, 245, 190), (w - 6, 5, 3, 5))
        pygame.draw.rect(surf, (255, 245, 190), (w - 6, h - 10, 3, 5))

    return surf


class Car:
    """Voiture pilotée par un joueur.

    La position et la vitesse sont des vecteurs en pixels, vitesse en pixels
    par image. L'angle est en degrés, en convention trigonométrique 0 = vers la droite, 90 = vers le haut de l'écran.
    """

    def __init__(self, start_col: int, start_row: int,
                 color: tuple[int, int, int] = (255, 0, 0),
                 model_spec: dict | None = None):
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
        # Caractéristiques et design du modèle choisi dans le menu
        spec = model_spec or {}
        self.model_name = spec.get("name", "Équilibrée")
        self.model_acceleration = spec.get("acceleration", 1.0)
        self.model_handling = spec.get("handling", 1.0)
        self.model_aerodynamics = spec.get("aerodynamics", 1.0)
        self.design = spec.get("design", "sport")
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
        # Prise en compte de la maniabilité du modèle choisi
        self.angle += self.steering * CAR_TURN_RATE * self.model_handling * speed
        front = self.forward()
        side = pygame.Vector2(-front.y, front.x)
        v_long = self.velocity.dot(front)
        v_lat = self.velocity.dot(side)
        # Prise en compte de l'accélération du modèle choisi
        v_long += (self.throttle * CAR_ACCELERATION * self.model_acceleration * self.terrain.traction * self.acceleration_factor)
        self.drifting = abs(v_lat) > self.terrain.drift_threshold
        if self.drifting:
            v_lat *= 1 - self.terrain.drift_friction
        else:
            v_lat = 0
        self.velocity = front * v_long + side * v_lat
        # Réduction des frottements de l'air selon l'aérodynamisme du modèle
        self.velocity *= 1 - (CAR_AIR_DRAG / self.model_aerodynamics)
        self.position += self.velocity
        self.throttle = 0
        self.steering = 0

    def hits_wall(self, pos: pygame.Vector2, walls: set) -> bool:
        """Indique si la voiture placée en pos toucherait une case mur.
        On teste les 4 coins d'un carré centré sur la voiture.
        """
        r = CAR_WIDTH / 2
        for dx in (-r, r):
            for dy in (-r, r):
                cell = (int((pos.x + dx) // TILE_SIZE), int((pos.y + dy) // TILE_SIZE))
                if cell in walls:
                    return True
        return False
    
    def build_sprite(self) -> pygame.Surface:
        """Dessine la voiture pointee vers la droite (angle 0)."""
        return build_car_surface(self.color, self.design)

    def get_rotated_sprite(self) -> tuple[pygame.Surface, pygame.Rect]:
        """Renvoie l'image tournée selon l'angle et son rectangle centré."""
        rotated = pygame.transform.rotate(self.sprite, self.angle)
        rect = rotated.get_rect(center=(int(self.position.x), int(self.position.y)))
        return rotated, rect