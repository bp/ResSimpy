from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.DataModelBaseClasses.NetworkObject import NetworkObject
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Units.AttributeMappings.NetworkUnitMapping import NetworkUnits


@dataclass(repr=False)
class Target(NetworkObject, ABC):
    control_quantity: Optional[str] = None
    control_conditions: Optional[str] = None
    control_connections: Optional[str] = None
    control_method: Optional[str] = None
    calculation_method: Optional[str] = None
    calculation_conditions: Optional[str] = None
    calculation_connections: Optional[str] = None
    value: Optional[float] = None
    add_value: Optional[float] = None
    region: Optional[str] = None
    priority: Optional[int] = None
    minimum_rate: Optional[str] = None
    minimum_rate_no_shut: Optional[float] = None
    guide_rate: Optional[str] = None
    max_change_pressure: Optional[float] = None
    rank_dt: Optional[float] = None
    control_type: Optional[str] = None
    calculation_type: Optional[str] = None
    region_number: Optional[int] = None

    def __init__(self, properties_dict: Optional[dict[str, None | int | str | float]] = None,
                 date: Optional[str] = None, date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 unit_system: Optional[UnitSystem] = None, name: Optional[str] = None,
                 control_quantity: Optional[str] = None, control_conditions: Optional[str] = None,
                 control_connections: Optional[str] = None, control_method: Optional[str] = None,
                 calculation_method: Optional[str] = None, calculation_conditions: Optional[str] = None,
                 calculation_connections: Optional[str] = None, value: Optional[float] = None,
                 add_value: Optional[float] = None, region: Optional[str] = None, priority: Optional[int] = None,
                 minimum_rate: Optional[str] = None, minimum_rate_no_shut: Optional[float] = None,
                 guide_rate: Optional[str] = None, max_change_pressure: Optional[float] = None,
                 rank_dt: Optional[float] = None, control_type: Optional[str] = None,
                 calculation_type: Optional[str] = None, region_number: Optional[int] = None) -> None:
        """Initialises the Target class.

        Args:
            properties_dict (dict): dict of the properties to set on the object.
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model. Required if the object uses a decimal TIME.
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
            name (Optional[str]): The name of the object.
            control_quantity(Optional[str]): Specifies control type for connections.
            control_conditions(Optional[str]): Column heading keyword indicating the conditions used for control.
            control_connections(Optional[str]): Specifies connections controlled to meet targets, using lists or single
            connections; constraints ensure targets are satisfied.
            control_method(Optional[str]): Indicates the method used to allocate the target constraint to controlling
            connections.
            calculation_method (Optional[str]): Specifies how the target rate is determined.
            calculation_conditions (Optional[str]): Indicates the conditions used to calculate the target rate.
            calculation_connections (Optional[str]): Indicates which connections contribute to the target calculation.
            value (Optional[float]): Indicates the value for the target rate.
            add_value (Optional[float]): Specifies an amount to be added to the target rate calculated by CALCMETHOD.
            region (Optional[str]): Specified a region name from REGDATA table.
            priority (Optional[int]): Column heading for target priority; lower integers indicate higher priority.
            minimum_rate (Optional[str]): Indicates the minimum rate for each connection. Applies to all CTRL
            unless an individual qmin is specified for a connections in a subsequent TGTCON table.
            minimum_rate_no_shut (Optional[float]): Indicates the minimum rate for each connection. Applies to all CTRL
            unless an individual qmin_noshut is specified for a connections in a subsequent TGTCON table.
            guide_rate (Optional[str]): Specifies the guide rate for each connection.
            max_change_pressure (Optional[float]): Specifies the maximum rate of change of region pressure versus time.
            rank_dt (Optional[float]): Specifies the minimum time change between reranking the connections.
            control_type (Optional[str]): Specifies which connections (or wells) should be included from CTRLCONS
            connections.
            calculation_type (Optional[str]): Specifies which connections (or wells) should be included from CALCONS
            connections.
            region_number (Optional[int]): Region numbers, to which function input options are to be applied.
        """
        self.control_quantity = control_quantity
        self.control_conditions = control_conditions
        self.control_connections = control_connections
        self.control_method = control_method
        self.calculation_method = calculation_method
        self.calculation_conditions = calculation_conditions
        self.calculation_connections = calculation_connections
        self.value = value
        self.add_value = add_value
        self.region = region
        self.priority = priority
        self.minimum_rate = minimum_rate
        self.minimum_rate_no_shut = minimum_rate_no_shut
        self.guide_rate = guide_rate
        self.max_change_pressure = max_change_pressure
        self.rank_dt = rank_dt
        self.control_type = control_type
        self.calculation_type = calculation_type
        self.region_number = region_number

        super().__init__(properties_dict=properties_dict, date=date, date_format=date_format, start_date=start_date,
                         unit_system=unit_system, name=name)

    @property
    def units(self) -> NetworkUnits:
        """Returns the attribute to unit map for the WellConnection."""
        return NetworkUnits(self.unit_system)
