"""Holds the class for the NexusSolverParams which handles loading and storing of the series of \
NexusSolverParam data objects.
"""
from __future__ import annotations

from typing import Sequence, TYPE_CHECKING

from ResSimpy.Enums.TimeSteppingMethodEnum import TimeSteppingMethod
from ResSimpy.Nexus.DataModels.NexusSolverParameter import NexusSolverParameter
from ResSimpy.Nexus.NexusKeywords.runcontrol_keywords import (DT_KEYWORDS, SOLVER_SCOPE_KEYWORDS,
                                                              SOLVER_SCOPED_KEYWORDS, SOLVER_KEYWORDS,
                                                              IMPSTAB_KEYWORDS, GRIDSOLVER_KEYWORDS, SOLO_KEYWORDS,
                                                              TOLS_KEYWORDS, DCMAX_KEYWORDS, MAX_CHANGE_KEYWORDS)
from ResSimpy.DataModelBaseClasses.SolverParameter import SolverParameter
from ResSimpy.GenericContainerClasses.SolverParameters import SolverParameters
from ResSimpy.FileOperations import file_operations as fo

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator


class NexusSolverParameters(SolverParameters):
    def __init__(self, model: NexusSimulator) -> None:
        """NexusSolverParameters class constructor.

        Args:
            model (NexusSimulator): Originating NexusSimulator object.
            start_date (str): Start date of the simulation.
        """
        self.__solver_parameters: Sequence[NexusSolverParameter] | None = None
        self.__model = model
        self.file_content = ['']
        self.start_date = ''

    @property
    def solver_parameters(self) -> Sequence[SolverParameter]:
        """Returns a list of solver parameters (usually of type list).

        If solver parameters are not loaded 'self.load' will attempt to load them.
        If loading fails it will return a value error.
        """
        if self.__solver_parameters is None:
            self.load()
        if self.__solver_parameters is None:
            raise ValueError('No solver parameters found.')
        return self.__solver_parameters

    @solver_parameters.setter
    def solver_parameters(self, value: list[NexusSolverParameter]) -> None:
        """Sets solver parameters for this instance and returns none.

        Args:
            value(list[NexusSolverParameter]): list of solver parameters.
        """
        self.__solver_parameters = value

    def load(self) -> None:
        """Loads data from run control file and sets start date from the model."""
        if self.__model.model_files.runcontrol_file is None:
            raise ValueError('No runcontrol file found when trying to load solver parameters.')
        self.file_content = self.__model.model_files.runcontrol_file.get_flat_list_str_file
        self.start_date = self.__model.start_date

        read_in_solver_parameter: list[NexusSolverParameter] = []
        # read in the solver parameters from the runcontrol file

        current_solver_param_token = None
        current_date = self.start_date
        solver_parameter_for_timestep = NexusSolverParameter(date=self.start_date)
        current_solver_scope = 'ALL'
        solver_parameters_that_work_with_generic_function = {
            'DT': DT_KEYWORDS,
            'GRIDSOLVER': GRIDSOLVER_KEYWORDS,
            'TOLS': TOLS_KEYWORDS,
        }
        solver_parameters_that_work_with_generic_function.update({key: DCMAX_KEYWORDS for key in MAX_CHANGE_KEYWORDS})

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

            # see if we get any SOLVER blocks
            if fo.check_token(token='SOLVER', line=line):
                current_solver_param_token = 'SOLVER'
                solver_token_value = fo.get_expected_token_value('SOLVER', line, file_list=self.file_content)
                solver_parameter_for_timestep = (
                    self.__get_solver_token_values(solver_token_value, line, solver_parameter_for_timestep))
                current_solver_scope = solver_token_value

            if current_solver_param_token == 'SOLVER' and not fo.check_token(token='SOLVER', line=line):
                solver_parameter_for_timestep = self.__set_solver_parameters(current_solver_scope, line,
                                                                             solver_parameter_for_timestep)

            if fo.check_token(token='METHOD', line=line):
                timestep_method = fo.get_expected_token_value('METHOD', line, file_list=self.file_content)
                # convert the string to the enum
                if timestep_method.lower() == 'implicit':
                    timestep_method_enum = TimeSteppingMethod.implicit
                else:
                    timestep_method_enum = TimeSteppingMethod.impes
                # set the timestepping_method in the object
                solver_parameter_for_timestep.timestepping_method = timestep_method_enum

            if fo.check_token(token='IMPLICITMBAL', line=line):
                solver_parameter_for_timestep.implicit_mbal = fo.get_expected_token_value('IMPLICITMBAL', line,
                                                                                          file_list=self.file_content)

            if fo.check_token(token='IMPSTAB', line=line):
                current_solver_param_token = 'IMPSTAB'
                impstab_token_value = fo.get_token_value('IMPSTAB', line, file_list=self.file_content)
                if impstab_token_value is not None:
                    solver_parameter_for_timestep.impstab_on = impstab_token_value.upper() == 'ON'

            if current_solver_param_token == 'IMPSTAB' and not fo.check_token(token='IMPSTAB', line=line):
                next_value = fo.get_next_value(0, file_as_list=[line])
                if next_value is not None and next_value in IMPSTAB_KEYWORDS:
                    solver_parameter_for_timestep = self.__get_impstab_token_values(next_value, line,
                                                                                    solver_parameter_for_timestep)

            for possible_solver_param_tokens in solver_parameters_that_work_with_generic_function:
                if fo.check_token(token=possible_solver_param_tokens, line=line):
                    current_solver_param_token = possible_solver_param_tokens
                    grid_solver_method = fo.get_expected_token_value(current_solver_param_token, line, file_list=[line])
                    solver_parameter_for_timestep = (
                        self.__get_generic_solver_token_values(grid_solver_method, line, solver_parameter_for_timestep,
                                                               current_solver_param_token))

            if (current_solver_param_token in solver_parameters_that_work_with_generic_function and
                    not fo.check_token(token=current_solver_param_token, line=line)):
                next_value = fo.get_next_value(0, file_as_list=[line])
                valid_keywords = solver_parameters_that_work_with_generic_function[current_solver_param_token]
                if next_value is not None and next_value.upper() in valid_keywords:
                    solver_parameter_for_timestep = (
                        self.__get_generic_solver_token_values(next_value, line, solver_parameter_for_timestep,
                                                               current_solver_param_token))
            if fo.check_token(token='PERFREV', line=line):
                solver_parameter_for_timestep.perfrev = fo.get_expected_token_value('PERFREV', line,
                                                                                    file_list=self.file_content)

            for keyword in SOLO_KEYWORDS:
                if fo.check_token(token=keyword, line=line):
                    self.__get_generic_solver_token_values(keyword, line, solver_parameter_for_timestep,
                                                           'SOLO')

        read_in_solver_parameter.append(solver_parameter_for_timestep)

        # finally assign the read in solver parameters to the class variable
        self.__solver_parameters = read_in_solver_parameter

    def __set_solver_parameters(self, current_solver_scope: str, line: str,
                                solver_parameter_for_timestep: NexusSolverParameter) -> NexusSolverParameter:
        """Sets the solver parameters for the SOLVER keyword in the NexusSolverParameter object."""
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
        if type_assignment is bool:
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

    def __get_impstab_token_values(self, token_value: str, line: str,
                                   solver_parameter_for_timestep: NexusSolverParameter) -> NexusSolverParameter:
        keyword_mapping = NexusSolverParameter.impstab_keyword_mapping()
        attribute_value, type_assignment = keyword_mapping[token_value.upper()]

        match token_value:
            case 'USEMASSCFL':
                value = ''
            case 'COATS':
                value = 'COATS'
            case 'PEACEMAN':
                value = 'PEACEMAN'
            case _:
                value = fo.get_expected_token_value(token_value, line, file_list=self.file_content)

        solver_parameter_for_timestep.__setattr__(attribute_value, type_assignment(value))
        return solver_parameter_for_timestep

    def __get_generic_solver_token_values(self, next_token: str, line: str,
                                          solver_parameter_for_timestep: NexusSolverParameter,
                                          current_solver_param_token: str
                                          ) -> NexusSolverParameter:
        """Get the values for the generic KEYWORD VALUE format when following a token like DT, TOLS, GRIDSOLVER, etc."""
        # get the keyword mapping for the current solver parameter section
        if current_solver_param_token in MAX_CHANGE_KEYWORDS:
            attribute_value, type_assignment = (
                NexusSolverParameter.get_max_change_attribute_name(keyword=current_solver_param_token,
                                                                   value=next_token))
        else:
            keyword_mapping = self.__get_keyword_mapping_for_current_solver_param(current_solver_param_token)
            # get the ressimpy attribute name
            attribute_value, type_assignment = keyword_mapping[next_token.upper()]

        value = fo.get_expected_token_value(next_token, line, file_list=self.file_content)
        # add the value to the solver_parameter_for_timestep object
        solver_parameter_for_timestep.__setattr__(attribute_value, type_assignment(value))
        return solver_parameter_for_timestep

    def __get_keyword_mapping_for_current_solver_param(self, current_solver_param_token: str) -> (
            dict)[str, tuple[str, type]]:
        """Get the keyword mapping for the current solver parameter section."""
        solver_param_to_keyword_mapping = {'DT': NexusSolverParameter.dt_keyword_mapping(),
                                           'SOLVER': NexusSolverParameter.solver_keyword_mapping(),
                                           'IMPSTAB': NexusSolverParameter.impstab_keyword_mapping(),
                                           'GRIDSOLVER': NexusSolverParameter.gridsolver_keyword_mapping(),
                                           'SOLO': NexusSolverParameter.solo_keyword_mapping(),
                                           'TOLS': NexusSolverParameter.tols_keyword_mapping(),
                                           }
        keyword_mapping = solver_param_to_keyword_mapping[current_solver_param_token]
        return keyword_mapping
