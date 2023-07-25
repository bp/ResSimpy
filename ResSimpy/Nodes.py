from dataclasses import dataclass
from abc import ABC, abstractmethod
from uuid import UUID

import pandas as pd
from ResSimpy.Node import Node
from typing import Sequence, Optional, Literal


@dataclass(kw_only=True)
class Nodes(ABC):
    @abstractmethod
    def get_nodes(self) -> Sequence[Node]:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def get_node(self, node_name: str) -> Optional[Node]:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def get_node_df(self) -> pd.DataFrame:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def get_nodes_overview(self) -> str:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def remove_node(self, node_to_remove: UUID | dict[str, None | str | float | int]) -> None:
        raise NotImplementedError("Implement this in the derived class")

    def add_node(self, node_to_add: dict[str, None | str | float | int]) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @property
    def table_header(self) -> str:
        raise NotImplementedError("Implement this in the derived class")

    @property
    def table_footer(self) -> str:
        raise NotImplementedError("Implement this in the derived class")

    @property
    def _network_element_name(self) -> Literal['nodes']:
        return 'nodes'
