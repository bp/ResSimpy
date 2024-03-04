from enum import Enum


class PvtType(str, Enum):
    """Enum representing the different PVT types."""
    BLACKOIL = 'BLACKOIL'
    GASWATER = 'GASWATER'
    WATEROIL = 'WATEROIL'
    EOS = 'EOS'


class SeparatorType(str, Enum):
    """Enum representing the different separator types."""
    BLACKOIL = 'BLACKOIL'
    GASPLANT = 'GASPLANT'
    EOS = 'EOS'
