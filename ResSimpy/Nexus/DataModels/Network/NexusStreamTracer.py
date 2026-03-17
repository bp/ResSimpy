"""Class representing a single Nexus STREAM_TRACER entry."""

from __future__ import annotations
from dataclasses import dataclass

from ResSimpy.DataModelBaseClasses.DataObjectMixin import DataObjectMixinDictType
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.DataModelBaseClasses.NetworkObject import NetworkObject
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping


@dataclass(kw_only=True, repr=False)
class NexusStreamTracer(NetworkObject):
    """Represents a single row in a Nexus STREAM_TRACER table.

    A STREAM_TRACER block associates named streams with a fluid component and
    an optional tracer name and concentration, e.g.::

        STREAM_TRACER
        NAME       COMPONENT   TRACER   CONCENTRATION
        SEAWTR     WATER       SALT     1.0
        TRTWTR     WATER       SALT     1.0
        ENDSTREAM_TRACER

    Attributes:
        name (str): The stream name (NAME column). Used in WELLS tables as the STREAM value.
        component (str): The fluid component associated with this stream (COMPONENT column),
            e.g. ``'WATER'``, ``'GAS'``, ``'OIL'``.
        tracer (Optional[str]): The tracer label (TRACER column). Defaults to None.
        concentration (Optional[float]): Tracer concentration (CONCENTRATION column). Defaults to None.
    """

    component: str | None = None
    tracer: str | None = None
    concentration: float | None = None

    def __init__(
        self,
        properties_dict: DataObjectMixinDictType | None = None,
        date: str | None = None,
        date_format: DateFormat | None = None,
        start_date: str | None = None,
        unit_system: UnitSystem | None = None,
        name: str | None = None,
        component: str | None = None,
        tracer: str | None = None,
        concentration: float | None = None,
    ) -> None:
        """Initialises the NexusStreamTracer class.

        Args:
            properties_dict (Optional[dict]): dict of the properties to set on the object.
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model.
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
            name (Optional[str]): The stream name (NAME column).
            component (Optional[str]): Fluid component, e.g. ``'WATER'``, ``'GAS'``, ``'OIL'``.
            tracer (Optional[str]): Tracer label (TRACER column).
            concentration (Optional[float]): Tracer concentration (CONCENTRATION column).
        """
        self.component = component
        self.tracer = tracer
        self.concentration = concentration

        super().__init__(
            properties_dict=properties_dict,
            date=date,
            date_format=date_format,
            start_date=start_date,
            unit_system=unit_system,
            name=name,
        )

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of Nexus STREAM_TRACER column headers to attribute definitions."""
        return {
            'NAME': ('name', str),
            'COMPONENT': ('component', str),
            'TRACER': ('tracer', str),
            'CONCENTRATION': ('concentration', float),
        }

    @property
    def units(self) -> BaseUnitMapping:
        """Returns the attribute-to-unit map for this data object."""
        return BaseUnitMapping(unit_system=self.unit_system)
