"""Holds the class for the NexusSolverParams which handles loading and storing of the series of
NexusSolverParam data objects.
"""
from typing import Sequence

from ResSimpy.Enums.TimeSteppingMethodEnum import TimeSteppingMethod
from ResSimpy.Nexus.DataModels.NexusSolverParameter import NexusSolverParameter
from ResSimpy.SolverParameter import SolverParameter
from ResSimpy.SolverParameters import SolverParameters
from ResSimpy.FileOperations import file_operations as fo

class NexusSolverParameters(SolverParameters):
    def __init__(self, runcontrol_file: list[str], start_date: str, ) -> None:
        """NexusSolverParameters class constructor.

        Args:
            runcontrol_file (list[str]): flattened file content as a list of strings from the run control.
            start_date (str): Start date of the simulation.
        """
        self.__solver_parameters: Sequence[NexusSolverParameter] | None = None
        self.start_date = start_date
        self.file_content = runcontrol_file

    @property
    def solver_parameters(self) -> Sequence[SolverParameter]:
        if self.__solver_parameters is None:
            self.load()
        if self.__solver_parameters is None:
            raise ValueError('No solver parameters found.')
        return self.__solver_parameters

    @solver_parameters.setter
    def solver_parameters(self, value: list[NexusSolverParameter]) -> None:
        self.__solver_parameters = value

    def load(self) -> None:
        read_in_solver_parameter: list[NexusSolverParameter] = []
        # read in the solver parameters from the runcontrol file

        dt_auto = None
        dt_min = None
        dt_max = None
        dt_max_increase = None
        timestep_method_enum = None
        current_solver_param_token = None
        for line in self.file_content:
            # refactor to a time blocked out section of the file.
            # maybe put a for loop in here for all the potential starting tokens?

            if fo.check_token(token='DT', line=line):
                current_solver_param_token = 'DT'
                dt_token_value = fo.get_expected_token_value('DT', line, file_list=self.file_content)
                dt_auto, dt_max, dt_max_increase, dt_min = (
                    self.__get_dt_token_values(dt_token_value, line, dt_auto, dt_max, dt_max_increase, dt_min))
            if current_solver_param_token == 'DT' and not fo.check_token(token='DT', line=line):
                next_value = fo.get_next_value(0, file_as_list=[line])
                if next_value is not None and next_value in ['AUTO', 'MIN', 'MAX', 'MAXINCREASE']:
                    dt_auto, dt_max, dt_max_increase, dt_min = (
                        self.__get_dt_token_values(next_value, line, dt_auto, dt_max, dt_max_increase, dt_min))

            if fo.check_token(token='METHOD', line=line):
                timestep_method = fo.get_expected_token_value('METHOD', line, file_list=self.file_content)
                # convert the string to the enum
                if timestep_method.lower() == 'implicit':
                    timestep_method_enum = TimeSteppingMethod.implicit
                else:
                    timestep_method_enum = TimeSteppingMethod.impes

        solver_param_for_timestep = NexusSolverParameter(date=self.start_date, timestepping_method=timestep_method_enum,
                                                         dt_auto=dt_auto, dt_min=dt_min, dt_max=dt_max,
                                                         dt_max_increase=dt_max_increase)
        read_in_solver_parameter.append(solver_param_for_timestep)

        # finally assign the read in solver parameters to the class variable
        self.__solver_parameters = read_in_solver_parameter

    def __get_dt_token_values(self, dt_token_value, line, dt_auto, dt_max, dt_max_increase, dt_min):
        # TODO think about the input/output data struct for these
        if dt_token_value == 'AUTO':
            dt_auto = float(fo.get_expected_token_value(dt_token_value, line, file_list=self.file_content))
        elif dt_token_value == 'MIN':
            dt_min = float(fo.get_expected_token_value(dt_token_value, line, file_list=self.file_content))
        elif dt_token_value == 'MAX':
            dt_max = float(fo.get_expected_token_value(dt_token_value, line, file_list=self.file_content))
        elif dt_token_value == 'MAXINCREASE':
            dt_max_increase = float(fo.get_expected_token_value(dt_token_value, line, file_list=self.file_content))
        return dt_auto, dt_max, dt_max_increase, dt_min
