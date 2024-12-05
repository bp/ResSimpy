"""Abstract base class for constraints."""
from __future__ import annotations
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import pandas as pd

from ResSimpy.DataModelBaseClasses.Constraint import Constraint
from typing import Optional, Mapping, Sequence

from ResSimpy.Enums.UnitsEnum import UnitSystem


@dataclass(kw_only=True)
class Constraints(ABC):
    """Abstract base class for constraints."""
    _constraints: Mapping[str, Sequence[Constraint]] | list[Constraint] = field(default_factory=dict)

    @property
    def constraints(self) -> Mapping[str, Sequence[Constraint]] | list[Constraint]:
        """Returns mapping of constraints."""
        return self._constraints

    @abstractmethod
    def get_all(self, object_name: Optional[str] = None, date: Optional[str] = None) \
            -> Mapping[str, Sequence[Constraint]]:
        """Get the constraints of the existing model with optional parameters to filter for name and date.

        Args:
            object_name(Optional[str] = None): name of the connection, node or wellname to return. Defaults to None.
            date(Optional[str] = None)): date in model format to filter the dates to in the constraints.
        """
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def get_df(self) -> pd.DataFrame:
        """Creates a dataframe representing all processed constraint data in a surface file."""
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def get_overview(self) -> str:
        """Returns an overview of the constraint."""
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def remove(self) -> None:
        """Remove a constraint."""
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def add(self,
            constraint_to_add: dict[str, None | float | int | str | UnitSystem] | Constraint,
            comments: str | None,
            ) -> None:
        """Adds a constraint to the network and corresponding surface file.

        Args:
            constraint_to_add(dict[str, None | float | int | str | UnitSystem] | Constraint): properties of the
            constraints or a constraint object.
            comments(str): add optional post line comments.
        """
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def modify(self, name: str,
               current_constraint: dict[str, None | float | int | str] | Constraint,
               new_constraint_props: dict[str, None | float | int | str | UnitSystem] | Constraint,
               comments: Optional[str] = None) \
            -> None:
        """Adds optional post line comments in the modified constraint.

        Args:
            name(str): The well name.
            current_constraint(dict[str, None | float | int | str] | Constraint):Modify an existing constraint.
            new_constraint_props(dict[str, None | float | int | str | UnitSystem] | Constraint): dictionary or
            constraint to update the constraint with.
            comments(Optional[str]):??
        """
        raise NotImplementedError("Implement this in the derived class")
