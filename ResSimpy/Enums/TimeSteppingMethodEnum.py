"""Enum representing the different timestepping and solver methods."""
from enum import Enum


class TimeSteppingMethod(str, Enum):
    """Enum representing the different timestepping and solver methods."""
    IMPLICIT = 'IMPLICIT'
    IMPES = 'IMPES'
