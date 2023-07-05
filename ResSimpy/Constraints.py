from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import pandas as pd

from ResSimpy.Constraint import Constraint
from typing import Optional, Mapping, Sequence


@dataclass(kw_only=True)
class Constraints(ABC):
    __constraints: dict[str, list[Constraint]] = field(default_factory=lambda: {})

    @abstractmethod
    def get_constraints(self, object_name: Optional[str] = None, date: Optional[str] = None) \
            -> Mapping[str, Sequence[Constraint]]:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def get_constraint_df(self) -> pd.DataFrame:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def get_constraint_overview(self) -> str:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def remove_constraint(self):
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def add_constraint(self):
        raise NotImplementedError("Implement this in the derived class")
