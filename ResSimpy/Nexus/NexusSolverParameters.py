"""Holds the class for the NexusSolverParams which handles loading and storing of the series of
NexusSolverParam data objects.
"""
from typing import Sequence

from ResSimpy.Enums.TimeSteppingMethodEnum import TimeSteppingMethod
from ResSimpy.Nexus.DataModels.NexusSolverParameter import NexusSolverParameter
from ResSimpy.Nexus.NexusKeywords.runcontrol_keywords import (DT_KEYWORDS, SOLVER_SCOPE_KEYWORDS,
                                                              SOLVER_SCOPED_KEYWORDS, SOLVER_KEYWORDS)
from ResSimpy.SolverParameter import SolverParameter
from ResSimpy.SolverParameters import SolverParameters
from ResSimpy.FileOperations import file_operations as fo


class NexusSolverParameters(SolverParameters):
    def __init__(self, runcontrol_file: list[str], start_date: str) -> None:
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

        timestep_method_enum = None
        current_solver_param_token = None
        current_date = self.start_date
        solver_parameter_for_timestep = NexusSolverParameter(date=self.start_date)
        current_solver_scope = 'ALL'

        for line in self.file_content:
            # maybe put a for loop in here for all the potential starting tokens?
            if fo.check_token(token='TIME', line=line):
                # append the existing solver parameter to the list
                if solver_parameter_for_timestep != NexusSolverParameter(date=current_date):
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

            # see if we get any SOLVER blocks
            if fo.check_token(token='SOLVER', line=line):
                current_solver_param_token = 'SOLVER'
                solver_token_value = fo.get_expected_token_value('SOLVER', line, file_list=self.file_content)
                solver_parameter_for_timestep = (
                    self.__get_solver_token_values(solver_token_value, line, solver_parameter_for_timestep))
                current_solver_scope = solver_token_value

            if current_solver_param_token == 'SOLVER' and not fo.check_token(token='SOLVER', line=line):
                next_value = fo.get_next_value(0, file_as_list=[line])
                next_value = next_value.upper() if next_value is not None else None
                if next_value in SOLVER_SCOPE_KEYWORDS:
                    current_solver_scope = next_value
                    # get the value of the next token and assign it to the solver_parameter_for_timestep object
                    solver_scoped_keyword = fo.get_expected_token_value(next_value, line, file_list=self.file_content)
                    attribute_value, type_assignment = self.__get_solver_attribute_value(
                        current_solver_scope, solver_scoped_keyword)
                    value = fo.get_token_value(solver_scoped_keyword, line, file_list=[line])
                    if value is not None:
                        solver_parameter_for_timestep.__setattr__(attribute_value, type_assignment(value))
                    else:
                        # cover for the fact that it may not have a next value
                        solver_parameter_for_timestep.__setattr__(attribute_value,
                                                                  type_assignment(solver_scoped_keyword))

                elif next_value in ['ITERATIVE', 'DIRECT']:
                    attribute_value, type_assignment = self.__get_solver_attribute_value(
                        current_solver_scope, next_value)
                    solver_parameter_for_timestep.__setattr__(attribute_value, type_assignment(next_value))

                elif next_value in SOLVER_SCOPED_KEYWORDS:
                    # if the first value we find is in the SOLVER_SCOPED_KEYWORDS, then we have a keyword that is
                    # not a token, but a value referring to a scope. So we can directly get the value and assign it
                    # to the solver_parameter_for_timestep object.
                    attribute_value, type_assignment = self.__get_solver_attribute_value(
                        current_solver_scope, next_value)
                    value = fo.get_token_value(next_value, line, file_list=self.file_content)
                    solver_parameter_for_timestep.__setattr__(attribute_value, type_assignment(value))

                elif next_value in ['NOCUT', 'CUT']:
                    solver_parameter_for_timestep.solver_timestep_cut = next_value == 'CUT'
                elif next_value in ['PRECON_ILU', 'PRECON_AMG', 'PRECON_AMG_RS']:
                    solver_parameter_for_timestep.solver_precon = next_value
                    precon_setting = fo.get_token_value(next_value, line, file_list=[line])
                    if precon_setting is not None:
                        precon_value_num = fo.get_expected_token_value(precon_setting, line,
                                                                       file_list=self.file_content)
                        solver_parameter_for_timestep.solver_precon_value = float(precon_value_num)
                        solver_parameter_for_timestep.solver_precon_setting = precon_setting
                elif next_value in SOLVER_KEYWORDS:
                    solver_parameter_for_timestep = self.__get_solver_token_values(next_value,
                                                                                   line, solver_parameter_for_timestep)

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

    def __get_solver_token_values(self, solver_token_value: str, line: str,
                                  solver_parameter_for_timestep: NexusSolverParameter) -> NexusSolverParameter:
        """Get the values for the SOLVER KEYWORD VALUE format."""
        solver_token_value = solver_token_value.upper()
        keyword_mapping = NexusSolverParameter.solver_keyword_mapping()

        # get the attribute value and type assignment
        if solver_token_value in SOLVER_SCOPE_KEYWORDS:
            property_set = fo.get_expected_token_value(solver_token_value, line, file_list=[line])
            attribute_value, type_assignment = self.__get_solver_attribute_value(solver_token_value, property_set)
            value = fo.get_expected_token_value(property_set, line, file_list=self.file_content)

        else:
            attribute_value, type_assignment = keyword_mapping[solver_token_value]
            value = fo.get_expected_token_value(solver_token_value, line, file_list=self.file_content)
        if type_assignment == bool:
            # set to True if the value is 'ON' and False if the value is 'OFF' (the bool conversion happens
            # by type_assignment)
            value = '' if value.upper() == 'OFF' else value
        solver_parameter_for_timestep.__setattr__(attribute_value, type_assignment(value))
        return solver_parameter_for_timestep

    @staticmethod
    def __get_solver_attribute_value(solver_scope: str, solver_scoped_keyword: str) -> tuple[str, type]:
        """Get the attribute value and type assignment for a solver keyword and a following value like CYCLELENGTH that
        has several mappings.
        """
        keyword_mapping = NexusSolverParameter.solver_keyword_mapping()
        lookup_attribute_value = solver_scope.upper() + ' ' + solver_scoped_keyword.upper()
        attribute_value, type_assignment = keyword_mapping[lookup_attribute_value]

        return attribute_value, type_assignment
