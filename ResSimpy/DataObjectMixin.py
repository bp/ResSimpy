import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ResSimpy.Utils import to_dict_generic
from ResSimpy.Utils.obj_to_table_string import to_table_line


@dataclass(init=False)
class DataObjectMixin(ABC):
    __id: uuid.UUID = field(default_factory=lambda: uuid.uuid4(), compare=False)

    def to_dict(self, keys_in_keyword_style: bool = False, add_date=True, add_units=True) -> \
            dict[str, None | str | int | float]:
        """Returns a dictionary of the attributes of the object.

        Args:
            keys_in_keyword_style (bool): if True returns the key values as simulator keywords, otherwise returns the \
                attribute name as stored by ressimpy.

        Returns:
            a dictionary keyed by attributes and values as the value of the attribute
        """
        result_dict = to_dict_generic.to_dict(self, keys_in_keyword_style, add_date=add_date, add_units=add_units)
        return result_dict

    def to_table_line(self, headers: list[str]) -> str:
        return to_table_line(self, headers)

    @property
    def id(self) -> uuid.UUID:
        """Unique identifier for each Node object."""
        return self.__id

    @staticmethod
    @abstractmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        raise NotImplementedError("Implement this in the derived class")
