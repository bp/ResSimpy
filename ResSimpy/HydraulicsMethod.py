from abc import ABC
from dataclasses import dataclass


@dataclass
class HydraulicsMethod(ABC):
    """The abstract base class for hydraulics methods
    Attributes:
        method_number (int): Method number in order of hydraulics methods in simulator input.
    """

    method_number: int

    def __init__(self, method_number: int) -> None:
        self.method_number: int = method_number
