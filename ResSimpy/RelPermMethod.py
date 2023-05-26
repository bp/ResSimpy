from abc import ABC
from dataclasses import dataclass


@dataclass
class RelPermMethod(ABC):
    """The abstract base class for relative permeability and capillary pressure methods
    Attributes:
        method_number (int): Method number in order of rel perm and cap pressure methods in simulator input.
    """

    method_number: int

    def __init__(self, method_number) -> None:
        self.method_number = method_number
