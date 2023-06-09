from abc import ABC
from dataclasses import dataclass


@dataclass
class DynamicProperty(ABC):
    """The abstract base class for dynamic property simulator inputs, for use in inputs such as PVT, relperm, etc.

    Attributes
    ----------
        input_number (int): Method, table or input number, in order as entered in the simulation input deck.
    """

    input_number: int

    def __init__(self, input_number: int) -> None:
        self.input_number: int = input_number
