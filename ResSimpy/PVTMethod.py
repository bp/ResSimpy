from abc import ABC
from dataclasses import dataclass


@dataclass
class PVTMethod(ABC):
    """The abstract base class for PVT methods
    Attributes:
        method_number (int): Method number in order of PVT methods in simulator input file
    """

    method_number: int

    def __init__(self, method_number):
        self.method_number = method_number
