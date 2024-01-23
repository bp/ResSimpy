"""Functions for loading a well list from a surface network file."""

from ResSimpy.Nexus.DataModels.NexusWellList import NexusWellList
import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Enums.HowEnum import OperationEnum


def load_well_lists(file_as_list: list[str], current_date: None | str,
                    previous_well_lists: None | list[NexusWellList] = None,
                    table_start_index: int = 0) -> list[tuple[NexusWellList, int]]:
    """Loads a well list from a surface network file.

    Args:
        file_as_list (list[str]): The surface network file as a list of strings.
        current_date (None | str): The current date of the simulation.
        previous_well_lists (None | list[tuple[NexusWellList, int]]):
        The list of tuples of already loaded in NexusWellLists with their starting index. Defaults to None.
        table_start_index (int): The starting index of the table. Defaults to 0.

    Returns:
        NexusWellList: A NexusWellList object containing the well list data.
    """
    if previous_well_lists is None:
        previous_well_lists = []
    if current_date is None:
        current_date = ''

    well_list_name = nfo.get_expected_token_value('WELLLIST', file_as_list[0], file_as_list)

    previous_well_list = get_previous_well_list(well_list_name=well_list_name, well_lists=previous_well_lists)

    new_well_list = load_well_list_from_table(well_list_as_list_str=file_as_list, current_date=current_date,
                                              previous_well_list=previous_well_list, well_list_name=well_list_name)

    return [(new_well_list, table_start_index)]


def get_previous_well_list(well_list_name: str, well_lists: list[NexusWellList]) -> NexusWellList | None:
    """Gets the previous well list from a list of well lists.

    Args:
        well_list_name (str): The name of the well list to get.
        well_lists (list[NexusWellList]): The list of well lists to search.

    Returns:
        NexusWellList | None: The previous well list if it exists, None otherwise.
    """
    for well_list in well_lists:
        if well_list.name == well_list_name:
            return well_list
    return None


def load_well_list_from_table(well_list_as_list_str: list[str], current_date: str, well_list_name: str,
                              previous_well_list: NexusWellList | None = None) -> NexusWellList:
    """Loads a well list from a table taken from a surface network file.
    Currently does not support Wildcards in welllists.

    Args:
        well_list_as_list_str (list[str]): The subsection of surface network file as a list of strings.
        current_date (str): The current date of the simulation.
        previous_well_list (NexusWellList | None): The previous well list. Defaults to None.

    Returns:
        NexusWellList: A NexusWellList object containing the well list data.
    """
    well_list = previous_well_list.wells.copy() if previous_well_list is not None else []
    operation: OperationEnum | None = None
    for line in well_list_as_list_str:
        if nfo.check_token('CLEAR', line):
            # clear the existing welllist
            well_list = []
            continue

        if nfo.check_token('ADD', line):
            operation = OperationEnum.ADD
            continue
        elif nfo.check_token('REMOVE', line):
            operation = OperationEnum.REMOVE
            continue

        if operation is None:
            continue
        if nfo.check_token('ENDWELLLIST', line):
            break

        # otherwise the well should be removed/added from/to the welllist.
        well_name = nfo.get_next_value(0, [line])
        if well_name is None:
            # handle the empty line case
            continue

        if operation == OperationEnum.ADD:
            well_list.append(well_name)
        elif operation == OperationEnum.REMOVE:
            if well_name in well_list:
                well_list.remove(well_name)

    # TODO may also need to store the line number for the loaded well list
    return NexusWellList(name=well_list_name, wells=well_list, date=current_date)
