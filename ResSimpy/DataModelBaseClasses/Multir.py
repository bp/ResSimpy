from abc import ABC
from dataclasses import dataclass


@dataclass
class Multir(ABC):
    """Used to represent a single multiplier between regions in a grid."""
    region_1: None | int = None
    region_2: None | int = None
    tmult: None | float = None
    directions: None | str = None
    std_connections: bool = True
    non_std_connections: bool = True
