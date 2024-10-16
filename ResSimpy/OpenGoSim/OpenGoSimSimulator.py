from dataclasses import dataclass
from typing import Optional

import ResSimpy.FileOperations.file_operations as fo
from ResSimpy.DataModelBaseClasses.Aquifer import Aquifer
from ResSimpy.Enums.PenetrationDirectionEnum import PenetrationDirectionEnum
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Enums.WellTypeEnum import WellType
from ResSimpy.DataModelBaseClasses.Equilibration import Equilibration
from ResSimpy.FileOperations.File import File
from ResSimpy.DataModelBaseClasses.Gaslift import Gaslift
from ResSimpy.GenericContainerClasses.Hydraulics import Hydraulics
from ResSimpy.OpenGoSim.DataModels.OpenGoSimCompletion import OpenGoSimCompletion
from ResSimpy.OpenGoSim.DataModels.OpenGoSimWell import OpenGoSimWell
from ResSimpy.OpenGoSim.Enums.SimulationTypeEnum import SimulationType
from ResSimpy.OpenGoSim.Model_Parts.OpenGoSimNetwork import OpenGoSimNetwork
from ResSimpy.OpenGoSim.OpenGoSimKeywords.OpenGoSimKeywords import OPENGOSIM_KEYWORDS
from ResSimpy.OpenGoSim.OpenGoSimWells import OpenGoSimWells
from ResSimpy.DataModelBaseClasses.PVT import PVT
from ResSimpy.DataModelBaseClasses.RelPerm import RelPerm
from ResSimpy.DataModelBaseClasses.Reporting import Reporting
from ResSimpy.DataModelBaseClasses.Rock import Rock
from ResSimpy.DataModelBaseClasses.Separator import Separator
from ResSimpy.DataModelBaseClasses.Simulator import Simulator
from ResSimpy.DataModelBaseClasses.Valve import Valve
from ResSimpy.DataModelBaseClasses.Water import Water


def line_contains_block_ending(line: str) -> bool:
    """Checks if a line contains a block ending or not."""
    if '/' in line or fo.check_token('END', line):
        return True
    return False


