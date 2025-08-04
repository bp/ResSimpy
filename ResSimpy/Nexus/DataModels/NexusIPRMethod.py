from ResSimpy.DataModelBaseClasses.DataObjectMixin import DataObjectMixin
from dataclasses import dataclass
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping
import pandas as pd
from pandas import DataFrame


@dataclass
class NexusIprMethod(DataObjectMixin):
    """Class to hold IPR Method."""

    __table: pd.DataFrame

    def __init__(self, date: str, table: pd.DataFrame) -> None:
        """Individual IPRTable class to add read of IPR files.

        Args:
             date(str): IPR table date.
             table(pd.DataFrame): IPR table.
        """

        self.__table = table

        super().__init__(date=date)

    @property
    def units(self) -> BaseUnitMapping:
        """Returns BaseUnitMapping."""
        return BaseUnitMapping(unit_system=None)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type[float]]]:
        """Gets the mapping of keywords to attribute definitions."""
        mapping = {
            'PRES': ('pressure', float),
            'QO': ('oil_surface_rate', float),
            'QW': ('water_surface_rate', float),
            'QG': ('gas_surface_rate', float),
        }
        return mapping

    @property
    def table(self) -> DataFrame:
        """Returns table as DataFrame."""
        return self.__table
