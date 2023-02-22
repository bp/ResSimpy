from __future__ import annotations
from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from ResSimpy.Nexus.DataModels.NexusFile import NexusFile


# Factory methods for generating empty lists with typing
def get_empty_list_str() -> list[str]:
    value: list[str] = []
    return value


def get_empty_list_str_nexus_file() -> list[Union[str, NexusFile]]:
    value: list[Union[str, NexusFile]] = []
    return value


def get_empty_list_nexus_file() -> list[NexusFile]:
    value: list[NexusFile] = []
    return value
