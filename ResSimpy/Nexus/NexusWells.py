from dataclasses import dataclass, field
from typing import Sequence, Optional

import pandas as pd

from ResSimpy.Enums.HowEnum import OperationEnum
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Wells import Wells
from ResSimpy.Nexus.load_wells import load_wells


@dataclass(kw_only=True)
class NexusWells(Wells):
    __wells: list[NexusWell] = field(default_factory=lambda: [])
    wellspec_files: list[NexusFile] = field(default_factory=lambda: [])

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

    def load_wells(self, well_file: NexusFile, start_date: str, default_units: UnitSystem) -> None:
        new_wells = load_wells(nexus_file=well_file, start_date=start_date, default_units=default_units)
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

    def modify_well(self, well_name: str, perforations_properties: list[NexusCompletion.InputDictionary],
                    how: OperationEnum = OperationEnum.ADD, remove_all_that_match: bool = False,
                    write_to_file: bool = True, ) -> None:
        """ Modify the existing wells in memory using a dictionary of properties.

        Args:
            well_name (str): name of the well to modify
            perforations_properties (list[InputDict]): a dictionary containing the properties to modify with the \
                attribute as keys and the values as the updated property value. If remove will remove perforation that \
                matches the values in the dictionary.
            how (OperationEnum): operation enum taking the values OperationEnum.ADD, OperationEnum.REMOVE. \
                Specifies how to modify the existing wells perforations.
            remove_all_that_match (bool): If True will remove all wells that partially match the completion_properties\
                provided. If False will remove perforation if only one matches, if several match throws a warning and \
                does not remove them.
            write_to_file (bool): If True writes directly to file. (Currently not in use)
        """
        well = self.get_well(well_name)
        if well is None:
            raise ValueError(f'No well named {well_name} found in simulator')
        for perf in perforations_properties:
            if how == OperationEnum.ADD:
                try:
                    date = perf.get('date')
                except AttributeError:
                    raise AttributeError(
                        f'No date provided in perf: {perf}, please provide a date to add the perforation at.')
                if date is None:
                    raise AttributeError(
                        f'No date provided in perf: {perf}, please provide a date to add the perforation at.')
                well.add_completion(date=date, completion_properties=perf)
            elif how == OperationEnum.REMOVE:
                completions_to_remove = well.find_completions(perf)
                well.remove_completions(completions_to_remove)
            elif how == OperationEnum.MODIFY:
                raise NotImplementedError('Modify in place not yet available. Please choose one of ADD/REMOVE')
            else:
                raise ValueError('Please select one of the valid OperationEnum values: e.g. OperationEnum.ADD')
