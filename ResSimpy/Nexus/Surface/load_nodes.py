from typing import Sequence

from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.Surface.NexusNode import NexusNode
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
import ResSimpy.Nexus.nexus_file_operations as nfo


def load_node_table(file_as_list: list[str], current_date: str, unit_system: UnitSystem) -> Sequence[NexusNode]:
    list_of_nodes: list[NexusNode] = []
    header_index, headers = nfo.get_table_header(file_as_list, )
    return list_of_nodes


def load_nodes(surface_file: NexusFile, start_date: str, default_units: UnitSystem) -> Sequence[NexusNode]:
    current_date = start_date
    keyword_map = NexusNode.get_node_nexus_mapping()
    nexus_nodes_list = []
    file_as_list = surface_file.get_flat_list_str_file()
    node_start = -1
    node_end = -1
    unit_system = default_units
    for index, line in enumerate(file_as_list):
        property_dict = {}
        nfo.check_property_in_line(line, property_dict, file_as_list)
        unit_system = property_dict.get('UNIT_SYSTEM') if not None else default_units
        if nfo.check_token('TIME', line):
            current_date = nfo.get_expected_token_value(
                token='TIME', token_line=line, file_list=file_as_list,
                custom_message=f"Cannot find the date associated with the TIME card in {line=} at line number {index}")

        if nfo.check_token('NODES', line):
            node_start = index + 1
        if node_start > 0 and nfo.check_token('ENDNODES', line):
            node_end = index
        if 0 < node_start < node_end:
            node_table = load_node_table(file_as_list[node_start: node_end], current_date, unit_system)
            nexus_nodes_list.extend(node_table)
            node_start = -1
            node_end = -1
    return nexus_nodes_list
