from model.terrain_tempo import ROAD, GRASS, DIRT, ICE
from model.tile import Tile
from model.circuit import Circuit

LEGEND = {
    "R": (ROAD, (80, 80, 90)),
    "G": (GRASS, (50, 140, 60)),
    "I": (ICE, (120, 190, 240)),
    "D": (DIRT, (155, 118, 83)),
    "1": (ROAD, (80, 80, 90)),
    "2": (ROAD, (80, 80, 90)),
    "W": (ROAD, (150, 50, 40)),
    "C": (ROAD, (230, 200, 60)),
    "L": (ROAD, (240, 240, 240)),
    "V": (ROAD, (10, 10, 10)),
    "B": (ROAD, (255, 60, 200)),
    "M": (ROAD, (80, 80, 90)),
    "A": (GRASS, (255, 105, 125)),  # rubis clair
    "E": (GRASS, (215, 20, 55)),    # rubis
    "K": (GRASS, (120, 0, 30)),     # rubis foncé
    "S": (GRASS, (110, 180, 255)),  # saphir clair
    "U": (GRASS, (30, 90, 220)),    # saphir
    "X": (GRASS, (10, 30, 110)),    # saphir foncé
}

CIRCUIT_1 = [
    "WWWWWWWWWWWWWWWW",
    "WRRRRL1RR2RRRRRW",
    "WRRRRLRRRRRRRRRW",
    "WRRGGGGGGGGGGBBW",
    "WRRGGGVGVGGGGRRW",
    "WRRGVRIIIIRGGRRW",
    "WMMGVRIIIIRGGRRW",
    "WRRGGCCWWCCGGRRW",
    "WRRGGRRGGRRGGRRW",
    "WRRCRRRGGRRDDCRW",   
    "WRRCRRRGGRRDDCRW",   
    "WWWWWWWWWWWWWWWW",
]
CIRCUIT_2 = [
    "WWWWWWWWWWWWWWWW",
    "WVGGGGRCCRGGGGVW",
    "WGGGGRRGGIIGGGVW",
    "WGGGMMGGGGIIGGVW",
    "WGGRRGGVVGGIIGGW",
    "WGLLGGGVVGGGCCGW",
    "WG12GGGVVGGGRRGW",
    "WGGRRGGVVGGBBGGW",
    "WVGGBBGGGGRRGGVW",
    "WVGGGMMGGRRGGGVW",
    "WGGGGGRCCRGGGGGW",
    "WWWWWWWWWWWWWWWW",
]
CIRCUIT_3 = [
    "WWWWWWWWWWWWWWWW",
    "WVRRRRVVVVRRRRVW",
    "WIIWWRRVVRRWWIIW",
    "WRRWBWRMMRWBWRRW",
    "WCCWIEWRRWUIWCCW",
    "WRRWAKWLLWXSWRRW",
    "WMRWEKW12WXUWRMW",
    "WRRWEKWRRWXUWRRW",
    "WRRWBWRRRRWBWRRW",
    "WRRWWRRVVRRWWRRW",
    "WVRCCRVVVVRCCRVW",
    "WWWWWWWWWWWWWWWW",
]

def build_circuit(layout):
    grid = []
    starts = {}  
    walls  =set()  
    checkpoints = []  
    finish = set()  
    voids = set()
    boosts = set()  
    item_boxes = set()                          
    for row_idx, line in enumerate(layout):
        row = []
        for col_idx, letter in enumerate(line):
            terrain, color = LEGEND[letter]
            row.append(Tile(col_idx, row_idx, terrain, color))
            if letter in "12":                       
                starts[letter] = (col_idx, row_idx)  
            if letter == "W":
                walls.add((col_idx, row_idx))          
            if letter == "C":
                group = None
                for g in checkpoints:
                    if (col_idx - 1, row_idx) in g or (col_idx, row_idx - 1) in g:
                        group = g
                if group is None:
                    group = set()
                    checkpoints.append(group)
                group.add((col_idx, row_idx))
            if letter == "L":
                finish.add((col_idx, row_idx))
            if letter == "V":
                voids.add((col_idx, row_idx)) 
            if letter == "B":
                boosts.add((col_idx, row_idx))
            if letter == "M":
                item_boxes.add((col_idx, row_idx))
        grid.append(row)
    circuit = Circuit(grid)
    circuit.starts = starts
    circuit.walls = walls
    circuit.checkpoints = checkpoints
    circuit.finish = finish
    circuit.voids = voids
    circuit.boosts = boosts
    circuit.item_boxes = item_boxes

    return circuit
CIRCUITS = [
    {"layout": CIRCUIT_1, "order": [[3, 1, 0, 2], [3, 1, 0, 2]], "laps": 3},
    {"layout": CIRCUIT_2, "order": [[2, 1, 0], [2, 1, 0]], "laps": 5},   
    {"layout": CIRCUIT_3, "order": [[2, 0, 3, 1], [3, 1, 2, 0]], "laps": 3},
]