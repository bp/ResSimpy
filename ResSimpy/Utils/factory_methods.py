from typing import Union
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile


def get_empty_list_str() -> list[str]:
    value: list[str] = []
    return value


def get_empty_list_str_nexus_file() -> list[Union[str, 'NexusFile']]:
    value: list[Union[str, 'NexusFile']] = []
    return value


def get_empty_list_nexus_file() -> list['NexusFile']:
    value: list['NexusFile'] = []
    return value
