"""Holds the class for the NexusSolverParams which handles loading and storing of the series of
NexusSolverParam data objects.
"""
from typing import Sequence

from ResSimpy.Enums.TimeSteppingMethodEnum import TimeSteppingMethod
from ResSimpy.Nexus.DataModels.NexusSolverParameter import NexusSolverParameter
from ResSimpy.Nexus.NexusKeywords.runcontrol_keywords import DT_KEYWORDS
from ResSimpy.SolverParameter import SolverParameter
from ResSimpy.SolverParameters import SolverParameters
from ResSimpy.FileOperations import file_operations as fo

class NexusSolverParameters(SolverParameters):
    def __init__(self, runcontrol_file: list[str], start_date: str ) -> None:
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

        timestep_method_enum = TimeSteppingMethod.impes
        current_solver_param_token = None
        current_date = self.start_date
        solver_parameter_for_timestep = NexusSolverParameter(date=self.start_date)
        for line in self.file_content:
            # maybe put a for loop in here for all the potential starting tokens?
            if fo.check_token(token='TIME', line=line):
                # append the existing solver parameter to the list
                if solver_parameter_for_timestep != NexusSolverParameter(date=current_date,
                                                                         timestepping_method=timestep_method_enum):
                    # prevent blank solver parameters from being added to the list
                    read_in_solver_parameter.append(solver_parameter_for_timestep)
                # create a new solver parameter object for the new time block
                current_date = fo.get_expected_token_value('TIME', line, file_list=self.file_content)
                solver_parameter_for_timestep = NexusSolverParameter(date=current_date)
                # reset the current_solver_param_token
                current_solver_param_token = None

            # see if we get any DT blocks
            if fo.check_token(token='DT', line=line):
                current_solver_param_token = 'DT'
                dt_token_value = fo.get_expected_token_value('DT', line, file_list=self.file_content)
                solver_parameter_for_timestep = (
                    self.__get_dt_token_values(dt_token_value, line, solver_parameter_for_timestep))

            if current_solver_param_token == 'DT' and not fo.check_token(token='DT', line=line):
                next_value = fo.get_next_value(0, file_as_list=[line])
                if next_value is not None and next_value in DT_KEYWORDS:
                    solver_parameter_for_timestep = (self.__get_dt_token_values(next_value, line,
                                                                                solver_parameter_for_timestep))

            if fo.check_token(token='METHOD', line=line):
                timestep_method = fo.get_expected_token_value('METHOD', line, file_list=self.file_content)
                # convert the string to the enum
                if timestep_method.lower() == 'implicit':
                    timestep_method_enum = TimeSteppingMethod.implicit
                else:
                    timestep_method_enum = TimeSteppingMethod.impes

            # set the timestepping_method in the object
            solver_parameter_for_timestep.timestepping_method = timestep_method_enum

        read_in_solver_parameter.append(solver_parameter_for_timestep)

        # finally assign the read in solver parameters to the class variable
        self.__solver_parameters = read_in_solver_parameter

    def __get_dt_token_values(self, dt_token_value: str, line: str,
                              solver_parameter_for_timestep: NexusSolverParameter) -> NexusSolverParameter:
        keyword_mapping = NexusSolverParameter.dt_keyword_mapping()
        attribute_value, type_assignment = keyword_mapping[dt_token_value.upper()]

        value = fo.get_expected_token_value(dt_token_value, line, file_list=self.file_content)

        solver_parameter_for_timestep.__setattr__(attribute_value, type_assignment(value))
        return solver_parameter_for_timestep
