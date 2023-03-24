from dataclasses import dataclass, field
import pandas as pd

from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.Surface.NexusNode import NexusNode
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.Surface.load_nodes import load_nodes
from ResSimpy.Nodes import Nodes
from typing import Sequence, Optional


@dataclass(kw_only=True)
class NexusNodes(Nodes):
    __nodes: list[NexusNode] = field(default_factory=lambda: [])

    def get_nodes(self) -> Sequence[NexusNode]:
        return self.__nodes

    def get_node(self, node_name: str) -> Optional[NexusNode]:
        nodes_to_return = filter(lambda x: x.name.upper() == node_name.upper(), self.__nodes)
        return next(nodes_to_return, None)

    def get_node_df(self) -> pd.DataFrame:
        raise NotImplementedError('To be implemented')

    def get_nodes_overview(self) -> str:
        raise NotImplementedError('To be implemented')

    def load_nodes(self, surface_file: NexusFile, start_date: str, default_units: UnitSystem) -> None:
        new_nodes = load_nodes(surface_file, start_date, default_units)
        self.__nodes += new_nodes
