from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.DataModelBaseClasses.NetworkObject import NetworkObject
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Units.AttributeMappings.NetworkUnitMapping import NetworkUnits


@dataclass(repr=False)
class WellConnection(NetworkObject, ABC):
    bhdepth: Optional[float] = None
    datum_depth: Optional[float] = None
    x_pos: Optional[float] = None
    y_pos: Optional[float] = None
    length: Optional[float] = None
    temperature: Optional[float] = None
    diameter: Optional[float] = None
    roughness: Optional[float] = None
    inner_diameter: Optional[float] = None
    productivity_index: Optional[float] = None
    hyd_method: Optional[str] = None
    crossflow: Optional[str] = None
    crossshut: Optional[str] = None
    inj_mobility: Optional[str] = None
    polymer: Optional[str] = None
    stream: Optional[str] = None
    group: Optional[str] = None
    i: Optional[int] = None
    j: Optional[int] = None
    drainage_radius: Optional[float] = None
    pvt_method: Optional[int] = None
    d_factor: Optional[float] = None
    on_time: Optional[float] = None

    def __init__(self, properties_dict: Optional[dict[str, None | int | str | float]] = None,
                 date: Optional[str] = None, date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 unit_system: Optional[UnitSystem] = None, name: Optional[str] = None,
                 datum_depth: Optional[float] = None, crossflow: Optional[str] = None, crossshut: Optional[str] = None,
                 inj_mobility: Optional[str] = None, polymer: Optional[str] = None, stream: Optional[str] = None,
                 group: Optional[str] = None, i: Optional[int] = None, j: Optional[int] = None,
                 drainage_radius: Optional[float] = None, pvt_method: Optional[int] = None,
                 d_factor: Optional[float] = None, on_time: Optional[float] = None, bhdepth: Optional[float] = None,
                 x_pos: Optional[float] = None, y_pos: Optional[float] = None, length: Optional[float] = None,
                 temperature: Optional[float] = None, diameter: Optional[float] = None,
                 inner_diameter: Optional[float] = None, roughness: Optional[float] = None,
                 productivity_index: Optional[float] = None, hyd_method: Optional[str] = None) -> None:
        """Initialises the WellConnection class.

        Args:
            properties_dict (dict): dict of the properties to set on the object.
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model. Required if the object uses a decimal TIME.
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
            name (Optional[str]): The name of the object.
            crossshut (Optional[str]): Cross-shut identifier.
            crossflow (Optional[str]): Crossflow identifier.
            d_factor (Optional[float]): Non-Darcy D-factor (D).
            datum_depth (Optional[float]): Depth relative to a datum.
            drainage_radius (Optional[float]): The drainage radius.
            group (Optional[str]): The group that the Well Connection belongs to.
            i (Optional[int]): The location of the Well Connection in the i direction.
            j (Optional[int]): The location of the Well Connection in the j direction.
            inj_mobility (Optional[str]): Injection mobility identifier.
            on_time (Optional[float]): On-time duration.
            polymer (Optional[str]): Polymer identifier.
            pvt_method (Optional[int]): PVT method.
            stream (Optional[str]): Stream identifier.
            bhdepth (Optional[float]): Bottomhole depth (BHDEPTH).
            x_pos(Optional[float]): X-coordinate position (X).
            y_pos (Optional[float]): Y-coordinate position (Y).
            length (Optional[float]): Length of the well connection (LENGTH).
            temperature (Optional[float]): Temperature (TEMP).
            diameter (Optional[float]):  Diameter of the well connection (DIAM).
            inner_diameter (Optional[float]): Inner diameter of the well connection (INNERDIAM).
            roughness (Optional[float]): Pipe roughness (ROUGHNESS).
            productivity_index (Optional[float]): Productivity index (PI).
            hyd_method (Optional[str]): Hydraulic method (METHOD).
        """

        self.bhdepth = bhdepth
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.length = length
        self.temperature = temperature
        self.diameter = diameter
        self.inner_diameter = inner_diameter
        self.roughness = roughness
        self.productivity_index = productivity_index
        self.hyd_method = hyd_method

        super().__init__(properties_dict=properties_dict, date=date, date_format=date_format, start_date=start_date,
                         unit_system=unit_system, name=name)

        self.datum_depth = datum_depth if datum_depth is not None else self.datum_depth
        self.crossflow = crossflow if crossflow is not None else self.crossflow
        self.crossshut = crossshut if crossshut is not None else self.crossshut
        self.inj_mobility = inj_mobility if inj_mobility is not None else self.inj_mobility
        self.polymer = polymer if polymer is not None else self.polymer
        self.stream = stream if stream is not None else self.stream
        self.group = group if group is not None else self.group
        self.i = i if i is not None else self.i
        self.j = j if j is not None else self.j
        self.drainage_radius = drainage_radius if drainage_radius is not None else self.drainage_radius
        self.pvt_method = pvt_method if pvt_method is not None else self.pvt_method
        self.d_factor = d_factor if d_factor is not None else self.d_factor
        self.on_time = on_time if on_time is not None else self.on_time

    @property
    def units(self) -> NetworkUnits:
        """Returns the attribute to unit map for the WellConnection."""
        return NetworkUnits(self.unit_system)
