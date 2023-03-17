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
        pass

    def get_node(self, node_name: str) -> Optional[NexusNode]:
        pass

    def get_node_df(self) -> pd.DataFrame:
        pass

    def get_nodes_overview(self) -> str:
        pass

    def load_nodes(self, surface_file: NexusFile, start_date: str, default_units: UnitSystem) -> None:
        new_nodes = load_nodes(surface_file, )
        self.__nodes += new_nodes
