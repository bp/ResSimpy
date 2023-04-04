from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnections import NexusNodeConnections
from ResSimpy.Nexus.DataModels.Network.NexusNodes import NexusNodes
import ResSimpy.Nexus.nexus_file_operations as nfo

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator


@dataclass(kw_only=True)
class NexusNetwork:
    model: NexusSimulator
    Nodes: NexusNodes = NexusNodes()
    Connections: NexusNodeConnections = NexusNodeConnections()

    def get_surface_file(self, method_number: Optional[int] = None):
        if method_number is None:
            return self.model.fcs_file.surface_files
        if self.model.fcs_file.surface_files is None:
            return None
        return self.model.fcs_file.surface_files[method_number]

    def load(self):
        for surface in self.model.fcs_file.surface_files.values():
            nexus_obj_dict = nfo.collect_all_tables_to_objects(
                surface, {'NODECON': NexusNodeConnection,
                          'NODES': NexusNode,
                          },
                start_date=self.model.start_date,
                default_units=self.model.get_default_units())
            self.Nodes.add_nodes(nexus_obj_dict.get('NODES'))
            self.Connections.add_connections(nexus_obj_dict.get('NODECON'))
