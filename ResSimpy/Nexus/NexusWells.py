from dataclasses import dataclass, field
from typing import Sequence, Optional

import pandas as pd
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Wells import Wells
from ResSimpy.Nexus.load_wells import load_wells


@dataclass(kw_only=True)
class NexusWells(Wells):
    __wells: list[NexusWell] = field(default_factory=lambda: [])
    wellspec_paths: list[str] = field(default_factory=lambda: [])

    def get_wells(self) -> Sequence[NexusWell]:
        return self.__wells

    def get_well(self, well_name: str) -> Optional[NexusWell]:
        """Returns a specific well requested, or None if that well cannot be found"""
        wells_to_return = filter(lambda x: x.well_name.upper() == well_name.upper(), self.__wells)

        return next(wells_to_return, None)

    def get_wells_df(self) -> pd.DataFrame:
        # loop through wells and completions to output a table
        df_store = pd.DataFrame()
        for well in self.__wells:
            for completion in well.completions:
                completion_props: dict[str, None | float | int | str] = {'well_name': well.well_name,
                                                                         'units': well.units.name, }
                completion_props.update(completion.to_dict())
                df_row = pd.DataFrame(completion_props, index=[0])
                df_store = pd.concat([df_store, df_row], axis=0, ignore_index=True)
        df_store = df_store.dropna(axis=1, how='all')
        return df_store

    def load_wells(self, well_file: str, start_date: str, default_units: UnitSystem) -> None:
        new_wells = load_wells(wellspec_file_path=well_file, start_date=start_date, default_units=default_units)
        self.__wells += new_wells

    def get_wells_overview(self) -> str:
        overview: str = ''
        for well in self.__wells:
            overview += well.printable_well_info

        return overview
