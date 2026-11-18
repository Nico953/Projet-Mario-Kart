from abc import ABC, abstractmethod
import random
import pygame
from constants import TILE_SIZE
from model.effects import BoostEffect, SlowEffect, StunEffect, InvincibilityEffect


def _apply_car_effect(car, effect) -> None:
    """Applique un effet de model/effects.py sur la voiture."""
    if hasattr(car, "add_effect"):
        car.add_effect(effect)
    else:
        effect.on_start(car)
        if not hasattr(car, "effects"):
            car.effects = []
        car.effects.append(effect)


class Rarity:
    """Niveaux de rareté des objets, poids de tirage et couleurs pour l'interface."""
    COMMUN = "Commun"
    RARE = "Rare"
    EPIQUE = "Épique"
    LEGENDAIRE = "Légendaire"

    WEIGHTS = {
        COMMUN: 50,
        RARE: 25,
        EPIQUE: 15,
        LEGENDAIRE: 10,
    }

    COLORS = {
        COMMUN: (185, 185, 195),
        RARE: (65, 155, 255),
        EPIQUE: (185, 75, 245),
        LEGENDAIRE: (255, 195, 0),
    }


class Item(ABC):
    """Classe mère abstraite représentant un objet récupérable par un joueur."""

    def __init__(self, name: str, rarity: str):
        self.name = name
        self.rarity = rarity
        self.color = Rarity.COLORS[rarity]

    @abstractmethod
    def use(self, user_car, model) -> None:
        """Déclenche l'effet de l'objet lors de son activation par le joueur."""
        pass


class MushroomItem(Item):
    """Objet commun : applique un boost d'accélération temporaire."""

    def __init__(self):
        super().__init__("Champignon", Rarity.COMMUN)

    def use(self, user_car, model) -> None:
        _apply_car_effect(user_car, BoostEffect(seconds=1.5, factor=2.0))


class BananaItem(Item):
    """Objet commun : dépose une banane derrière la voiture."""

    def __init__(self):
        super().__init__("Banane", Rarity.COMMUN)

    def use(self, user_car, model) -> None:
        drop_pos = user_car.position - user_car.forward() * (TILE_SIZE * 0.7)
        model.hazards.append(BananaHazard(drop_pos.x, drop_pos.y))


class BombItem(Item):
    """Objet rare : pose une bombe à retardement sur la piste."""

    def __init__(self):
        super().__init__("Bombe", Rarity.RARE)

    def use(self, user_car, model) -> None:
        drop_pos = user_car.position - user_car.forward() * (TILE_SIZE * 0.8)
        model.hazards.append(BombHazard(drop_pos.x, drop_pos.y, fuse_time=2.0))


class StarItem(Item):
    """Objet épique : rend la voiture insensible aux effets négatifs."""

    def __init__(self):
        super().__init__("Étoile", Rarity.EPIQUE)

    def use(self, user_car, model) -> None:
        _apply_car_effect(user_car, InvincibilityEffect(seconds=10.0))


class BlueShellItem(Item):
    """Objet légendaire : fait tomber une bombe directement sur l'adversaire."""

    def __init__(self):
        super().__init__("Carapace bleue", Rarity.LEGENDAIRE)

    def use(self, user_car, model) -> None:
        for car in model.cars:
            if car is not user_car:
                model.hazards.append(BombHazard(car.position.x, car.position.y, fuse_time=0.5))


class TrackHazard(ABC):
    """Classe mère abstraite pour les pièges actifs posés sur le circuit."""

    def __init__(self, x: float, y: float, radius: float):
        self.position = pygame.Vector2(x, y)
        self.radius = radius
        self.active = True

    @abstractmethod
    def update(self, dt: float, cars: list) -> None:
        """Met à jour le piège et vérifie les collisions avec les voitures."""
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Dessine le piège sur l'écran."""
        pass


