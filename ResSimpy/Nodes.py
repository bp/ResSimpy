from dataclasses import dataclass
from abc import ABC
import pandas as pd
from ResSimpy.Node import Node
from typing import Sequence, Optional


@dataclass(kw_only=True)
class Nodes(ABC):
    def get_nodes(self) -> Sequence[Node]:
        raise NotImplementedError("Implement this in the derived class")

    def get_node(self, node_name: str) -> Optional[Node]:
        raise NotImplementedError("Implement this in the derived class")

    def get_node_df(self) -> pd.DataFrame:
        raise NotImplementedError("Implement this in the derived class")

    def get_nodes_overview(self) -> str:
        raise NotImplementedError("Implement this in the derived class")
