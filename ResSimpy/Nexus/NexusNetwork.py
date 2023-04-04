from dataclasses import dataclass

from ResSimpy.Nexus.DataModels.Surface.NexusNodeConnections import NexusNodeConnections
from ResSimpy.Nexus.DataModels.Surface.NexusNodes import NexusNodes


@dataclass(kw_only=True)
class NexusNetwork:
    nodes = NexusNodes()
    connections = NexusNodeConnections()


