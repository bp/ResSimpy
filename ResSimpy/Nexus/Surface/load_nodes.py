from typing import Sequence, Type

from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.Surface.NexusNode import NexusNode
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
import ResSimpy.Nexus.nexus_file_operations as nfo


def load_nodes(surface_file: NexusFile, start_date: str, default_units: UnitSystem) -> Sequence[NexusNode]:
    """ Loads all nodes from a given surface file.

    Args:
        surface_file (NexusFile): NexusFile representation of the surface file.
        start_date (str): Starting date of the run
        default_units (UnitSystem): Units used in case not specified by surface file.
    Raises:
        TypeError: if the unit system found in the property check is not a valid enum UnitSystem
    Returns:
        Sequence[NexusNode]: a list of NexusNodes from the surface_file provided
    """
    current_date = start_date
    nexus_nodes_list: list[NexusNode] = []
    file_as_list = surface_file.get_flat_list_str_file()
    node_map = NexusNode.get_nexus_mapping()
    node_start = -1
    node_end = -1
    property_dict: dict = {}
    for index, line in enumerate(file_as_list):
        # check for changes in unit system
        nfo.check_property_in_line(line, property_dict, file_as_list)
        unit_system = property_dict.get('UNIT_SYSTEM', default_units)
        if not isinstance(unit_system, UnitSystem):
            raise TypeError(f"Value found for {unit_system=} of type {type(unit_system)} \
                            not compatible, expected type UnitSystem Enum")
        if nfo.check_token('TIME', line):
            current_date = nfo.get_expected_token_value(
                token='TIME', token_line=line, file_list=file_as_list,
                custom_message=f"Cannot find the date associated with the TIME card in {line=} at line number {index}")

        if nfo.check_token('NODES', line):
            node_start = index + 1
        if node_start > 0 and nfo.check_token('ENDNODES', line):
            node_end = index
        if 0 < node_start < node_end:
            node_table = nfo.load_table_to_objects(file_as_list=file_as_list, row_object=NexusNode,
                                                   property_map=node_map, current_date=current_date,
                                                   unit_system=unit_system)
            nexus_nodes_list.extend(node_table)
            # reset indices for further tables
            node_start = -1
            node_end = -1
    return nexus_nodes_list
