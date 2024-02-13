from dataclasses import dataclass
from typing import Optional, Mapping


@dataclass(kw_only=True, repr=True)
class NexusProc:
    """Class that represents a single nexus procedure."""
    __date: str
    __name: Optional[str]
    __priority: Optional[int]
    __contents: list[str]

    def __init__(self, date: str, contents: list[str], name: Optional[str] = None, priority: Optional[int] = None) -> \
            None:
        self.__date = date
        self.__name = name
        self.__priority = priority
        self.__contents = contents

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

    @staticmethod
    def get_keyword_mapping() -> Mapping[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
        keywords = {
            'NAME': ('name', str),
            'PRIORITY': ('priority', str)
        }
        return keywords
