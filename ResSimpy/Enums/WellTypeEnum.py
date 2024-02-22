"""Collection of Enumerations for well type used in ResSimpy."""
from enum import Enum


class WellType(str, Enum):
    """An enum representing the type of the well."""
    PRODUCER = 'PRODUCER'
    OIL_INJECTOR = 'OIL_INJECTOR'
    GAS_INJECTOR = 'GAS_INJECTOR'
    WATER_INJECTOR = 'WATER_INJECTOR'
    SOLVENT_INJECTOR = 'SOLVENT_INJECTOR'
    WAG_INJECTOR = 'WAG_INJECTOR'
