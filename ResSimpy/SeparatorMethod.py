from abc import ABC
from dataclasses import dataclass


@dataclass
class SeparatorMethod(ABC):
    """The abstract base class for separator property methods
    Attributes:
        method_number (int): Method number in order of separator methods in simulator input file
    """

    method_number: int

    def __init__(self, method_number):
        self.method_number = method_number
