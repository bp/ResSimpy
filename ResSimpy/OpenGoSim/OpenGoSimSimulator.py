from dataclasses import dataclass
from typing import Sequence, Optional

from ResSimpy.Aquifer import Aquifer
from ResSimpy.Completion import Completion
from ResSimpy.Enums.PenetrationDirectionEnum import PenetrationDirectionEnum
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Enums.WellTypeEnum import WellType
from ResSimpy.Equilibration import Equilibration
from ResSimpy.File import File
from ResSimpy.Gaslift import Gaslift
from ResSimpy.Hydraulics import Hydraulics
from ResSimpy.Network import Network
from ResSimpy.OpenGoSim.DataModels.OpenGoSimCompletion import OpenGoSimCompletion
from ResSimpy.OpenGoSim.DataModels.OpenGoSimWell import OpenGoSimWell
from ResSimpy.OpenGoSim.Enums.SimulationTypeEnum import SimulationType
from ResSimpy.OpenGoSim.Model_Parts.OpenGoSimNetwork import OpenGoSimNetwork
from ResSimpy.OpenGoSim.OpenGoSimWells import OpenGoSimWells
from ResSimpy.PVT import PVT
from ResSimpy.RelPerm import RelPerm
from ResSimpy.Rock import Rock
from ResSimpy.Separator import Separator
from ResSimpy.Simulator import Simulator
import ResSimpy.FileOperations.file_operations as fo
from ResSimpy.Valve import Valve
from ResSimpy.Water import Water


