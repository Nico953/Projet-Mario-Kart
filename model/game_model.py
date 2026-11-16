from constants import GameState
from model.car import Car
from model.circuit import Circuit
from model.circuit_maps import build_circuit, CIRCUIT_1


class GameModel:

    def __init__(self):
        self.state: str = GameState.MENU
        self.circuit: Circuit | None = None
        self.cars: list[Car] = []

    def load_circuit(self) -> None:
        self.circuit = build_circuit(CIRCUIT_1)
        self.spawn_car()

    def spawn_car(self) -> None:
        col1, row1 = self.circuit.starts["1"]
        col2, row2 = self.circuit.starts["2"]
        self.cars = [Car(col1, row1, (220, 40, 40)), Car(col2, row2, (40, 90, 220))]

    def update(self) -> None:
        if self.state != GameState.RACING or self.circuit is None:
            return
        for car in self.cars:
            tile = self.circuit.get_tile_at_pixel(car.position.x, car.position.y)
            if tile is not None:
                car.terrain = tile.terrain
            car.update_position()