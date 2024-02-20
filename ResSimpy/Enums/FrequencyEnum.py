"""Enum for defining frequency labels for outputs."""
from enum import Enum


class FrequencyEnum(Enum):
    """Enum for defining frequency labels for outputs."""

    UNDEFINED = 0
    NONE = 1
    DT = 2
    DTTOL = 3
    TIMES = 4
    FREQ = 5
    TNEXT = 6
    MONTHLY = 7
    QUARTERLY = 8
    YEARLY = 9
    TIMESTEP = 10
    TSTART = 11
    OFF = 12
    ON = 13
