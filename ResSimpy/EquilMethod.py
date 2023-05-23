from abc import ABC
from dataclasses import dataclass


@dataclass
class EquilMethod(ABC):
    """The abstract base class for equilibration methods
    Attributes:
        method_number (int): Method number in order of equilibration methods in simulator input file
    """

    method_number: int

    def __init__(self, method_number):
        self.method_number = method_number