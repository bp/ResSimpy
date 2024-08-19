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
        """Writes a list of well objects.

        Returns:
               A sequence ( usually of type List) of wells. If wells were not previously loaded,
               they will be loaded (using the _load before returning).
        """
        if not self._wells_loaded:
            self._load()
        return self._wells

    def _load(self) -> None:
        raise NotImplementedError("Implement this in the derived class")

    def get_all(self) -> Sequence[Well]:
        """Returns a sequence of wells usually of type list."""
        raise NotImplementedError("Implement this in the derived class")

    def get(self, well_name: str) -> Optional[Well]:
        """?

        Args:
            well_name (str): The well name.
        """
        raise NotImplementedError("Implement this in the derived class")

    def get_df(self) -> pd.DataFrame:
        """Returns a pandas data frame."""
        raise NotImplementedError("Implement this in the derived class")

    def modify(self, well_name: str, completion_properties_list: list[dict[str, None | float | int | str]],
               how: OperationEnum = OperationEnum.ADD) -> None:
        """?

        Args:
            well_name (str) : The well name
            completion_properties_list (list[dict[str, None | float | int | str]]) : ?
            how (OperationEnum) : ?

        Returns:
            None
        """
        raise NotImplementedError("Implement this in the derived class")

    def add_completion(self, well_name: str, completion_properties: dict[str, None | float | int | str],
                       preserve_previous_completions: bool = True, comments: Optional[str] = None) -> None:
        """Add the new completion.

        Args:
            well_name(str): The well name.
            completion_properties(dict[str, None | float | int | str]): Properties of the added completion.
            preserve_previous_completions():? .
            comments(Optional[str]): Comments about the added completion.

        Returns:
            None
        """
        raise NotImplementedError("Implement this in the derived class")

    def remove_completion(self, well_name: str,
                          completion_properties: Optional[dict[str, None | float | int | str]] = None,
                          completion_id: Optional[UUID] = None) -> None:
        """Removes completion.

        Args:
            well_name(str): Well name.
            completion_properties(Optional[dict[str, None | float | int | str]]): Completion properties.
            completion_id(Optional[UUID]): Completion unique identifier.

        Returns:
            None
        """
        raise NotImplementedError("Implement this in the derived class")

    def modify_completion(self, well_name: str, properties_to_modify: dict[str, None | float | int | str],
                          completion_to_change: Optional[dict[str, None | float | int | str]] = None,
                          completion_id: Optional[UUID] = None,
                          comments: Optional[str] = None) -> None:
        """Modifies the completion properties with the new values.

        Args:
            well_name (str): Well name.
            properties_to_modify(dict[str, None | float | int | str]): Well properties to be modified.
            completion_to_change(optional[dict[str, None | float | int | str]]): Completion that will be modified.
            completion_id(Optional[UUID]): Completion unique identifier.
            comments(Optional[str]): Comments about the modified completion.

        Returns:
            None
        """
        raise NotImplementedError("Implement this in the derived class")

    def get_wells_overview(self) -> str:
        """Returns well information as a string format and updates the overview variable."""
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
        """Returns table header as a string."""
        raise NotImplementedError("Implement this in the derived class")

    @property
    def table_footer(self) -> str:
        """Returns table footer as a string."""
        raise NotImplementedError("Implement this in the derived class")
