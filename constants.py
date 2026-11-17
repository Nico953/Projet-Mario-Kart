WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60

TILE_SIZE = 64
GRID_COLS = 16
GRID_ROWS = 12

CAR_ACCELERATION = 0.10
CAR_TURN_RATE = 0.6
CAR_AIR_DRAG = 0.02
CAR_WIDTH = 30
CAR_HEIGHT = 50


class GameState:
    MENU = "menu"
    RACING = "racing"


# --- Couleurs UI ---
COLOR_BG = (15, 15, 25)
COLOR_TEXT = (240, 240, 240)
COLOR_ACCENT = (255, 200, 0)
COLOR_PANEL = (30, 30, 50)
COLOR_PANEL_BORDER = (60, 60, 100)


# --- Couleurs joueurs et modèles personnalisables ---
COLOR_P1 = (220, 40, 40)
COLOR_P2 = (40, 90, 220)

CAR_MODELS = [
    {
        "name": "Équilibrée",
        "acceleration": 1.0,
        "handling": 1.0,
        "aerodynamics": 1.0,
        "design": "sport",
    },
    {
        "name": "Dragster",
        "acceleration": 1.35,
        "handling": 0.75,
        "aerodynamics": 0.90,
        "design": "muscle",
    },
    {
        "name": "Agile",
        "acceleration": 0.85,
        "handling": 1.35,
        "aerodynamics": 0.95,
        "design": "compact",
    },
    {
        "name": "Aéro F1",
        "acceleration": 0.95,
        "handling": 1.05,
        "aerodynamics": 1.35,
        "design": "formula",
    },
]