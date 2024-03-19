from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Sequence, Optional, TYPE_CHECKING
from uuid import UUID

import pandas as pd

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.File import File
if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import Network


class NetworkOperationsMixIn(ABC):
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
    def _add_to_memory(self, additional_objs: Optional[list[Any]]):
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
