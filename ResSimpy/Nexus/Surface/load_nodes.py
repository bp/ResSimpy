from typing import Sequence

from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.Surface.NexusNode import NexusNode
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem


def read_single_node(file_as_list: list[str]) -> NexusNode:
    pass


def load_nodes(surface_file: NexusFile, start_date, default_units: UnitSystem) -> Sequence[NexusNode]:
    pass
