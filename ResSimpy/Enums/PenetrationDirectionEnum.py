from enum import Enum


class PenetrationDirectionEnum(str, Enum):
    """Enum representing the penetration direction options in Eclipse."""
    X = 'X'
    Y = 'Y'
    Z = 'Z'
    FX = 'FX'
    FY = 'FY'
