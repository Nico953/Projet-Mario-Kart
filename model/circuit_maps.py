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
}

CIRCUIT_1 = [
    "WWWWWWWWWWWWWWWW",
    "WRRRRL1RR2RRRRRW",
    "WRRRRLRRRRRRRRRW",
    "WRRGGGGGGGGGGRRW",
    "WRRGGGVGVGGGGRRW",
    "WRRWVRIIIIRGGRRW",
    "WRRWVRIIIIRGGRRW",
    "WRRWGCCWWCCGGRRW",
    "WRRWGRRGGRRGGRRW",
    "WRRCRRRGGRRDDCRW",   
    "WRRCRRRGGRRDDCRW",   
    "WWWWWWWWWWWWWWWW",
]
def build_circuit(layout):
    grid = []
    starts = {}  
    walls  =set()  
    checkpoints = []  
    finish = set()  
    voids = set()                            
    for row_idx, line in enumerate(layout):
        row = []
        for col_idx, letter in enumerate(line):
            terrain, color = LEGEND[letter]
            row.append(Tile(col_idx, row_idx, terrain, color))
            if letter in "12":                       
                starts[letter] = (col_idx, row_idx)  
            if letter == "W":
                walls.add((col_idx, row_idx))
            if letter == "V":
                voids.add((col_idx, row_idx))
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
        grid.append(row)
    circuit = Circuit(grid)
    circuit.starts = starts
    circuit.walls = walls
    circuit.checkpoints = checkpoints
    circuit.finish = finish
    circuit.voids = voids

    return circuit
