from __future__ import annotations
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import pandas as pd

from ResSimpy.Constraint import Constraint
from typing import Optional, Mapping, Sequence

from ResSimpy.Enums.UnitsEnum import UnitSystem


@dataclass(kw_only=True)
class Constraints(ABC):
    __constraints: dict[str, list[Constraint]] = field(default_factory=lambda: {})

    @abstractmethod
    def get_all(self, object_name: Optional[str] = None, date: Optional[str] = None) \
            -> Mapping[str, Sequence[Constraint]]:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def get_df(self) -> pd.DataFrame:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def get_overview(self) -> str:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def remove(self) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def add(self,
            constraint_to_add: dict[str, None | float | int | str | UnitSystem] | Constraint,
            comments: str | None,
            ) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def modify(self, name: str,
               current_constraint: dict[str, None | float | int | str] | Constraint,
               new_constraint_props: dict[str, None | float | int | str | UnitSystem] | Constraint,
               comments: Optional[str] = None) \
            -> None:
        raise NotImplementedError("Implement this in the derived class")
