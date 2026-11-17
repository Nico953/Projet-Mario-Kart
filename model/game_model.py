from constants import GameState, TILE_SIZE
from model.car import Car
from model.circuit import Circuit
from model.circuit_maps import build_circuit, CIRCUIT_1



class GameModel:

    def __init__(self):
        self.state: str = GameState.MENU
        self.circuit: Circuit | None = None
        self.cars: list[Car] = []
        
        self.laps_to_win = 3

    def load_circuit(self) -> None:
        self.circuit = build_circuit(CIRCUIT_1)
        self.spawn_car()

    def spawn_car(self) -> None:
        col1, row1 = self.circuit.starts["1"]
        col2, row2 = self.circuit.starts["2"]
        self.cars = [Car(col1, row1, (220, 40, 40)), Car(col2, row2, (40, 90, 220))]
        self.laps = [0 for car in self.cars]
        self.passed = [set() for car in self.cars]
        self.winner = None
        self.last_checkpoint = [self.circuit.starts["1"], self.circuit.starts["2"]]
        from model.effects import SlowEffect, StunEffect, InvincibilityEffect

    def update(self) -> None:
        if self.state != GameState.RACING or self.circuit is None:
            return
        for i, car in enumerate(self.cars):
            tile = self.circuit.get_tile_at_pixel(car.position.x, car.position.y)
            if tile is not None:
                car.terrain = tile.terrain
                pos = (tile.col, tile.row)
                for k, group in enumerate(self.circuit.checkpoints):
                    if pos in group:
                        self.passed[i].add(k)
                        self.last_checkpoint[i] = pos
                if pos in self.circuit.finish and len(self.passed[i]) == len(self.circuit.checkpoints):
                    self.laps[i] += 1
                    self.passed[i] = set()
                    print("Voiture", i + 1, "tour", self.laps[i])
                if self.laps[i] >= self.laps_to_win and self.winner is None:
                    self.winner = i + 1
                    print("Gagnant : voiture", self.winner)
            car.update_position()
            tile = self.circuit.get_tile_at_pixel(car.position.x, car.position.y)
            if tile is None or (tile.col, tile.row) in self.circuit.voids:
                col, row = self.last_checkpoint[i]
                car.position.x = col * TILE_SIZE + TILE_SIZE / 2
                car.position.y = row * TILE_SIZE + TILE_SIZE / 2
                car.velocity *= 0
                