class TerrainTempo:
    """Terrain provisoire pour tester la voiture en attendant les vrais terrains.

    traction : facilité à accélérer et freiner (1 = parfait).
    drift_threshold : vitesse latérale au-delà de laquelle la voiture dérape.
    drift_friction : part de la vitesse latérale perdue à chaque image en dérapage.
    """

    def __init__(self, traction: float, drift_threshold: float,
                 drift_friction: float):
        self.traction = traction
        self.drift_threshold = drift_threshold
        self.drift_friction = drift_friction


ROAD = TerrainTempo(traction=1.0, drift_threshold=0.21, drift_friction=0.15)
GRASS = TerrainTempo(traction=0.7, drift_threshold=0.09, drift_friction=0.10)
DIRT = TerrainTempo(traction=0.6, drift_threshold=0.05, drift_friction=0.06)
ICE = TerrainTempo(traction=0.5, drift_threshold=0.004, drift_friction=0.01)