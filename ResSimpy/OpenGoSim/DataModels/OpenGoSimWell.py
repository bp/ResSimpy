from dataclasses import dataclass

from ResSimpy.Completion import Completion
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Enums.WellTypeEnum import WellType
from ResSimpy.Well import Well


@dataclass(kw_only=True)
class OpenGoSimWell(Well):
    __well_type: WellType

    def __init__(self, well_name: str, completions: list[Completion], well_type: WellType) -> None:
        self.__well_type = well_type

        super().__init__(well_name=well_name, completions=completions, unit_system=UnitSystem.ENGLISH)


    @property
    def well_type(self) -> WellType:
        """The Well Type."""
        return self.__well_type
