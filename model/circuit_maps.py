from model.TerrainTempo import ROAD, GRASS, DIRT, ICE
from model.tile import Tile
from model.circuit import Circuit

LEGEND = {
    "R": (ROAD, (80, 80, 90)),
    "G": (GRASS, (50, 140, 60)),
    "I": (ICE, (214, 234, 240)),
    "D": (DIRT, (155, 118, 83)),
}

CIRCUIT_1 = [
    "GGGGGGGGGGGGGGGG",
    "GRRRRRRRRRRRRRRG",
    "GRRRRRRRRRRRRRRG",
    "GRRGGGGGGGGGGRRG",
    "GRRGGGGDGGGGGRRG",
    "GRRGGRIIIIRGGRRG",
    "GRRGGRIIIIRGGRRG",
    "GRRGGRRDGRRGGRRG",
    "GRRGGRRGGRRGGRRG",
    "GRRRRRRGGRRDDRRG",
    "GRRRRRRGGRRDDRRG",
    "GGGGGGGGGGGGGGGG",
]
def build_circuit(layout):
    grid = []
    for row_idx, line in enumerate(layout):
        row = []
        for col_idx, letter in enumerate(line):
            terrain, color = LEGEND[letter]
            row.append(Tile(col_idx, row_idx, terrain, color))
        grid.append(row)
    return Circuit(grid)