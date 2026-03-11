from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataModelBaseClasses.NetworkObject import NetworkObject
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusKeywords.proc_keywords import PREDEFINED_VARS, CONDITIONAL_KEYWORDS, NEXUS_ALL_PROC_FUNCS
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping


# set custom error message
class SetError(Exception):
    """A SetError message will appear when the user tries to wrongly set the attribute contents_breakdown."""


@dataclass(kw_only=True, repr=True)
class NexusProc(NetworkObject):
    """Class that represents a single nexus procedure."""
    __priority: Optional[int]
    __contents: Optional[list[str]]
    __contents_breakdown: dict[str, int]

    def __init__(self, date: Optional[str] = None, contents: Optional[list[str]] = None,
                 name: Optional[str] = None, priority: Optional[int] = None, unit_system: Optional[UnitSystem] = None,
                 start_date: Optional[str] = None, date_format: Optional[DateFormat] = None) -> None:
        """Initialize the attributes of the class.

        Attributes:
                date: The date the procedure occured.
                name: The name of the procedure.
                priority: An integer describing the relative priority of the procedure.
                contents: The entire contents of the procedure (everything written between PROC and ENDPROC).
        contents_breakdown: A dictionary of counts for built-in nexus proc functions used in the procedure.

        Methods:
                reset_nexus_proc_function_counts(): Returns a dictionary of zero counts for the nexus proc functions.
        """
        self.__priority = priority
        self.__contents = contents

        self.__contents_breakdown = self.reset_nexus_proc_function_counts()
        super().__init__(properties_dict={}, date=date, date_format=date_format, start_date=start_date,
                         unit_system=unit_system, name=name)

    @property
    def contents(self) -> Optional[list[str]]:
        """Returns the contents of the main body of the procedure."""
        return self.__contents

    @property
    def priority(self) -> Optional[int]:
        """Returns the priority of the procedure."""
        return self.__priority

    @property
    def contents_breakdown(self) -> dict[str, int]:
        """Returns the dictionary counts of the proc functions."""
        return self.__contents_breakdown

    @contents_breakdown.setter
    def contents_breakdown(self, value: dict) -> None:
        # ensures this param is a dict with length equal to the Nexus proc functions
        if (isinstance(value, dict)) and (len(value) == len(self.reset_nexus_proc_function_counts())):
            self.__contents_breakdown = value
        else:
            raise SetError('This parameter is for internal use and should not be set by the user.\n'
                           'This parameter must be a dictionary where the keys are defined according to the 2022\n'
                           'Nexus Keyword Manual page 1013.')

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
        keywords: dict[str, tuple[str, type]] = {
            'NAME': ('name', str),
            'PRIORITY': ('priority', str)
        }
        return keywords

    @staticmethod
    def reset_nexus_proc_function_counts() -> dict[str, int]:
        """This function initializes and returns a dict of built-in Nexus proc functions.

        Please refer to page 1013 of the 2022 Nexus Keyword manual for a description of the functions.
            Returns: A dictionary of Nexus proc functions where the key is the specific function and the value is
        the count, initialized to zero.
        """

        predef_vars = dict(zip(PREDEFINED_VARS, [0] * len(PREDEFINED_VARS)))
        cond = dict(zip(CONDITIONAL_KEYWORDS, [0] * len(CONDITIONAL_KEYWORDS)))
        all_proc_funcs = dict(zip(NEXUS_ALL_PROC_FUNCS, [0] * len(NEXUS_ALL_PROC_FUNCS)))
        to_search = predef_vars | cond | all_proc_funcs

        return to_search

    def to_string(self) -> str:
        """Outputs the procedure as a string in the format it would be written in a Nexus file."""
        output_str = "PROCS"
        if self.name is not None:
            output_str += f" NAME {self.name}"
        if self.priority is not None:
            output_str += f" PRIORITY {self.priority}"
        output_str += '\n'
        if self.contents is not None:
            output_str += '\n'.join(self.contents) + '\n'
        output_str += "ENDPROCS\n"
        return output_str

    @property
    def units(self) -> BaseUnitMapping:
        """Returns the attribute to unit map for the data object."""
        return BaseUnitMapping(None)
