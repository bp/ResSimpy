from __future__ import annotations
from typing import TYPE_CHECKING, Union
import pandas as pd

if TYPE_CHECKING:
    from ResSimpy.Nexus.DataModels.NexusFile import NexusFile


# Factory methods for generating empty lists with typing
def get_empty_list_str() -> list[str]:
    value: list[str] = []
    return value


# Factory method for generating empty dictionary with typing
def get_empty_dict_union() -> dict[str, Union[str, int, float, pd.DataFrame, dict[str, pd.DataFrame]]]:
    value: dict[str, Union[str, int, float, pd.DataFrame, dict[str, pd.DataFrame]]] = {}
    return value


def get_empty_list_str_nexus_file() -> list[Union[str, NexusFile]]:
    value: list[Union[str, NexusFile]] = []
    return value


def get_empty_list_nexus_file() -> list[NexusFile]:
    value: list[NexusFile] = []
    return value


def get_empty_dict_nexus_file() -> dict[str, NexusFile]:
    value: dict[str, NexusFile] = {}
    return value
