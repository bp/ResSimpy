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
    _wells: Sequence[Well] = field(default_factory=list)
    _wells_loaded: bool = False

    def __init__(self, assume_loaded: bool = False) -> None:
        """Initialises the Wells class.

        Args:
            assume_loaded (bool): whether the class should assume that the Wells have already been loaded.
        """
        self._wells_loaded = assume_loaded
        self._wells = []

    @property
    def wells(self) -> Sequence[Well]:
        if not self._wells_loaded:
            self._load()
        return self._wells

    def _load(self) -> None:
        raise NotImplementedError("Implement this in the derived class")

    def get_all(self) -> Sequence[Well]:
        raise NotImplementedError("Implement this in the derived class")

    def get(self, well_name: str) -> Optional[Well]:
        raise NotImplementedError("Implement this in the derived class")

    def get_df(self) -> pd.DataFrame:
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

    def get_wells_overview(self) -> str:
        overview: str = ''
        for well in self.wells:
            overview += well.printable_well_info

        return overview

    def get_wells_dates(self) -> set[str]:
        """Returns a set of the unique dates in the wellspec file over all wells."""
        set_dates: set[str] = set()
        for well in self.wells:
            set_dates.update(set(well.dates_of_completions))

        return set_dates

    @property
    def table_header(self) -> str:
        raise NotImplementedError("Implement this in the derived class")

    @property
    def table_footer(self) -> str:
        raise NotImplementedError("Implement this in the derived class")
