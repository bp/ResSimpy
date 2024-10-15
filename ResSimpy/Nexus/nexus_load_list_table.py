"""Functions for loading a well list from a surface network file."""
from typing import TypeVar, Type

from ResSimpy.DataModelBaseClasses.NetworkList import NetworkList
import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Enums.HowEnum import OperationEnum
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat

SubTypeNetworkList = TypeVar('SubTypeNetworkList', bound=NetworkList)


def load_table_to_lists(file_as_list: list[str], row_object: Type[SubTypeNetworkList], table_header: str,
                        current_date: None | str,
                        date_format: DateFormat, previous_lists: None | list[SubTypeNetworkList] = None,
                        table_start_index: int = 0) -> list[tuple[SubTypeNetworkList, int]]:
    """Loads a well list from a surface network file.

    Args:
        file_as_list (list[str]): The surface network file as a list of strings.
        row_object (NetworkList): The object to be loaded.
        table_header (str): The header of the table to read from.
        current_date (None | str): The current date of the simulation.
        date_format (Optional[DateFormat]): The date format of the objects being loaded.
        previous_lists (None | list[tuple[NexusWellList, int]]): /
        The list of tuples of already loaded in NetworkLists with their starting index. Defaults to None.
        table_start_index (int): The starting index of the table. Defaults to 0.

    Returns:
        NexusWellList: A NexusWellList object containing the well list data.
    """
    if previous_lists is None:
        previous_lists = []
    if current_date is None:
        current_date = ''
    list_name = ''
    for line in file_as_list:
        if nfo.check_token(table_header, line):
            list_name = nfo.get_expected_token_value(table_header, line, file_as_list)

    previous_list_object = get_previous_list(list_name=list_name, lists=previous_lists)

    new_list_object = load_list_from_table(table_as_list_str=file_as_list, current_date=current_date,
                                           previous_list_object=previous_list_object, list_name=list_name,
                                           date_format=date_format, row_object=row_object, table_header=table_header)

    return [(new_list_object, table_start_index)]


def get_previous_list(list_name: str, lists: list[SubTypeNetworkList]) -> SubTypeNetworkList | None:
    """Gets the previous network list from a list of well lists.

    Args:
        list_name (str): The name of the well list to get.
        lists (list[NetworkList]): The list of well lists to search.

    Returns:
        NetworkList | None: The previous well list if it exists, None otherwise.
    """

    # Find the latest matching welllist
    matching_lists = [x for x in lists if x.name == list_name]
    sorted_lists = sorted(matching_lists, key=lambda x: x.iso_date)
    return None if len(sorted_lists) == 0 else sorted_lists[-1]


def load_list_from_table(table_as_list_str: list[str], row_object: Type[SubTypeNetworkList], table_header: str,
                         current_date: str,
                         list_name: str, date_format: DateFormat,
                         previous_list_object: SubTypeNetworkList | None = None) -> SubTypeNetworkList:
    """Loads a well list from a table taken from a surface network file.

    Currently does not support Wildcards in welllists.

    Args:
        table_as_list_str (list[str]): The subsection of surface network file as a list of strings.
        row_object (NetworkList): The object to be loaded.
        table_header (str): The header of the table to read from.
        current_date (str): The current date of the simulation.
        list_name (str): The name of the well list.
        date_format (Optional[DateFormat]): The date format of the Welllist being loaded.
        previous_list_object (NexusWellList | None): The previous well list. Defaults to None.

    Returns:
        NexusWellList: A NexusWellList object containing the well list data.
    """
    store_list = previous_list_object.elements_in_the_list.copy() if previous_list_object is not None else []
    operation: OperationEnum | None = None
    for line in table_as_list_str:
        if nfo.check_token('CLEAR', line):
            # clear the existing welllist
            store_list = []
            continue

        if nfo.check_token('ADD', line):
            operation = OperationEnum.ADD
            continue
        elif nfo.check_token('REMOVE', line):
            operation = OperationEnum.REMOVE
            continue

        if operation is None:
            continue
        if nfo.check_token('END' + table_header, line):
            break

        # otherwise the well should be removed/added from/to the welllist.
        name = nfo.get_next_value(0, [line])
        if name is None:
            # handle the empty line case
            continue

        if operation == OperationEnum.ADD:
            store_list.append(name)
        elif operation == OperationEnum.REMOVE:
            if name in store_list:
                store_list.remove(name)

    # TODO may also need to store the line number for the loaded well list
    return row_object(name=list_name, elements_in_the_list=store_list, date=current_date,
                      date_format=date_format)
