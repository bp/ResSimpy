from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from typing import Any, Sequence, Optional, TYPE_CHECKING, TypeVar
from uuid import UUID

import pandas as pd

from ResSimpy.DataObjectMixin import DataObjectMixin
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.File import File

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import Network

T = TypeVar('T', bound=DataObjectMixin)


class NetworkOperationsMixIn(ABC):
    """A mixin for network collections that forces the implementation of the same methods across all classes."""
    def __init__(self, parent_network: Network) -> None:
        """Initialises the NetworkOperationsMixIn class.

        Args:
            parent_network (Network): The parent network that the object is a part of.
        """
        self.__parent_network = parent_network

    @abstractmethod
    def get_all(self) -> Sequence[Any]:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Any]:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def get_df(self) -> pd.DataFrame:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def get_overview(self) -> str:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def load(self, file: File, start_date: str, default_units: UnitSystem) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def _add_to_memory(self, additional_objs: Optional[list[Any]]) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def remove(self, obj_to_remove: UUID | dict[str, None | str | float | int]) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def add(self, obj_to_add: dict[str, None | str | float | int]) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def modify(self, obj_to_modify: dict[str, None | str | float | int],
               new_properties: dict[str, None | str | float | int]) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @property
    @abstractmethod
    def table_header(self) -> str:
        raise NotImplementedError("Implement this in the derived class")

    @property
    @abstractmethod
    def table_footer(self) -> str:
        raise NotImplementedError("Implement this in the derived class")

    @property
    @abstractmethod
    def _network_element_name(self) -> str:
        raise NotImplementedError("Implement this in the derived class")

    @staticmethod
    def resolve_carried_over_attributes(objects_to_resolve: Sequence[T]) -> Sequence[T]:
        """Resolves carried over attributes from previous time steps to the future timesteps.

        Args:
            objects_to_resolve (Sequence[DataObjectMixin]): list of objects to resolve carried over attributes for.
            Must be of homogenous type.
        """
        resolved_objects: list[T] = []

        if (len(objects_to_resolve) > 0 and
                not all(isinstance(x, type(objects_to_resolve[0])) for x in objects_to_resolve)):
            raise ValueError("Objects to resolve must be of the same type.")

        # order by date and the order entered in the simulator.
        current_ordering = list(enumerate(objects_to_resolve))
        sorted_by_date_sim_ordering = sorted(current_ordering, key=lambda x: (x[1].iso_date, x[0]))
        sorted_by_date = [x[1] for x in sorted_by_date_sim_ordering]
        # split by the name of the object
        unique_names = list({x.name for x in sorted_by_date})

        # resolve by name
        for name in unique_names:
            matching_names = [x for x in sorted_by_date if x.name == name]
            resolving_by_name = NetworkOperationsMixIn.resolve_same_named_objects(matching_names)
            resolved_objects.extend(resolving_by_name)

        return resolved_objects

    @staticmethod
    def resolve_same_named_objects(sorted_by_date: Sequence[T]) -> Sequence[T]:
        """Resolves a subset of objects by date."""
        resolved_objects: list[T] = []
        for unresolved_obj in sorted_by_date:
            # append the first
            if len(resolved_objects) == 0:
                resolved_objects.append(unresolved_obj)
                continue
            last_resolved_object = resolved_objects[-1]

            new_resolved_object = copy.deepcopy(unresolved_obj)

            for attr, value in last_resolved_object.__dict__.items():
                if value is not None and getattr(unresolved_obj, attr, None) is None:
                    setattr(new_resolved_object, attr, value)
            resolved_objects.append(new_resolved_object)
        return resolved_objects
