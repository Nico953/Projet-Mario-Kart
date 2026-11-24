import pygame
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE,
    COLOR_BG, COLOR_TEXT, COLOR_ACCENT, COLOR_PANEL, COLOR_PANEL_BORDER,
    COLOR_P1, COLOR_P2, CAR_MODELS, GameState
)
from model.car import build_car_surface
from model.circuit_maps import CIRCUITS, LEGEND
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

    def _draw_circuit_preview(self, layout: list[str], center: tuple[int, int]) -> None:
        """Dessine un aperçu miniature du circuit sélectionné dans le menu."""
        cell = 8
        rows = len(layout)
        cols = len(layout[0])
        surf = pygame.Surface((cols * cell, rows * cell))
        for r, line in enumerate(layout):
            for c, letter in enumerate(line):
                _, color = LEGEND[letter]
                pygame.draw.rect(surf, color, (c * cell, r * cell, cell, cell))
        rect = surf.get_rect(center=center)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, rect.inflate(6, 6), 2, border_radius=4)
        self.screen.blit(surf, rect)

    def _draw_menu(self, model: GameModel) -> None:
        """Affiche le menu de personnalisation des voitures et de choix du circuit."""
        cx = WINDOW_WIDTH // 2

        title_surf = self.title_font.render(
            "PERSONNALISATION DES VOITURES", True, COLOR_ACCENT)
        self.screen.blit(title_surf, title_surf.get_rect(center=(cx, 55)))

        players_info = [
            ("JOUEUR 1 (Q / D)", COLOR_P1, model.selected_models[0], cx - 310),
            ("JOUEUR 2 (← / →)", COLOR_P2, model.selected_models[1], cx + 310),
        ]

        for header, p_color, model_idx, card_cx in players_info:
            spec = CAR_MODELS[model_idx]
            card = pygame.Rect(0, 0, 340, 390)
            card.center = (card_cx, 315)
            pygame.draw.rect(self.screen, COLOR_PANEL, card, border_radius=12)
            pygame.draw.rect(self.screen, p_color, card, 3, border_radius=12)

            # En-tête du joueur
            hdr_surf = self.font.render(header, True, p_color)
            self.screen.blit(hdr_surf, hdr_surf.get_rect(center=(card_cx, card.top + 30)))

            # Aperçu agrandi du design de voiture orienté vers le haut
            raw_car = build_car_surface(p_color, spec["design"])
            preview = pygame.transform.rotozoom(raw_car, 90, 2.1)
            self.screen.blit(preview, preview.get_rect(center=(card_cx, card.top + 115)))

            # Nom du modèle sélectionné
            name_surf = self.font.render(f"<  {spec['name']}  >", True, COLOR_TEXT)
            self.screen.blit(name_surf, name_surf.get_rect(center=(card_cx, card.top + 190)))

            # Barres de progression des caractéristiques (échelle max = 1.5)
            stats = [
                ("Accélération", spec["acceleration"]),
                ("Maniabilité", spec["handling"]),
                ("Aérodynamisme", spec["aerodynamics"]),
            ]
            for idx, (stat_label, val) in enumerate(stats):
                y = card.top + 230 + idx * 45
                lbl = self.small_font.render(stat_label, True, COLOR_TEXT)
                self.screen.blit(lbl, (card.left + 25, y))

                bar_bg = pygame.Rect(card.left + 25, y + 20, 290, 12)
                pygame.draw.rect(self.screen, (20, 20, 35), bar_bg, border_radius=6)
                fill_w = int(290 * min(1.0, val / 1.5))
                pygame.draw.rect(self.screen, p_color, (bar_bg.x, bar_bg.y, fill_w, 12), border_radius=6)

        # Panneau central de sélection du circuit
        c_idx = model.selected_circuit
        c_data = CIRCUITS[c_idx]
        c_card = pygame.Rect(0, 0, 230, 250)
        c_card.center = (cx, 315)
        pygame.draw.rect(self.screen, COLOR_PANEL, c_card, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_ACCENT, c_card, 2, border_radius=12)

        c_title = self.font.render(f"Circuit {c_idx + 1} / {len(CIRCUITS)}", True, COLOR_ACCENT)
        self.screen.blit(c_title, c_title.get_rect(center=(cx, c_card.top + 28)))

        self._draw_circuit_preview(c_data["layout"], (cx, c_card.top + 115))

        laps_txt = self.small_font.render(f"Objectif : {c_data['laps']} tours", True, COLOR_TEXT)
        self.screen.blit(laps_txt, laps_txt.get_rect(center=(cx, c_card.top + 190)))

        hint_txt = self.small_font.render("Z / S ou ↑ / ↓", True, (170, 170, 185))
        self.screen.blit(hint_txt, hint_txt.get_rect(center=(cx, c_card.top + 220)))

        # Bouton de lancement et rappel pour quitter
        play_rect = pygame.Rect(cx - 170, 565, 340, 50)
        pygame.draw.rect(self.screen, COLOR_PANEL, play_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_ACCENT, play_rect, 2, border_radius=10)
        play_txt = self.font.render("DÉMARRER LA COURSE (Entrée)", True, COLOR_ACCENT)
        self.screen.blit(play_txt, play_txt.get_rect(center=play_rect.center))

        quit_txt = self.small_font.render("Quitter : Échap", True, (170, 170, 185))
        self.screen.blit(quit_txt, quit_txt.get_rect(center=(cx, 645)))

    def _draw_hud(self, model: GameModel) -> None:
        """Affiche en course le numéro du circuit, les tours et l'objet de chaque joueur."""
        bar = pygame.Rect(0, 0, WINDOW_WIDTH, 36)
        pygame.draw.rect(self.screen, (15, 15, 25), bar)

        c_txt = self.small_font.render(
            f"Circuit {model.selected_circuit + 1}/{len(CIRCUITS)}  |  Échap : Menu",
            True, COLOR_ACCENT
        )
        self.screen.blit(c_txt, c_txt.get_rect(center=(WINDOW_WIDTH // 2, 18)))

        if len(model.cars) >= 2:
            held1 = getattr(model.cars[0], "held_item", None)
            held2 = getattr(model.cars[1], "held_item", None)
            item1 = held1.name if held1 else "Aucun"
            item2 = held2.name if held2 else "Aucun"
            p1_txt = self.small_font.render(
                f"J1 — Tours : {model.laps[0]}/{model.laps_to_win} | Objet (E) : {item1}",
                True, COLOR_P1
            )
            p2_txt = self.small_font.render(
                f"J2 — Tours : {model.laps[1]}/{model.laps_to_win} | Objet (Shift D) : {item2}",
                True, COLOR_P2
            )
            self.screen.blit(p1_txt, (16, 9))
            self.screen.blit(p2_txt, p2_txt.get_rect(topright=(WINDOW_WIDTH - 16, 9)))

    def _draw_winner_overlay(self, model: GameModel) -> None:
        """Affiche le bandeau du vainqueur en fin de course."""
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        win_color = COLOR_P1 if model.winner == 1 else COLOR_P2
        box = pygame.Rect(0, 0, 500, 170)
        box.center = (cx, cy)
        pygame.draw.rect(self.screen, COLOR_PANEL, box, border_radius=14)
        pygame.draw.rect(self.screen, win_color, box, 4, border_radius=14)

        win_surf = self.title_font.render(f"VICTOIRE DU JOUEUR {model.winner} !", True, win_color)
        self.screen.blit(win_surf, win_surf.get_rect(center=(cx, cy - 28)))

        sub_surf = self.small_font.render("Entrée : Rejouer   |   Échap : Retour au menu", True, COLOR_TEXT)
        self.screen.blit(sub_surf, sub_surf.get_rect(center=(cx, cy + 35)))

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
        # Affichage des pièges actifs sur la piste (bananes et bombes)
        for hazard in getattr(model, "hazards", []):
            hazard.draw(self.screen)
        for car in model.cars:
            surf, rect = car.get_rotated_sprite()
            self.screen.blit(surf, rect)
        self._draw_hud(model)
        if model.winner is not None:
            self._draw_winner_overlay(model)