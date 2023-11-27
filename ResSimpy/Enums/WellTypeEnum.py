"""Collection of Enumerations for Units used in ResSimpy."""
from enum import Enum


# Enum representing the different well types
class WellType(str, Enum):
    PRODUCER = 'PRODUCER'
    OIL_INJECTOR = 'OIL_INJECTOR'
    GAS_INJECTOR = 'GAS_INJECTOR'
    WATER_INJECTOR = 'WATER_INJECTOR'
    SOLVENT_INJECTOR = 'SOLVENT_INJECTOR'
