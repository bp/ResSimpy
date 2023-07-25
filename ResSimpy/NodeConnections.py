from dataclasses import dataclass
from abc import ABC, abstractmethod
from uuid import UUID

import pandas as pd
from typing import Sequence, Optional, Literal

from ResSimpy.NodeConnection import NodeConnection


@dataclass(kw_only=True)
class NodeConnections(ABC):
    def get_connections(self) -> Sequence[NodeConnection]:
        raise NotImplementedError("Implement this in the derived class")

    def get_connection(self, node_name: str) -> Optional[NodeConnection]:
        raise NotImplementedError("Implement this in the derived class")

    def get_connection_df(self) -> pd.DataFrame:
        raise NotImplementedError("Implement this in the derived class")

    def get_connections_overview(self) -> str:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def remove_connection(self, connection_to_remove: UUID | dict[str, None | str | float | int]) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def add_connection(self, connection_to_add: dict[str, None | str | float | int]) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def modify_connection(self, connection_to_modify: dict[str, None | str | float | int],
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
    def _network_element_name(self) -> Literal['connections']:
        return 'connections'
