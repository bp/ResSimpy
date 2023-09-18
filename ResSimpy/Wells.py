from __future__ import annotations
from dataclasses import dataclass, field
from abc import ABC
from uuid import UUID

import pandas as pd
from ResSimpy.Enums.HowEnum import OperationEnum

from ResSimpy.Well import Well
from typing import Sequence, Optional


@dataclass(kw_only=True)
class Wells(ABC):
    __wells: list[Well] = field(default_factory=list)

    @property
    def wells(self):
        return self.__wells

    @wells.setter
    def wells(self, value):
        self.__wells = value

    def get_all(self) -> Sequence[Well]:
        raise NotImplementedError("Implement this in the derived class")

    def get(self, well_name: str) -> Optional[Well]:
        raise NotImplementedError("Implement this in the derived class")

    def get_df(self) -> pd.DataFrame:
        raise NotImplementedError("Implement this in the derived class")

    def get_wells_overview(self) -> str:
        raise NotImplementedError("Implement this in the derived class")

    def modify(self, well_name: str, completion_properties_list: list[dict[str, None | float | int | str]],
               how: OperationEnum = OperationEnum.ADD) -> None:
        raise NotImplementedError("Implement this in the derived class")

    def add_completion(self, well_name: str, completion_properties: dict[str, None | float | int | str],
                       preserve_previous_completions: bool = True, comments: Optional[str] = None) -> None:
        raise NotImplementedError("Implement this in the derived class")

    def remove_completion(self, well_name: str,
                          completion_properties: Optional[dict[str, None | float | int | str]] = None,
                          completion_id: Optional[UUID] = None) -> None:
        raise NotImplementedError("Implement this in the derived class")

    def modify_completion(self, well_name: str, properties_to_modify: dict[str, None | float | int | str],
                          completion_to_change: Optional[dict[str, None | float | int | str]] = None,
                          completion_id: Optional[UUID] = None,
                          comments: Optional[str] = None) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @property
    def table_header(self) -> str:
        raise NotImplementedError("Implement this in the derived class")

    @property
    def table_footer(self) -> str:
        raise NotImplementedError("Implement this in the derived class")
