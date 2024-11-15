from enum import Enum


class ActivationChangeEnum(str, Enum):
    """Enum representing whether an object has been activated or deactivated."""
    ACTIVATE = 'ACTIVATE'
    DEACTIVATE = 'DEACTIVATE'
