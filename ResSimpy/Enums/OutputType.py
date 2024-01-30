"""Enum for defining types of outputs."""
from enum import Enum


class OutputType(Enum):
    """Enum for defining types of outputs."""

    UNDEFINED = 0
    NONE = 1
    ARRAY = 2
    SPREADSHEET = 4
    MAP = 5
