import pygame


MAPPING = {
    pygame.K_UP: "accelerate",
    pygame.K_DOWN: "brake",
    pygame.K_LEFT: "left",
    pygame.K_RIGHT: "right",
}


class InputHandler:
    """Lit l'etat du clavier et le traduit en actions de jeu."""

    def __init__(self):
        self.mapping = MAPPING

    def get_inputs(self) -> dict:
        """Renvoie un dictionnaire action -> touche enfoncee ou non."""
        keys = pygame.key.get_pressed()
        p = {action: False for action in self.mapping.values()}

        for key, action in self.mapping.items():
            if keys[key]:
                p[action] = True

        return p