from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusConstraints import NexusConstraints
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnections import NexusNodeConnections
from ResSimpy.Nexus.DataModels.Network.NexusNodes import NexusNodes
import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.DataModels.Network.NexusWellConnections import NexusWellConnections
from ResSimpy.Nexus.DataModels.Network.NexusWellbore import NexusWellbore
from ResSimpy.Nexus.DataModels.Network.NexusWellbores import NexusWellbores
from ResSimpy.Nexus.DataModels.Network.NexusWellhead import NexusWellhead
from ResSimpy.Nexus.DataModels.Network.NexusWellheads import NexusWellheads
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator


@dataclass(kw_only=True)
class NexusNetwork:
    model: NexusSimulator
    Nodes: NexusNodes
    Connections: NexusNodeConnections
    WellConnections: NexusWellConnections
    Wellheads: NexusWellheads
    Wellbores: NexusWellbores
    Constraints: NexusConstraints
    __has_been_loaded: bool = False

    def __init__(self, model: NexusSimulator):
        self.__has_been_loaded: bool = False
        self.model: NexusSimulator = model
        self.Nodes: NexusNodes = NexusNodes(self)
        self.Connections: NexusNodeConnections = NexusNodeConnections(self)
        self.WellConnections: NexusWellConnections = NexusWellConnections(self)
        self.Wellheads: NexusWellheads = NexusWellheads(self)
        self.Wellbores: NexusWellbores = NexusWellbores(self)
        self.Constraints: NexusConstraints = NexusConstraints(self)

    def get_load_status(self):
        if not self.__has_been_loaded:
            self.load()

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
                          'WELLS': NexusWellConnection,
                          'WELLHEAD': NexusWellhead,
                          'WELLBORE': NexusWellbore,
                          'CONSTRAINTS': NexusConstraint,
                          'CONSTRAINT': NexusConstraint,
                          'QMULT': NexusConstraint,
                          },
                start_date=self.model.start_date,
                default_units=self.model.default_units)
            self.Nodes.add_nodes(nexus_obj_dict.get('NODES'))
            self.Connections.add_connections(nexus_obj_dict.get('NODECON'))
            self.WellConnections.add_connections(nexus_obj_dict.get('WELLS'))
            self.Wellheads.add_wellheads(nexus_obj_dict.get('WELLHEAD'))
            self.Wellbores.add_wellbores(nexus_obj_dict.get('WELLBORE'))
            self.Constraints.add_constraints(nexus_obj_dict.get('CONSTRAINTS'))

        self.__has_been_loaded = True
