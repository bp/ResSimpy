from enum import Enum


class ActivationChangeEnum(str, Enum):
    """Enum representing the different PVT types."""
    ACTIVATE= 'ACTIVATE'
    DEACTIVATE = 'DEACTIVATE'

