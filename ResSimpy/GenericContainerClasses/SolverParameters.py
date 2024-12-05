from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence

from ResSimpy.DataModelBaseClasses.SolverParameter import SolverParameter


@dataclass
class SolverParameters(ABC):
    """Abstract base class for storing solver parameter objects and handle loading of these parameters."""

    __solver_parameters: Sequence[SolverParameter]

    @abstractmethod
    def load(self) -> None:
        """Loads the solver parameters given to the simulator."""
        raise NotImplementedError("Implement this in the derived class.")

    @property
    @abstractmethod
    def solver_parameters(self) -> Sequence[SolverParameter]:
        """Returns an instance of Solver Parameter in a sequence (usually of type list)."""
        return self.__solver_parameters
