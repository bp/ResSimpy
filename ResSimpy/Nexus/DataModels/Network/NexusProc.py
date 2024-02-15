from dataclasses import dataclass
from typing import Optional, Mapping


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
                 priority: Optional[int] = None) -> None:     # contents_breakdown: Optional[dict[str, int]] = None
        self.__date = date
        self.__name = name
        self.__priority = priority
        self.__contents = contents
        self.__contents_breakdown = self.reset_nexus_proc_function_counts()

        # if contents_breakdown is not None:
        #     #self.__contents_breakdown = self.reset_nexus_proc_function_counts()
        #     raise ValueError('Invalid argument specified. Contents_breakdown must have type None.')
        #
        # else:
        #     self.__contents_breakdown = self.reset_nexus_proc_function_counts()

    @property
    def contents(self) -> list[str]:
        """Returns the contents of the main body of the procedure."""
        return self.__contents

    @property
    def date(self) -> str:
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
        return self.__contents_breakdown

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

        """This function initializes and returns a dict of built-in Nexus proc functions. Please refer to page
        662 of the Nexus Keyword manual for a description of the functions.

            Returns: A dictionary of Nexus proc functions where the key is the specific function and the value is
        the count, initialized to zero.
        """

        # basic nexus proc functions - page 662 of Nexus keyword manual
        nexus_basic_proc_functions = {'ABS': 0, 'ACCUMULATE': 0, 'ANY': 0, 'ALL': 0, 'COUNT': 0, 'MAX': 0,
                                      'MAXVAL': 0, 'MIN': 0, 'MINVAL': 0, 'POWER': 0, 'PRINTOUT': 0, 'SET_VALUE': 0,
                                      'SIZE': 0, 'SUM': 0}

        # nexus functions that manipulate lists - page 673 of Nexus keyword manual
        nexus_functions_manipulate_lists = {'FILTER': 0, 'INTERSECT': 0, 'MASK': 0, 'SORT': 0, 'UNION': 0}

        # nexus functions to retrieve network data - page 676 of Nexus keyword manual
        nexus_functions_to_retrieve_network_data = {'CONC': 0, 'CONPARAM': 0, 'CUM': 0, 'GET_CONSTRAINT': 0,
                                                    'GET_TARGET': 0, 'GET_TGTCON': 0, 'GLR': 0, 'GOR': 0,
                                                    'IS_ACTIVE': 0, 'IS_BACK_FLOWING': 0, 'IS_FLOWING': 0,
                                                    'IS_NOT_FLOWING': 0, 'IS_SHUTIN': 0, 'OGR': 0, 'P': 0,
                                                    'PERF_LOOP': 0, 'Q': 0, 'QP': 0, 'VALVE_SETTING': 0,
                                                    'WAGPARAM': 0, 'WCUT': 0, 'WGR': 0, 'WOR': 0}
        # nexus functions that change network data
        nexus_functions_change_network_data = {'ABANDON': 0, 'ACTIVATE': 0, 'CONSTRAINT': 0, 'DEACTIVATE': 0,
                                               'DRILL': 0, 'GLR_SHUT': 0, 'NEXT_METHOD': 0}
        nexus_other_functions = {'GET_DT': 0, 'SET_DEBUG': 0, 'GET_TIME': 0, 'SET_LOG': 0, 'SET_PRINT': 0,
                                 'SET_DT': 0}

        # merge the dicts using | operator and return it
        return (nexus_basic_proc_functions | nexus_functions_manipulate_lists |
                nexus_functions_to_retrieve_network_data | nexus_functions_change_network_data |
                nexus_other_functions)

