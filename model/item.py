from abc import ABC, abstractmethod
import random
import pygame
from constants import TILE_SIZE


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
    """Objet commun : donne un boost de vitesse vers l'avant."""

    def __init__(self):
        super().__init__("Champignon", Rarity.COMMUN)

    def use(self, user_car, model) -> None:
        user_car.boost_timer = 2.0
        user_car.velocity += user_car.forward() * 4.0


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
    """Objet épique : rend la voiture invulnérable pendant 10 secondes."""

    def __init__(self):
        super().__init__("Étoile", Rarity.EPIQUE)

    def use(self, user_car, model) -> None:
        user_car.invulnerable_timer = 10.0


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
                if getattr(car, "invulnerable_timer", 0.0) <= 0:
                    car.slow_timer = 2.0
                    car.velocity *= 0.4
                self.active = False
                break

    def draw(self, screen: pygame.Surface) -> None:
        pos = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(screen, (255, 225, 40), pos, 10)
        pygame.draw.circle(screen, (130, 95, 0), pos, 10, 2)


class BombHazard(TrackHazard):
    """Bombe à retardement qui stoppe toutes les voitures proches à l'explosion."""

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
                    if getattr(car, "invulnerable_timer", 0.0) <= 0:
                        car.velocity *= 0
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