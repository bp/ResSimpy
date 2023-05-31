from abc import ABC
from dataclasses import dataclass


@dataclass
class ValveMethod(ABC):
    """The abstract base class for valve methods
    Attributes:
        method_number (int): Method number in order of valve methods in simulator input.
    """

    method_number: int

    def __init__(self, method_number: int) -> None:
        self.method_number: int = method_number
