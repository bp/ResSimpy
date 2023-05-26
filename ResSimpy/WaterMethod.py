from abc import ABC
from dataclasses import dataclass


@dataclass
class WaterMethod(ABC):
    """The abstract base class for water methods
    Attributes:
        method_number (int): Method number in order of water methods in simulator input
    """

    method_number: int

    def __init__(self, method_number) -> None:
        self.method_number = method_number
