from enum import Enum


class PvtType(str, Enum):
    """Enum representing the different PVT types."""
    BLACKOIL = 'BLACKOIL'
    GASWATER = 'GASWATER'
    WATEROIL = 'WATEROIL'
    EOS = 'EOS'
    API = 'API'


class SeparatorType(str, Enum):
    """Enum representing the different separator types."""
    BLACKOIL = 'BLACKOIL'
    GASPLANT = 'GASPLANT'
    EOS = 'EOS'


class PhaseType(str, Enum):
    """Enum representing the different phase types."""
    OIL = 'OIL'
    LIQUID = 'LIQ'
    GAS = 'GAS'
    RESERVOIR = 'RES'
    COMBINED = 'COMB'
    NONE = 'NONE'
