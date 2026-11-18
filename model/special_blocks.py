from abc import ABC, abstractmethod
import pygame
from constants import TILE_SIZE
from model.effects import CarEffect


def _apply_effect(car, effect: CarEffect) -> None:
    """Ajoute un effet permanent (seconds=None) à la voiture."""
    if getattr(car, "invincible", False) and getattr(effect, "harmful", False):
        return
    if hasattr(car, "add_effect"):
        car.add_effect(effect)
    else:
        effect.on_start(car)
        if not hasattr(car, "effects"):
            car.effects = []
        # Évite d'empiler deux fois le même blocage
        if not any(isinstance(e, type(effect)) for e in car.effects):
            car.effects.append(effect)


def clear_special_effects(car) -> None:
    """Annule les effets des blocs spéciaux (appelé par ResetBlock ou un checkpoint)."""
    car.steering_locked = False
    car.brakes_locked = False
    car.engine_cut = False
    if hasattr(car, "effects"):
        car.effects = [
            e for e in car.effects
            if not isinstance(e, (SteeringLockedEffect, BrakesLockedEffect, EngineCutEffect))
        ]


# --- Effets permanents (jusqu'à checkpoint ou bloc de réinitialisation) ---

class SteeringLockedEffect(CarEffect):
    """Bloque la direction : impossible de tourner."""
    harmful = True

    def __init__(self):
        super().__init__(seconds=None)

    def apply(self, car) -> None:
        car.steering_locked = True
        car.steering = 0


class BrakesLockedEffect(CarEffect):
    """Bloque les freins : impossible de freiner ou reculer."""
    harmful = True

    def __init__(self):
        super().__init__(seconds=None)

    def apply(self, car) -> None:
        car.brakes_locked = True
        if car.throttle < 0:
            car.throttle = 0


class EngineCutEffect(CarEffect):
    """Coupe le moteur : impossible d'accélérer."""
    harmful = True

    def __init__(self):
        super().__init__(seconds=None)

    def apply(self, car) -> None:
        car.engine_cut = True
        if car.throttle > 0:
            car.throttle = 0


# --- Blocs au sol sur le circuit ---

class SpecialBlock(ABC):
    """Classe mère abstraite pour les blocs à effet spécial posés sur la piste."""

    def __init__(self, col: int, row: int, color: tuple[int, int, int], symbol: str):
        self.col = col
        self.row = row
        self.position = pygame.Vector2(
            col * TILE_SIZE + TILE_SIZE / 2,
            row * TILE_SIZE + TILE_SIZE / 2,
        )
        self.color = color
        self.symbol = symbol
        self.radius = TILE_SIZE * 0.45

    def update(self, cars: list) -> None:
        """Vérifie si une voiture roule sur le bloc et déclenche son effet."""
        for car in cars:
            if car.position.distance_to(self.position) <= self.radius:
                self.on_trigger(car)

    @abstractmethod
    def on_trigger(self, car) -> None:
        """Action déclenchée lorsqu'une voiture passe sur le bloc."""

    def draw(self, screen: pygame.Surface) -> None:
        """Dessine le bloc spécial sur la piste."""
        rect = pygame.Rect(0, 0, TILE_SIZE - 8, TILE_SIZE - 8)
        rect.center = (int(self.position.x), int(self.position.y))
        pygame.draw.rect(screen, self.color, rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=8)

        font = pygame.font.SysFont("Arial", 16, bold=True)
        txt = font.render(self.symbol, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=rect.center))


class SteeringLockBlock(SpecialBlock):
    """Bloc orange : bloque la direction jusqu'au prochain checkpoint ou ResetBlock."""

    def __init__(self, col: int, row: int):
        super().__init__(col, row, color=(230, 120, 20), symbol="DIR X")

    def on_trigger(self, car) -> None:
        _apply_effect(car, SteeringLockedEffect())


class BrakeLockBlock(SpecialBlock):
    """Bloc violet : bloque les freins jusqu'au prochain checkpoint ou ResetBlock."""

    def __init__(self, col: int, row: int):
        super().__init__(col, row, color=(150, 50, 200), symbol="FRN X")

    def on_trigger(self, car) -> None:
        _apply_effect(car, BrakesLockedEffect())


class EngineCutBlock(SpecialBlock):
    """Bloc rouge foncé : coupe le moteur jusqu'au prochain checkpoint ou ResetBlock."""

    def __init__(self, col: int, row: int):
        super().__init__(col, row, color=(180, 30, 45), symbol="MOT X")

    def on_trigger(self, car) -> None:
        _apply_effect(car, EngineCutEffect())


class ResetBlock(SpecialBlock):
    """Bloc vert : annule tous les blocages subis par la voiture."""

    def __init__(self, col: int, row: int):
        super().__init__(col, row, color=(40, 185, 95), symbol="RESET")

    def on_trigger(self, car) -> None:
        clear_special_effects(car)