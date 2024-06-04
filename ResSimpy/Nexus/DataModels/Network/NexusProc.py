from dataclasses import dataclass
from typing import Optional, Mapping
from ResSimpy.Nexus.NexusKeywords.proc_keywords import PREDEFINED_VARS, CONDITIONAL_KEYWORDS, NEXUS_ALL_PROC_FUNCS


# set custom error message
class SetError(Exception):
    """A SetError message will appear when the user tries to wrongly set the attribute contents_breakdown."""


@dataclass(kw_only=True, repr=True)
class NexusProc:
    """Class that represents a single nexus procedure."""
    __date: Optional[str]
    __name: Optional[str]
    __priority: Optional[int]
    __contents: Optional[list[str]]
    __contents_breakdown: dict[str, int]

    def __init__(self, date: Optional[str] = None,
                 contents: Optional[list[str]] = None,
                 name: Optional[str] = None,
                 priority: Optional[int] = None) -> None:
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

        self.__date = date
        self.__name = name
        self.__priority = priority
        self.__contents = contents
        self.__contents_breakdown = self.reset_nexus_proc_function_counts()

    @property
    def contents(self) -> Optional[list[str]]:
        """Returns the contents of the main body of the procedure."""
        return self.__contents

    @property
    def date(self) -> Optional[str]:
        """Returns the date that the procedure occurred."""
        return self.__date

    @property
    def priority(self) -> Optional[int]:
        """Returns the priority of the procedure."""
        return self.__priority

    @property
    def name(self) -> Optional[str]:
        """Returns the name of the procedure."""
        return self.__name

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
    def get_keyword_mapping() -> Mapping[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
        keywords = {
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
