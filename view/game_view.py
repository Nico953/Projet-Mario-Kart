import pygame
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE,
    COLOR_BG, COLOR_TEXT, COLOR_ACCENT, COLOR_PANEL, COLOR_PANEL_BORDER,
    COLOR_P1, COLOR_P2, CAR_MODELS, GameState
)
from model.car import build_car_surface
from model.game_model import GameModel


class GameView:

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 24)
        # Polices supplémentaires pour le titre et les barres de statistiques
        self.title_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 16)

    def draw(self, model: GameModel) -> None:
        self.screen.fill(COLOR_BG)
        if model.state == GameState.MENU:
            self._draw_menu(model)
        elif model.state == GameState.RACING:
            self._draw_racing(model)
        pygame.display.flip()

    def _draw_menu(self, model: GameModel) -> None:
        """Affiche le menu de personnalisation des voitures pour les deux joueurs."""
        cx = WINDOW_WIDTH // 2

        title_surf = self.title_font.render(
            "PERSONNALISATION DES VOITURES", True, COLOR_ACCENT)
        self.screen.blit(title_surf, title_surf.get_rect(center=(cx, 65)))

        players_info = [
            ("JOUEUR 1 (Q / D)", COLOR_P1, model.selected_models[0], cx - 230),
            ("JOUEUR 2 (← / →)", COLOR_P2, model.selected_models[1], cx + 230),
        ]

        for header, p_color, model_idx, card_cx in players_info:
            spec = CAR_MODELS[model_idx]
            card = pygame.Rect(0, 0, 380, 410)
            card.center = (card_cx, 330)
            pygame.draw.rect(self.screen, COLOR_PANEL, card, border_radius=12)
            pygame.draw.rect(self.screen, p_color, card, 3, border_radius=12)

            # En-tête du joueur
            hdr_surf = self.font.render(header, True, p_color)
            self.screen.blit(hdr_surf, hdr_surf.get_rect(center=(card_cx, card.top + 32)))

            # Aperçu agrandi du design de voiture orienté vers le haut
            raw_car = build_car_surface(p_color, spec["design"])
            preview = pygame.transform.rotozoom(raw_car, 90, 2.2)
            self.screen.blit(preview, preview.get_rect(center=(card_cx, card.top + 125)))

            # Nom du modèle sélectionné
            name_surf = self.font.render(f"<  {spec['name']}  >", True, COLOR_TEXT)
            self.screen.blit(name_surf, name_surf.get_rect(center=(card_cx, card.top + 205)))

            # Barres de progression des caractéristiques (échelle max = 1.5)
            stats = [
                ("Accélération", spec["acceleration"]),
                ("Maniabilité", spec["handling"]),
                ("Aérodynamisme", spec["aerodynamics"]),
            ]
            for idx, (stat_label, val) in enumerate(stats):
                y = card.top + 250 + idx * 46
                lbl = self.small_font.render(stat_label, True, COLOR_TEXT)
                self.screen.blit(lbl, (card.left + 30, y))

                bar_bg = pygame.Rect(card.left + 30, y + 20, 320, 12)
                pygame.draw.rect(self.screen, (20, 20, 35), bar_bg, border_radius=6)
                fill_w = int(320 * min(1.0, val / 1.5))
                pygame.draw.rect(self.screen, p_color, (bar_bg.x, bar_bg.y, fill_w, 12), border_radius=6)

        # Bouton de lancement et rappel pour quitter
        play_rect = pygame.Rect(cx - 170, 580, 340, 52)
        pygame.draw.rect(self.screen, COLOR_PANEL, play_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_ACCENT, play_rect, 2, border_radius=10)
        play_txt = self.font.render("DÉMARRER LA COURSE (Entrée)", True, COLOR_ACCENT)
        self.screen.blit(play_txt, play_txt.get_rect(center=play_rect.center))

        quit_txt = self.small_font.render("Quitter : Échap", True, (170, 170, 185))
        self.screen.blit(quit_txt, quit_txt.get_rect(center=(cx, 660)))

    def _draw_racing(self, model: GameModel) -> None:

        for row_idx, row in enumerate(model.circuit.grid):
            for col_idx, tile in enumerate(row):
                sprite = tile.get_sprite(TILE_SIZE)
                self.screen.blit(
                    sprite, (col_idx * TILE_SIZE, row_idx * TILE_SIZE))

        if model.circuit is None:
            return
        for box in model.item_boxes:
            box.draw(self.screen)
        for car in model.cars:
            surf, rect = car.get_rotated_sprite()
            self.screen.blit(surf, rect)
        