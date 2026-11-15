from constants import GameState
from model.car import Car
from model.circuit import Circuit
from model.circuit_maps import build_circuit, CIRCUIT_1


class GameModel:

    def __init__(self):
        self.state: str = GameState.MENU
        self.circuit: Circuit | None = None
        self.car: Car | None = None

    def load_circuit(self) -> None:
        self.circuit = build_circuit(CIRCUIT_1)
        self.spawn_car()

    def spawn_car(self) -> None:
        self.car = Car(7, 1)

    def update(self) -> None:
        if self.state != GameState.RACING or self.circuit is None:
            return
        tile = self.circuit.get_tile_at_pixel(self.car.position.x, self.car.position.y)
        if tile is not None:
            self.car.terrain = tile.terrain
        self.car.update_position()
