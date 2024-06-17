"""Nexus implementation of the Well Connection class."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.WellConnection import WellConnection


@dataclass(kw_only=True)
class NexusWellConnection(WellConnection):
    """Nexus implementation of the Well Connection class.

    Attributes:
    stream (str): Stream identifier (STREAM)
    number (int): Identification number (NUMBER)
    scale (float): Scaling factor (SCALE)
    bhdepth (float): Bottomhole depth (BHDEPTH)
    datum_depth (float): Depth relative to a datum (DATUM)
    x_pos (float): X-coordinate position (X)
    y_pos (float): Y-coordinate position (Y)
    gradient_calc (str): Gradient calculation method (DATGRAD)
    length (float): Length of the well connection (LENGTH)
    bottomhole_measured_depth (float): Measured depth of the bottom hole (BHMD)
    add_tubing (int): Additional tubing indicator (ADDTUBING)
    diameter (float): Diameter of the well connection (DIAM)
    inner_diameter (float): Inner diameter of the well connection (INNERDIAM)
    roughness (float): Pipe roughness (ROUGHNESS)
    tracer (str): Tracer substance identifier (TRACERS)
    con_type (str): Connection type (TYPE)
    hyd_method (str): Hydraulic method (METHOD)
    pvt_method (int): PVT method (IPVT)
    water_method (int): Water method (IWAT)
    bat_method (int): Bat method (IBAT)
    temperature (float): Temperature (TEMP)
    elevation_profile (str): Elevation profile identifier (ELEVPR)
    temperature_profile (str): Temperature profile identifier (TEMPPR)
    inj_mobility (str): Injection mobility identifier (INJMOB)
    crossshut (str): Cross-shut identifier (CROSS_SHUT)
    crossflow (str): Crossflow identifier (CROSSFLOW)
    on_time (float): On-time duration (ONTIME)
    heat_transfer_coeff (float): Heat transfer coefficient (HTC)
    well_index_mult (float): Well index multiplier (WIMULT)
    productivity_index (float): Productivity index (PI)
    vip_productivity_index (str): VIP productivity index identifier (VIPPI)
    productivity_index_phase (str): Productivity index phase identifier (PIPHASE)
    d_factor (float): Non-Darcy D-factor (D)
    non_darcy_flow_model (str): Non-Darcy flow model identifier (ND)
    non_darcy_flow_method (str): Non-Darcy flow method identifier (DPERF)
    gas_mobility (float): Gas mobility value (GASMOB)
    capillary_number_model (str): Capillary number model identifier (CN)
    dp_add (float): Additional pressure drop (DPADD)
    dt_add (float): Additional temperature change (DTADD)
    rate_mult (float): Rate multiplier (RATEMULT)
    polymer (str): Polymer identifier (POLYMER)
    station (str): Station identifier (STATION)
    drill_queue (str): Drill queue identifier (ASSCDR)
    drill_order_benefit (float): Benefit of the drill order (BENEFIT)
    """

    bh_node_name: Optional[str] = None
    wh_node_name: Optional[str] = None

    stream: Optional[str] = None
    number: Optional[int] = None
    scale: Optional[float] = None
    gradient_calc: Optional[str] = None
    bottomhole_measured_depth: Optional[float] = None
    add_tubing: Optional[int] = None
    tracer: Optional[str] = None
    con_type: Optional[str] = None
    pvt_method: Optional[int] = None
    water_method: Optional[int] = None
    bat_method: Optional[int] = None
    elevation_profile: Optional[str] = None
    temperature_profile: Optional[str] = None
    inj_mobility: Optional[str] = None
    crossshut: Optional[str] = None
    crossflow: Optional[str] = None
    on_time: Optional[float] = None
    heat_transfer_coeff: Optional[float] = None
    well_index_mult: Optional[float] = None
    vip_productivity_index: Optional[float] = None
    productivity_index_phase: Optional[str] = None
    d_factor: Optional[float] = None
    non_darcy_flow_model: Optional[str] = None
    non_darcy_flow_method: Optional[str] = None
    gas_mobility: Optional[float] = None
    capillary_number_model: Optional[str] = None
    dp_add: Optional[float] = None
    dt_add: Optional[float] = None
    rate_mult: Optional[float] = None
    polymer: Optional[str] = None
    station: Optional[str] = None
    drill_queue: Optional[str] = None
    drill_order_benefit: Optional[float] = None

    def __init__(self, properties_dict: dict[str, None | int | str | float], date: Optional[str] = None,
                 date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 unit_system: Optional[UnitSystem] = None) -> None:
        """Initialises the NexusWellConnection class.

        Args:
            properties_dict (dict): dict of the properties to set on the object.
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model. Required if the object uses a decimal TIME.
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
        """
        name = properties_dict.get('name', None)
        name = name if isinstance(name, str) else None
        super().__init__(_date_format=date_format, _start_date=start_date, _unit_system=unit_system, name=name)

        # Set the date related properties, then set the date, automatically setting the ISODate
        protected_attributes = ['date_format', 'start_date', 'unit_system']

        for attribute in protected_attributes:
            if attribute in properties_dict:
                self.__setattr__(f"_{attribute}", properties_dict[attribute])

        # Loop through the properties dict if one is provided and set those attributes
        remaining_properties = [x for x in properties_dict.keys() if x not in protected_attributes]
        for key in remaining_properties:
            self.__setattr__(key, properties_dict[key])

        if date is None:
            if 'date' not in properties_dict or not isinstance(properties_dict['date'], str):
                raise ValueError(f"No valid Date found for object with properties: {properties_dict}")
            self.date = properties_dict['date']
        else:
            self.date = date

        if self.name is not None:
            self.bh_node_name = self.name + '%bh'
            self.wh_node_name = self.name + '%wh'

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
        nexus_mapping = {
            'NAME': ('name', str),
            'STREAM': ('stream', str),
            'NUMBER': ('number', int),
            'SCALE': ('scale', float),
            'BHDEPTH': ('bhdepth', float),
            'DATUM': ('datum_depth', float),
            'X': ('x_pos', float),
            'Y': ('y_pos', float),
            'DATGRAD': ('gradient_calc', str),
            'LENGTH': ('length', float),
            'BHMD': ('bottomhole_measured_depth', float),
            'ADDTUBING': ('add_tubing', int),
            'DIAM': ('diameter', float),
            'INNERDIAM': ('inner_diameter', float),
            'ROUGHNESS': ('roughness', float),
            'TRACERS': ('tracer', str),
            'TYPE': ('con_type', str),
            'METHOD': ('hyd_method', str),
            'IPVT': ('pvt_method', int),
            'IWAT': ('water_method', int),
            'IBAT': ('bat_method', int),
            'TEMP': ('temperature', float),
            'ELEVPR': ('elevation_profile', str),
            'TEMPPR': ('temperature_profile', str),
            'INJMOB': ('inj_mobility', str),
            'CROSS_SHUT': ('crossshut', str),
            'CROSSFLOW': ('crossflow', str),
            'ONTIME': ('on_time', float),
            'HTC': ('heat_transfer_coeff', float),
            'WIMULT': ('well_index_mult', float),
            'PI': ('productivity_index', float),
            'VIPPI': ('vip_productivity_index', float),
            'PIPHASE': ('productivity_index_phase', str),
            'D': ('d_factor', float),
            'ND': ('non_darcy_flow_model', str),
            'DPERF': ('non_darcy_flow_method', str),
            'GASMOB': ('gas_mobility', float),
            'CN': ('capillary_number_model', str),
            'DPADD': ('dp_add', float),
            'DTADD': ('dt_add', float),
            'RATEMULT': ('rate_mult', float),
            'POLYMER': ('polymer', str),
            'STATION': ('station', str),
            'ASSCDR': ('drill_queue', str),
            'BENEFIT': ('drill_order_benefit', float),
            }
        return nexus_mapping

    def __repr__(self) -> str:
        return super().__repr__()
