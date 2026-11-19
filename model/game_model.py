from constants import GameState, TILE_SIZE, CAR_MODELS, COLOR_P1, COLOR_P2, FPS
from model.car import Car
from model.circuit import Circuit
from model.circuit_maps import build_circuit, CIRCUIT_1
from model.effects import BoostEffect
from model.item import create_item_boxes



class GameModel:

    def __init__(self):
        self.state: str = GameState.MENU
        self.circuit: Circuit | None = None
        self.cars: list[Car] = []
        # Index des modèles de voitures sélectionnés dans le menu pour J1 et J2
        self.selected_models = [0, 1]
        
        self.laps_to_win = 3

    def load_circuit(self) -> None:
        self.circuit = build_circuit(CIRCUIT_1)
        self.spawn_car()
        self.item_boxes = create_item_boxes(list(self.circuit.item_boxes))

    def spawn_car(self) -> None:
        col1, row1 = self.circuit.starts["1"]
        col2, row2 = self.circuit.starts["2"]
        # Création des deux voitures avec le modèle personnalisé choisi par chaque joueur
        spec1 = CAR_MODELS[self.selected_models[0]]
        spec2 = CAR_MODELS[self.selected_models[1]]
        self.cars = [Car(col1, row1, COLOR_P1, spec1), Car(col2, row2, COLOR_P2, spec2)]
        self.laps = [0 for car in self.cars]
        self.passed = [set() for car in self.cars]
        self.winner = None
        self.last_checkpoint = [self.circuit.starts["1"], self.circuit.starts["2"]]
        self.on_boost = [False for car in self.cars]
        from model.effects import SlowEffect, StunEffect, InvincibilityEffect

    def update(self) -> None:
        if self.state != GameState.RACING or self.circuit is None:
            return
        for box in self.item_boxes:
            box.update(1 / FPS, self.cars)
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
                if pos in self.circuit.boosts:
                    if not self.on_boost[i]:
                        car.add_effect(BoostEffect())
                        self.on_boost[i] = True
                else:
                    self.on_boost[i] = False
            car.update_position()
            tile = self.circuit.get_tile_at_pixel(car.position.x, car.position.y)
            if tile is None or (tile.col, tile.row) in self.circuit.voids:
                col, row = self.last_checkpoint[i]
                car.position.x = col * TILE_SIZE + TILE_SIZE / 2
                car.position.y = row * TILE_SIZE + TILE_SIZE / 2
                car.velocity *= 0