from abc import ABC
from dataclasses import dataclass


@dataclass
class RockMethod(ABC):
    """The abstract base class for rock property methods
    Attributes:
        method_number (int): Method number in order of rock methods in simulator input file
    """

    method_number: int

    def __init__(self, method_number):
        self.method_number = method_number