@dataclass(kw_only=True)
class OpenGoSimSimulator(Simulator):
    __simulation_type: SimulationType
    __final_date: Optional[str]

    def __init__(self, origin: str) -> None:
        super().__init__()
        self._origin = origin
        self._wells: OpenGoSimWells = OpenGoSimWells()

        self.__final_date = None

        # Model parts not implemented yet. Will be replaced by OGS specific classes
        self._pvt=PVT()
        self._separator=Separator()
        self._water=Water()
        self._equil=Equilibration()
        self._rock=Rock()
        self._relperm=RelPerm()
        self._valve=Valve()
        self._aquifer=Aquifer()
        self._hydraulics=Hydraulics()
        self._gaslift=Gaslift()
        self._network=OpenGoSimNetwork()
        self._grid=None
        self._model_files=File(location=origin)

        self.__load_model()

    @property
    def simulation_type(self) -> SimulationType:
        return self.__simulation_type

    @property
    def final_date(self) -> Optional[str]:
        return self.__final_date

    def __repr__(self) -> str:
        full_string = f"""Simulation Type {self.simulation_type}"""
        return full_string

    def __load_model(self) -> None:
        """Loads the full OGS model."""
        block_tokens = ['SIMULATION', 'WELL_DATA', 'TIME']
        model_as_list = fo.load_file_as_list(self._origin)

        for index, line in enumerate(model_as_list):
            for token in block_tokens:
                if fo.check_token(token=token, line=line):
                    # Begin loading in the 'block' of information
                    if token.upper() == 'SIMULATION':
                        self.__load_in_simulation_block(model_as_list[index:])

                    if token.upper() == 'WELL_DATA':
                        self.__load_in_well_data_block(model_as_list[index:])

                    if token.upper() == 'TIME':
                        self.__load_in_time_block(model_as_list[index:])

    def __load_in_time_block(self, remaining_text: list[str]):
        # Load in the TIME block of the model.
        for index, line in enumerate(remaining_text):
            if fo.check_token('END', line):
                break
            if fo.check_token('START_DATE', line):
                self._start_date = fo.load_in_three_part_date(self, initial_token='START_DATE', token_line=line,
                                                              file_as_list=remaining_text, start_index=index)

            if fo.check_token('FINAL_DATE', line):
                value = fo.get_expected_token_value(token='FINAL_DATE', token_line=line, file_list=remaining_text)
                self.__final_date = fo.load_in_three_part_date(self, initial_token='FINAL_DATE', token_line=line,
                                                               file_as_list=remaining_text, start_index=index)

    def __load_in_simulation_block(self, remaining_text: list[str]):
        # Load in the SIMULATION block of the model.
        for line in remaining_text:
            if fo.check_token('END', line):
                break
            if fo.check_token('SIMULATION_TYPE', line):
                value = fo.get_expected_token_value(token='SIMULATION_TYPE', token_line=line, file_list=remaining_text)
                self.__simulation_type = SimulationType.SUBSURFACE if value.upper() == 'SUBSURFACE' \
                    else SimulationType.GEOMECHANICS_SUBSURFACE

    def __load_in_well_data_block(self, remaining_text: list[str]):
        # Load in the WELL_DATA block of the model.
        completions_to_add: list[Completion] = []
        well_name: str = fo.get_expected_token_value(token='WELL_DATA',
                                                     token_line=remaining_text[0],
                                                     file_list=remaining_text)
        well_type: WellType | None = None
        relevant_date = self.start_date
        for index, line in enumerate(remaining_text):
            if fo.check_token('END', line):
                break
            if fo.check_token('WELL_TYPE', line):
                value = fo.get_expected_token_value(token='WELL_TYPE', token_line=line, file_list=remaining_text)
                well_type = WellType[value.upper()]
            if fo.check_token('DATE', line):
                relevant_date = fo.load_in_three_part_date(self, initial_token='DATE', token_line=line,
                                                           file_as_list=remaining_text, start_index=index)
            if fo.check_token('CIJK_D', line) or fo.check_token('CIJKL_D', line):
                # Load in the completions
                snipped_string = line.replace('CIJK_D', '')
                snipped_string = snipped_string.replace('CIJKL_D', '')

                i_value = fo.get_next_value(start_line_index=index, file_as_list=remaining_text,
                                            search_string=snipped_string)

                snipped_string = snipped_string.replace(i_value, '', 1)

                j_value = fo.get_next_value(start_line_index=index, file_as_list=remaining_text,
                                            search_string=snipped_string)

                snipped_string = snipped_string.replace(j_value, '', 1)

                k_bottom_value = fo.get_next_value(start_line_index=index, file_as_list=remaining_text,
                                                   search_string=snipped_string)

                snipped_string = snipped_string.replace(k_bottom_value, '', 1)

                k_top_value = fo.get_next_value(start_line_index=index, file_as_list=remaining_text,
                                                search_string=snipped_string)

                snipped_string = snipped_string.replace(k_top_value, '', 1)

                pen_value = fo.get_next_value(start_line_index=index, file_as_list=remaining_text,
                                              search_string=snipped_string)

                penetration_direction = PenetrationDirectionEnum[pen_value] if pen_value is not None \
                    else PenetrationDirectionEnum.Z

                for c in range(int(k_bottom_value), int(k_top_value) + 1):
                    completion_to_add = OpenGoSimCompletion(i=int(i_value), j=int(j_value), k=c, date=relevant_date,
                                                            penetration_direction=penetration_direction)
                    completions_to_add.append(completion_to_add)

        if well_type is None:
            raise ValueError(f"Cannot determine well type for well {well_name}")

        loaded_well = OpenGoSimWell(well_type=well_type, well_name=well_name, completions=completions_to_add)

        self._wells._wells.append(loaded_well)
        self._wells._wells_loaded = True

    @staticmethod
    def get_fluid_type(surface_file_name: str) -> str:
        raise NotImplementedError("Not implemented for OGS yet")

    def set_output_path(self, path: str) -> None:
        raise NotImplementedError("Not implemented for OGS yet")

    def get_date_format(self) -> str:
        """Returns date format as a string."""
        raise NotImplementedError("Not implemented for OGS yet")

    def write_out_new_model(self, new_location: str, new_model_name: str) -> None:
        """Writes out a new version of the model to the location supplied.

        Args:
        new_location (str): Path to write the contents of the model to.
        """
        raise NotImplementedError("Not implemented for OGS yet")
