from dataclasses import dataclass, field

from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.UnitsEnum import Units
from ResSimpy.Wells import Wells
from ResSimpy.Nexus.load_wells import load_wells


@dataclass(kw_only=True)
class NexusWells(Wells):
    __wells: list[NexusWell] = field(default_factory=lambda: [])
    wellspec_paths: list[str] = field(default_factory=lambda: [])

    def get_wells(self):
        return self.__wells

    def get_wells_df(self):
        # TODO: implement this
        return self.__wells

    def load_wells(self, well_file: str, start_date: str, default_units: Units):
        new_wells = load_wells(wellspec_file_path=well_file, start_date=start_date, default_units=default_units)
        self.__wells += new_wells
