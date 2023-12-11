from enum import Enum


class SimulationType(str, Enum):
    """Enum representing OpenGoSim Simulation Types."""
    SUBSURFACE = 'SUBSURFACE'
    GEOMECHANICS_SUBSURFACE = 'GEOMECHANICS_SUBSURFACE'
