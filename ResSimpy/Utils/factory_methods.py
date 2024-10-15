from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING, Union
from uuid import UUID

import numpy as np
import pandas as pd

if TYPE_CHECKING:  # pragma: no cover
    from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
    from ResSimpy.Nexus.DataModels.NexusWaterMethod import NexusWaterParams
    from ResSimpy.FileOperations.File import File


# Factory methods for generating empty lists with typing
def get_empty_list_str() -> list[str]:
    value: list[str] = []
    return value


# Factory method for generating empty dictionary for dynamic property methods, with typing
def get_empty_dict_union() -> dict[str, Union[str, int, float, Enum, list[str], np.ndarray,
                                              pd.DataFrame, dict[str, Union[float, pd.DataFrame]]]]:
    value: dict[str, Union[str, int, float, Enum, list[str], np.ndarray, pd.DataFrame,
                           dict[str, Union[float, pd.DataFrame]]]] = {}
    return value


# Factory method for generating empty dictionary for eos options
def get_empty_eosopt_dict_union() -> \
        dict[str, Union[str, int, float, pd.DataFrame, list[str], dict[str, float], tuple[str, dict[str, float]], dict[
            str, pd.DataFrame]]]:
    value: dict[str, Union[
        str, int, float, pd.DataFrame, list[str], dict[str, float], tuple[str, dict[str, float]], dict[
            str, pd.DataFrame]]] = {}
    return value


# Factory method for generating empty dictionary for hysteresis parameters
def get_empty_hysteresis_dict() -> dict[str, Union[str, float, dict[str,
                                        Union[str, float, dict[str, Union[str, float]]]]]]:
    value: dict[str, Union[str, float, dict[str, Union[str, float, dict[str, Union[str, float]]]]]] = {}
    return value


def get_empty_list_str_nexus_file() -> list[Union[str, NexusFile]]:
    value: list[Union[str, NexusFile]] = []
    return value


def get_empty_list_file() -> list[File]:
    value: list[File] = []
    return value


def get_empty_list_nexus_file() -> list[NexusFile]:
    value: list[NexusFile] = []
    return value


def get_empty_dict_int_nexus_file() -> dict[int, NexusFile]:
    value: dict[int, NexusFile] = {}
    return value


def get_empty_dict_uuid_list_int() -> dict[UUID, list[int]]:
    value: dict[UUID, list[int]] = {}
    return value


def get_empty_list_nexus_water_params() -> list[NexusWaterParams]:
    value: list[NexusWaterParams] = []
    return value
