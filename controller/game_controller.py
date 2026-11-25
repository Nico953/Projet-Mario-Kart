import pygame
import sys
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    GameState, CAR_MODELS
)
from model.circuit_maps import CIRCUITS
from model.game_model import GameModel
from view.game_view import GameView
from controller.input_handler import InputHandler, PLAYER_1_KEYS, PLAYER_2_KEYS
import math

class GameController:

    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.model = GameModel()
        self.view = GameView(self.screen)
        self.input_handler = InputHandler()
        self.running = True
        self.load_sounds()
        self.last_step = None
    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)

    def handle_keydown(self, key: int) -> None:

        state = self.model.state

        if state == GameState.MENU:
            self.handle_menu_key(key)
        elif state == GameState.RACING:
            self.handle_racing_key(key)

    def handle_menu_key(self, key: int) -> None:
        """Gère le changement de modèle de voiture, de circuit et le lancement de la course."""
        nb_models = len(CAR_MODELS)
        nb_circuits = len(CIRCUITS)
        # Joueur 1 : sélection du modèle avec Q et D
        if key == pygame.K_q:
            self.model.selected_models[0] = (self.model.selected_models[0] - 1) % nb_models
        elif key == pygame.K_d:
            self.model.selected_models[0] = (self.model.selected_models[0] + 1) % nb_models
        # Joueur 2 : sélection du modèle avec les flèches gauche et droite
        elif key == pygame.K_LEFT:
            self.model.selected_models[1] = (self.model.selected_models[1] - 1) % nb_models
        elif key == pygame.K_RIGHT:
            self.model.selected_models[1] = (self.model.selected_models[1] + 1) % nb_models
        # Sélection du circuit avec Z/S ou Haut/Bas
        elif key in (pygame.K_z, pygame.K_UP):
            self.model.selected_circuit = (self.model.selected_circuit - 1) % nb_circuits
        elif key in (pygame.K_s, pygame.K_DOWN):
            self.model.selected_circuit = (self.model.selected_circuit + 1) % nb_circuits
        elif key == pygame.K_RETURN:
            self.start_race()
        elif key == pygame.K_ESCAPE:
            self.quit()

    def use_player_item(self, player_idx: int) -> None:
        """Active l'objet tenu par le joueur donné puis vide son emplacement."""
        if player_idx >= len(self.model.cars):
            return
        car = self.model.cars[player_idx]
        if getattr(car, "held_item", None) is not None:
            car.held_item.use(car, self.model)
            car.held_item = None

    def handle_racing_key(self, key: int) -> None:
        """Gère les actions ponctuelles en course (objets, retour menu, rejouer)."""
        if key in PLAYER_1_KEYS["use_item"]:
            self.use_player_item(0)
        elif key in PLAYER_2_KEYS["use_item"]:
            self.use_player_item(1)
        elif key == pygame.K_ESCAPE:
            self.model.state = GameState.MENU
        elif key == pygame.K_RETURN and self.model.winner is not None:
            self.start_race()

    def update(self) -> None:
        if self.model.state != GameState.RACING:
            return

        inputs = self.input_handler.get_inputs()
        for car, player_input in zip(self.model.cars, inputs):
            self.apply_input(car, player_input)
        self.model.update()
        self.play_sounds()

    def apply_input(self, car, player_input) -> None:
        if player_input['accelerate']:
            car.accelerate()
        if player_input['brake']:
            car.brake()
        if player_input['left']:
            car.turn_left()
        if player_input['right']:
            car.turn_right()

    def render(self) -> None:
        self.view.draw(self.model)

    def quit(self) -> None:
        self.running = False
        pygame.quit()
        sys.exit()
    def load_sounds(self) -> None:
        """Charge les voix du compte à rebours et les sons de boost et de victoire."""
        voice = "assets/sounds/voice/"
        self.countdown_sounds = {
            3: pygame.mixer.Sound(voice + "three.ogg"),
            2: pygame.mixer.Sound(voice + "two.ogg"),
            1: pygame.mixer.Sound(voice + "one.ogg"),
            0: pygame.mixer.Sound(voice + "go.ogg"),
        }
        self.sounds = {
            "boost": pygame.mixer.Sound("assets/sounds/boost.ogg"),
            "win": pygame.mixer.Sound(voice + "you_win.ogg"),
        }

    def start_race(self) -> None:
        """Charge le circuit choisi et relance le compte à rebours."""
        self.model.load_circuit(self.model.selected_circuit)
        self.model.state = GameState.RACING
        self.last_step = None

    def play_sounds(self) -> None:
        """Joue la voix du compte à rebours et les sons demandés par le modèle."""
        step = max(0, math.ceil(self.model.countdown))
        if step != self.last_step:
            self.countdown_sounds[step].play()
            self.last_step = step
        for name in self.model.sound_events:
            self.sounds[name].play()
        self.model.sound_events.clear()