@dataclass(kw_only=True)
class OpenGoSimSimulator(Simulator):
    __simulation_type: SimulationType
    __final_date: Optional[str]

    def __init__(self, origin: str) -> None:
        """Initialises the OpenGoSimSimulator class.

        Args:
            origin (str): The path to the model file.
        """
        super().__init__()
        self._origin = origin
        self._wells: OpenGoSimWells = OpenGoSimWells()

        self.__final_date = None

        # Model parts not implemented yet. Will be replaced by OGS specific classes
        self._pvt = PVT()
        self._separator = Separator()
        self._water = Water()
        self._equil = Equilibration()
        self._rock = Rock()
        self._relperm = RelPerm()
        self._valve = Valve()
        self._aquifer = Aquifer()
        self._hydraulics = Hydraulics()
        self._gaslift = Gaslift()
        self._network = OpenGoSimNetwork()
        self._grid = None
        self._model_files = File(location=origin)
        self._default_units = UnitSystem.UNDEFINED
        self._reporting = Reporting(self)
        self.__load_model()

    @property
    def simulation_type(self) -> SimulationType:
        """Returns an instance of OpenGoSim simulation type."""
        return self.__simulation_type

    @property
    def final_date(self) -> Optional[str]:
        """Returns final date in the simulator."""
        return self.__final_date

    @staticmethod
    def sim_default_unit_system() -> UnitSystem:
        """Returns the default unit system used by the Simulator."""
        return UnitSystem.METRIC

    def __repr__(self) -> str:
        full_string = f"""Simulation Type {self.simulation_type.value}
Start Date: {self.start_date}
End Date: {self.final_date}

WELLS
-----
{self.wells.get_wells_overview()}
"""
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

    def __load_in_time_block(self, remaining_text: list[str]) -> None:
        # Load in the TIME block of the model.
        for index, line in enumerate(remaining_text):
            if line_contains_block_ending(line):
                break
            if fo.check_token('START_DATE', line):
                self._start_date = fo.load_in_three_part_date(initial_token='START_DATE', token_line=line,
                                                              file_as_list=remaining_text, start_index=index)

            if fo.check_token('FINAL_DATE', line):
                self.__final_date = fo.load_in_three_part_date(initial_token='FINAL_DATE', token_line=line,
                                                               file_as_list=remaining_text, start_index=index)

    def __load_in_simulation_block(self, remaining_text: list[str]) -> None:
        # Load in the SIMULATION block of the model.
        for line in remaining_text:
            if line_contains_block_ending(line):
                break
            if fo.check_token('SIMULATION_TYPE', line):
                value = fo.get_expected_token_value(token='SIMULATION_TYPE', token_line=line, file_list=remaining_text)
                self.__simulation_type = SimulationType.SUBSURFACE if value.upper() == 'SUBSURFACE' \
                    else SimulationType.GEOMECHANICS_SUBSURFACE

    def __load_in_well_data_block(self, remaining_text: list[str]) -> None:
        # Load in the WELL_DATA block of the model.
        completions_to_add: list[OpenGoSimCompletion] = []
        unique_completions: list[OpenGoSimCompletion] = []
        well_name: str = fo.get_expected_token_value(token='WELL_DATA',
                                                     token_line=remaining_text[0],
                                                     file_list=remaining_text)
        well_type: WellType | None = None
        relevant_date = self.start_date
        open_status = True
        penetration_direction = PenetrationDirectionEnum.Z
        refinement_name = None
        for index, line in enumerate(remaining_text):
            if line_contains_block_ending(line):
                break
            if fo.check_token('WELL_TYPE', line):
                value = fo.get_expected_token_value(token='WELL_TYPE', token_line=line, file_list=remaining_text)
                well_type = WellType[value.upper()]
            if fo.check_token('DATE', line):
                relevant_date = fo.load_in_three_part_date(initial_token='DATE', token_line=line,
                                                           file_as_list=remaining_text, start_index=index)

                new_completions_to_add: list[OpenGoSimCompletion] = []

                # Make a copy of each existing completion for the new date
                for unique_completion in unique_completions:
                    new_completion = OpenGoSimCompletion(i=unique_completion.i, j=unique_completion.j,
                                                         k=unique_completion.k, date=relevant_date,
                                                         penetration_direction=unique_completion.penetration_direction,
                                                         is_open=open_status, refinement_name=refinement_name)
                    new_completions_to_add.append(new_completion)
                completions_to_add.extend(new_completions_to_add)
            if fo.check_token('OPEN', line):
                # Apply 'open' state to all previous completions on this date
                for completion in completions_to_add:
                    if completion.date == relevant_date:
                        completion.is_open_set(True)
            if fo.check_token('SHUT', line):
                # Apply 'shut' state to all previous completions on this date
                for completion in completions_to_add:
                    if completion.date == relevant_date:
                        completion.is_open_set(False)
            if fo.check_token('CIJK_D', line) or fo.check_token('CIJKL_D', line):
                # Load in the completions
                remaining_text_from_here = remaining_text[index:]

                values_in_order = fo.get_multiple_expected_sequential_values(list_of_strings=remaining_text_from_here,
                                                                             number_tokens=4,
                                                                             ignore_values=['CIJK_D', 'CIJKL_D'])

                i_value = values_in_order[0]
                j_value = values_in_order[1]
                k_1 = values_in_order[2]
                k_2 = values_in_order[3]

                # Get the refinement name and / or penetration direction
                next_value = fo.get_nth_value(list_of_strings=remaining_text_from_here, value_number=5,
                                              ignore_values=['CIJK_D', 'CIJKL_D'])

                if fo.check_token('CIJKL_D', line):
                    # Completion is in grid refinement, get the name of that refinement first
                    refinement_name = next_value
                    next_value = fo.get_nth_value(list_of_strings=remaining_text_from_here, value_number=6,
                                                  ignore_values=['CIJKL_D'])

                # The next value, if present, will be the penetration direction.
                if next_value is not None and next_value.upper() not in OPENGOSIM_KEYWORDS:
                    penetration_direction = PenetrationDirectionEnum[next_value]

                # Create a new completion for every layer found, and add it to the well
                for c in range(int(k_1), int(k_2) + 1):
                    new_completion_to_add = OpenGoSimCompletion(i=int(i_value), j=int(j_value), k=c, date=relevant_date,
                                                                penetration_direction=penetration_direction,
                                                                refinement_name=refinement_name, is_open=open_status)
                    completions_to_add.append(new_completion_to_add)

                unique_completions = completions_to_add.copy()

        if well_type is None:
            raise ValueError(f"Cannot determine well type for well {well_name}")

        loaded_well = OpenGoSimWell(well_type=well_type, well_name=well_name, completions=completions_to_add)

        self._wells._wells.append(loaded_well)
        self._wells._wells_loaded = True

    @staticmethod
    def get_fluid_type(surface_file_content: list[str]) -> str:
        """Returns fluid type for single model from surface file.

        Args:
            surface_file_content(list[str]): List of strings with a new line per entry from surface file.
        """
        raise NotImplementedError("Not implemented for OGS yet")

    def set_output_path(self, path: str) -> None:
        """Initialises the output to the declares output location (path).

        Args:
            path(str): File location.
        """
        raise NotImplementedError("Not implemented for OGS yet")

    def get_date_format(self) -> str:
        """Returns date format as a string."""
        raise NotImplementedError("Not implemented for OGS yet")

    def write_out_new_model(self, new_location: str, new_model_name: str) -> None:
        """Writes out a new version of the model to the location supplied.

        Args:
            new_location (str): Path to write the contents of the model to.
            new_model_name (str): The name for the model that will be created.
        """
        raise NotImplementedError("Not implemented for OGS yet")
