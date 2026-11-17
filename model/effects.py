from abc import ABC, abstractmethod
from constants import FPS


class CarEffect(ABC):
    """Effet appliqué à une voiture pendant une durée donnée.

    À chaque image, la voiture appelle apply() sur chacun de ses effets,
    puis tick() pour faire avancer le temps. Un effet sans durée (None)
    reste actif jusqu'à ce que la voiture le retire.
    """

    def __init__(self, seconds: float | None):
        self.remaining = None if seconds is None else int(seconds * FPS)

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