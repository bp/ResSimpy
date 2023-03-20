from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Node import Node


@dataclass(kw_only=True)
class NexusNode(Node):
    x_pos: Optional[float] = None
    y_pos: Optional[float] = None
    number: Optional[int] = None
    temp: Optional[float] = None
    station: Optional[str] = None

    @staticmethod
    def get_node_nexus_mapping():
        """gets the mapping of nexus keywords to attribute definitions"""
        keywords = {
            'NAME': 'name',
            'TYPE': 'type',
            'DEPTH': 'depth',
            'X': 'x_pos',
            'Y': 'y_pos',
            'NUMBER': 'number',
            'TEMP': 'temp',
            'STATION': 'station',
        }