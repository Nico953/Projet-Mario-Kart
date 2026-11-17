from abc import ABC, abstractmethod
from constants import FPS


class CarEffect(ABC):
    """Effet appliqué à une voiture pendant une durée donnée.

    À chaque image, la voiture appelle apply() sur chacun de ses effets,
    puis tick() pour faire avancer le temps. Un effet sans durée (None)
    reste actif jusqu'à ce que la voiture le retire.
    """
    harmful = False
    def __init__(self, seconds: float | None):
        self.remaining = None if seconds is None else int(seconds * FPS)

    def on_start(self, car) -> None:
        """Action ponctuelle au moment où l'effet commence (rien par défaut)."""

    @abstractmethod
    def apply(self, car) -> None:
        """Modifie les capacités de la voiture pour l'image en cours."""

    def tick(self) -> None:
        """Décompte une image de la durée restante."""
        if self.remaining is not None:
            self.remaining -= 1

    def is_finished(self) -> bool:
        """Indique si l'effet est termine et doit etre retiré."""
        return self.remaining is not None and self.remaining <= 0


class BoostEffect(CarEffect):
    """Multiplie l'acceleration de la voiture, ce qui augmente aussi sa vitesse max."""

    def __init__(self, seconds: float = 1.5, factor: float = 2.0):
        super().__init__(seconds)
        self.factor = factor

    def apply(self, car) -> None:
        car.acceleration_factor *= self.factor



class SlowEffect(CarEffect):
    """Fait perdre de la vitesse d'un coup, puis reduit l'acceleration (banane)."""

    harmful = True

    def __init__(self, seconds: float = 1.5, speed_kept: float = 0.4):
        super().__init__(seconds)
        self.speed_kept = speed_kept

    def on_start(self, car) -> None:
        car.velocity *= self.speed_kept

    def apply(self, car) -> None:
        car.acceleration_factor *= 0.5


class StunEffect(CarEffect):
    """Arrete la voiture et l'empeche d'avancer (bombe, carapace bleue)."""
    harmful = True
    def __init__(self, seconds: float = 1.0):
        super().__init__(seconds)

    def apply(self, car) -> None:
        car.velocity *= 0
        car.acceleration_factor = 0


class InvincibilityEffect(CarEffect):
    """Rend la voiture insensible aux effets négatifs (étoile)."""
    def __init__(self, seconds: float = 10.0):
        super().__init__(seconds)

    def apply(self, car) -> None:
        car.invincible = True