"""Enum representing the different timestepping and solver methods."""
from enum import StrEnum


class TimeSteppingMethod(StrEnum):
    """Enum representing the different timestepping and solver methods."""
    IMPLICIT = 'IMPLICIT'
    IMPES = 'IMPES'
