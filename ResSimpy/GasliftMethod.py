from abc import ABC
from dataclasses import dataclass


@dataclass
class GasliftMethod(ABC):
    """The abstract base class for gaslift methods
    Attributes:
        method_number (int): Method number in order of gaslift methods in simulator input.
    """

    method_number: int

    def __init__(self, method_number) -> None:
        self.method_number = method_number
