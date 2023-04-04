from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnections import NexusNodeConnections
from ResSimpy.Nexus.DataModels.Network.NexusNodes import NexusNodes
import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator


@dataclass(kw_only=True)
class NexusNetwork:
    model: NexusSimulator
    Nodes: NexusNodes = NexusNodes()
    Connections: NexusNodeConnections = NexusNodeConnections()

    def get_surface_file(self, method_number: Optional[int] = None) -> Optional[dict[int, NexusFile] | NexusFile]:
        """ gets a specific surface file object or a dictionary of surface files keyed by method number

        Args:
            method_number (int): Method number for selection of a specific surface file.
                If None then returns a dictionary of method, surface file object

        Returns:
            Optional[dict[int, NexusFile] | NexusFile]: returns a specific surface file object or a dictionary of \
                surface files keyed by method number
        """
        if method_number is None:
            return self.model.fcs_file.surface_files
        if self.model.fcs_file.surface_files is None:
            return None
        return self.model.fcs_file.surface_files.get(method_number)

    def load(self):
        """ Loads all the objects from the surface files in the Simulator class.
        """
        for surface in self.model.fcs_file.surface_files.values():
            nexus_obj_dict = nfo.collect_all_tables_to_objects(
                surface, {'NODECON': NexusNodeConnection,
                          'NODES': NexusNode,
                          },
                start_date=self.model.start_date,
                default_units=self.model.get_default_units())
            self.Nodes.add_nodes(nexus_obj_dict.get('NODES'))
            self.Connections.add_connections(nexus_obj_dict.get('NODECON'))
