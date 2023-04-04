from dataclasses import dataclass

from ResSimpy.Nexus.DataModels.Network.NexusNodeConnections import NexusNodeConnections
from ResSimpy.Nexus.DataModels.Network.NexusNodes import NexusNodes


@dataclass(kw_only=True)
class NexusNetwork:
    nodes = NexusNodes()
    connections = NexusNodeConnections()
