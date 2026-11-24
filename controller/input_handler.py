import pygame


PLAYER_1_KEYS = {
    "accelerate": [pygame.K_z],
    "brake": [pygame.K_s],
    "left": [pygame.K_q,],
    "right": [pygame.K_d],
    "use_item": [pygame.K_e],
}

PLAYER_2_KEYS = {
    "accelerate": [pygame.K_UP],
    "brake": [pygame.K_DOWN],
    "left": [pygame.K_LEFT],
    "right": [pygame.K_RIGHT],
    "use_item": [pygame.K_RSHIFT],
}

class InputHandler:
    """Lit l'etat du clavier et le traduit en actions de jeu."""

    def __init__(self):
        self.players_keys = [PLAYER_1_KEYS, PLAYER_2_KEYS]

    def get_inputs(self) -> list[dict]:
        """Renvoie, pour chaque joueur, un dictionnaire action = touche enfoncee."""
        keys = pygame.key.get_pressed()
        inputs = []
        for mapping in self.players_keys:
            actions = {}
            for action, action_keys in mapping.items():
                actions[action] = any(keys[k] for k in action_keys)
            inputs.append(actions)
        return inputs