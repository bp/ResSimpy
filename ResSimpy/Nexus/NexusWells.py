from dataclasses import dataclass, field
from typing import Sequence, Optional, Literal

import pandas as pd

from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
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
        store_dictionaries = []
        for well in self.__wells:
            for completion in well.completions:
                completion_props: dict[str, None | float | int | str] = {
                    'well_name': well.well_name,
                    'units': well.units.name,
                    }
                completion_props.update(completion.to_dict())
                store_dictionaries.append(completion_props)
        df_store = pd.DataFrame(store_dictionaries)
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

    def get_wells_dates(self) -> set[str]:
        """Returns a set of the unique dates in the wellspec file over all wells"""
        set_dates: set[str] = set()
        for well in self.__wells:
            set_dates.update(set(well.dates_of_completions))

        return set_dates

    def modify_well(self, well_name: str, date: str, perforations_properties: list[NexusCompletion.InputDictionary],
                    how: Literal['add', 'remove'] = 'add', remove_all_that_match: bool = False,
                    write_to_file: bool = True, ) -> None:
        """ Modify the existing wells in memory using a dictionary of properties.

        Args:
            date (str): Date at which to modify the well
            well_name (str): name of the well to modify
            perforations_properties (list[InputDict]): a dictionary containing the properties to modify with the \
                attribute as keys and the values as the updated property value. If remove will remove perforation that \
                matches the values in the dictionary.
            how (Literal['add', 'remove']):
            remove_all_that_match (bool): If True will remove all wells that partially match the perforation_properties\
                provided. If False will remove perforation if only one matches, if several match throws a warning and \
                does not remove them.
            write_to_file (bool): If True writes directly to file. (Currently not in use)
        """
        well = self.get_well(well_name)
        if well is None:
            raise ValueError(f'No well named {well_name} found in simulator')
        for perf in perforations_properties:
            if how.upper() == 'ADD':
                well.add_completion(date=date, perforation_properties=perf)
            else:
                well.remove_completion(date=date, perforation_properties=perf,
                                       remove_all_that_match=remove_all_that_match)