class BananaHazard(TrackHazard):
    """Banane sur la piste qui ralentit la prochaine voiture qui passe dessus."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, radius=16.0)

    def update(self, dt: float, cars: list) -> None:
        if not self.active:
            return
        for car in cars:
            if car.position.distance_to(self.position) <= self.radius + 15:
                if not getattr(car, "invincible", False):
                    _apply_car_effect(car, SlowEffect(seconds=1.5, speed_kept=0.4))
                self.active = False
                break

    def draw(self, screen: pygame.Surface) -> None:
        pos = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(screen, (255, 225, 40), pos, 10)
        pygame.draw.circle(screen, (130, 95, 0), pos, 10, 2)


class BombHazard(TrackHazard):
    """Bombe à retardement qui immobilise les voitures proches à l'explosion."""

    def __init__(self, x: float, y: float, fuse_time: float = 2.0):
        super().__init__(x, y, radius=TILE_SIZE * 1.4)
        self.timer = fuse_time
        self.exploded_timer = 0.0

    def update(self, dt: float, cars: list) -> None:
        if not self.active:
            return

        if self.exploded_timer > 0:
            self.exploded_timer -= dt
            if self.exploded_timer <= 0:
                self.active = False
            return

        self.timer -= dt
        if self.timer <= 0:
            for car in cars:
                if car.position.distance_to(self.position) <= self.radius:
                    if not getattr(car, "invincible", False):
                        _apply_car_effect(car, StunEffect(seconds=1.0))
            self.exploded_timer = 0.25

    def draw(self, screen: pygame.Surface) -> None:
        pos = (int(self.position.x), int(self.position.y))
        if self.exploded_timer > 0:
            pygame.draw.circle(screen, (255, 110, 30), pos, int(self.radius), 4)
            pygame.draw.circle(screen, (255, 220, 80), pos, int(self.radius * 0.6))
            return

        pygame.draw.circle(screen, (30, 30, 35), pos, 13)
        spark_color = (255, 60, 60) if int(self.timer * 8) % 2 == 0 else (255, 190, 0)
        pygame.draw.circle(screen, spark_color, (pos[0] + 6, pos[1] - 8), 5)


class ItemBox:
    """Bloc à objet spécial (?) posé sur le circuit avec temps de réapparition."""

    def __init__(self, x: float, y: float, respawn_delay: float = 4.0):
        self.position = pygame.Vector2(x, y)
        self.size = 30
        self.respawn_delay = respawn_delay
        self.cooldown = 0.0

    @property
    def is_available(self) -> bool:
        return self.cooldown <= 0

    def update(self, dt: float, cars: list) -> None:
        """Gère la réapparition du bloc et la récupération d'objet par une voiture."""
        if self.cooldown > 0:
            self.cooldown = max(0.0, self.cooldown - dt)
            return

        for car in cars:
            if car.position.distance_to(self.position) <= self.size:
                if getattr(car, "held_item", None) is None:
                    car.held_item = create_random_item()
                    self.cooldown = self.respawn_delay
                    break

    def draw(self, screen: pygame.Surface) -> None:
        """Dessine le bloc mystère actif ou son emplacement en recharge."""
        rect = pygame.Rect(0, 0, self.size, self.size)
        rect.center = (int(self.position.x), int(self.position.y))

        if not self.is_available:
            pygame.draw.rect(screen, (120, 120, 140), rect, 2, border_radius=6)
            return

        pygame.draw.rect(screen, (255, 195, 0), rect, border_radius=6)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=6)
        font = pygame.font.SysFont("Arial", 20, bold=True)
        label = font.render("?", True, (30, 30, 50))
        screen.blit(label, label.get_rect(center=rect.center))


def create_random_item() -> Item:
    """Tire un objet aléatoire selon les probabilités de chaque rareté."""
    candidates = [
        (MushroomItem, Rarity.WEIGHTS[Rarity.COMMUN] // 2),
        (BananaItem, Rarity.WEIGHTS[Rarity.COMMUN] // 2),
        (BombItem, Rarity.WEIGHTS[Rarity.RARE]),
        (StarItem, Rarity.WEIGHTS[Rarity.EPIQUE]),
        (BlueShellItem, Rarity.WEIGHTS[Rarity.LEGENDAIRE]),
    ]
    classes, weights = zip(*candidates)
    chosen_cls = random.choices(classes, weights=weights, k=1)[0]
    return chosen_cls()


def create_item_boxes(grid_coords: list[tuple[int, int]]) -> list[ItemBox]:
    """Crée une liste de blocs à objets centrés sur les cases (col, row) données."""
    return [
        ItemBox(col * TILE_SIZE + TILE_SIZE / 2, row * TILE_SIZE + TILE_SIZE / 2)
        for col, row in grid_coords
    ]