from abc import ABC
from dataclasses import dataclass


@dataclass
class AquiferMethod(ABC):
    """The abstract base class for aquifer methods
    Attributes:
        method_number (int): Method number in order of aquifer methods in simulator input
    """

    method_number: int

    def __init__(self, method_number: int) -> None:
        self.method_number: int = method_number
