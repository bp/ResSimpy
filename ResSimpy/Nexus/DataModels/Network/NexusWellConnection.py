"""Nexus implementation of the Well Connection class."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.DataModelBaseClasses.WellConnection import WellConnection


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
    is_activated (bool): Whether the Well Connection has been activated using ACTIVATED / DEACTIVATE. Defaults to True.
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

    def __init__(self, properties_dict: Optional[dict[str, None | int | str | float]] = None,
                 date: Optional[str] = None, date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 unit_system: Optional[UnitSystem] = None, name: Optional[str] = None,
                 bh_node_name: Optional[str] = None, wh_node_name: Optional[str] = None,
                 stream: Optional[str] = None, number: Optional[int] = None, scale: Optional[float] = None,
                 gradient_cal: Optional[str] = None, bottomhole_measured_depth: Optional[float] = None,
                 add_tubing: Optional[int] = None, tracer: Optional[str] = None, con_type: Optional[str] = None,
                 pvt_method: Optional[int] = None, water_method: Optional[int] = None, bat_method: Optional[int] = None,
                 elevation_profile: Optional[str] = None, temperature_profile: Optional[str] = None,
                 inj_mobility: Optional[str] = None, crossshut: Optional[str] = None, crossflow: Optional[str] = None,
                 on_time: Optional[float] = None, heat_transfer_coeff: Optional[float] = None,
                 well_index_mult: Optional[float] = None, vip_productivity_index: Optional[float] = None,
                 productivity_index_phase: Optional[str] = None, d_factor: Optional[float] = None,
                 non_darcy_flow_model: Optional[str] = None, non_darcy_flow_method: Optional[str] = None,
                 gas_mobility: Optional[float] = None, capillary_number_model: Optional[str] = None,
                 dp_add: Optional[float] = None, dt_add: Optional[float] = None, rate_mult: Optional[float] = None,
                 polymer: Optional[str] = None, station: Optional[str] = None, drill_queue: Optional[str] = None,
                 drill_order_benefit: Optional[float] = None, bhdepth: Optional[float] = None,
                 datum_depth: Optional[float] = None, x_pos: Optional[float] = None,
                 y_pos: Optional[float] = None, length: Optional[float] = None, temperature: Optional[float] = None,
                 diameter: Optional[float] = None, roughness: Optional[float] = None,
                 inner_diameter: Optional[float] = None, productivity_index: Optional[float] = None,
                 hyd_method: Optional[str] = None, group: Optional[str] = None, i: Optional[int] = None,
                 j: Optional[int] = None, drainage_radius: Optional[float] = None) -> None:
        """Initialises the NexusWellConnection class.

        Args:
            properties_dict (Optional[dict]): dict of the properties to set on the object.
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model. Required if the object uses a decimal TIME.
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
            is_activated: bool: Whether the Well Connection has been set as activated. Defaults to True.
            name (Optional[str]): The name of the object.
            bh_node_name (Optional[str]): Bottom hole node name.
            wh_node_name (Optional[str]): Wellhead node name.
            stream (Optional[str]): Stream identifier (STREAM).
            number (Optional[int]): Identificaiton number (Number).
            scale (Optional[float]): Scaling factor (SCALE).
            gradient_cal (Optional[str]): Gradient calculation method (DATGRAD).
            bottomhole_measured_depth (Optional[float]): Measured depth of the bottom hole (BHMD).
            add_tubing (Optional[int]): Additional tubing indicator (ADDTUBING).
            tracer (Optional[str]): Tracer substance identifier (TRACERS).
            con_type (Optional[str]): Connection type (TYPE).
            pvt_method (Optional[int]): PVT method (IPVT).
            water_method (Optional[int]): Water method (IWAT).
            bat_method (Optional[int]): Bat method (IBAT).
            elevation_profile (Optional[str]): Elevation profile identifier (ELEVPR).
            temperature_profile (Optional[str]): Temperature profile identifier (TEMPPR).
            inj_mobility (Optional[str]): Injection mobility identifier (INJMOB).
            crossshut (Optional[str]): Cross-shut identifier (CROSS_SHUT).
            crossflow (Optional[str]): Crossflow identifier (CROSSFLOW).
            on_time (Optional[float]): On-time duration (ONTIME).
            heat_transfer_coeff (Optional[float]): Heat transfer coefficient (HTC).
            well_index_mult (Optional[float]): Well index multiplier (WIMULT).
            vip_productivity_index (Optional[float]): VIP productivity index identifier (VIPPI).
            productivity_index_phase (Optional[str]): Productivity index phase identifier (PIPHASE).
            d_factor (Optional[float]): Non-Darcy D-factor (D).
            non_darcy_flow_model (Optional[str]): Non-Darcy flow model identifier (ND).
            non_darcy_flow_method (Optional[str]): Non-Darcy flow method identifier (DPERF)
            gas_mobility (Optional[float]): Gas mobility value (GASMOB).
            capillary_number_model (Optional[str]): Capillary number model identifier (CN).
            dp_add (Optional[float]): Additional pressure drop (DPADD).
            dt_add (Optional[float]): Additional temperature change (DTADD).
            rate_mult (Optional[float]): Rate multiplier (RATEMULT).
            polymer (Optional[str]): Polymer identifier (POLYMER).
            station (Optional[str]): Station identifier (STATION).
            drill_queue (Optional[str]): Drill queue identifier (ASSCDR).
            drill_order_benefit (Optional[float]): Benefit of the drill order (BENEFIT).
            is_activated (bool): Whether the Well Connection has been activated using ACTIVATED / DEACTIVATE
            Defaults to True.
            bhdepth (float): Bottomhole depth (BHDEPTH)
            datum_depth (float): Depth relative to a datum (DATUM)
            x_pos (float): X-coordinate position (X)
            y_pos (float): Y-coordinate position (Y)
            length (float): Length of the well connection (LENGTH)
            temperature (float): Temperature (TEMP)
            diameter (float): Diameter of the well connection (DIAM)
            roughness (float): Pipe roughness (ROUGHNESS)
            inner_diameter (float): Inner diameter of the well connection (INNERDIAM)
            productivity_index_phase (str): Productivity index phase identifier (PIPHASE)
            hyd_method (str): Hydraulic method (METHOD)
            group (Optional[str]): The group that the Well Connection belongs to.
            drainage_radius (Optional[float]): The drainage radius.
            i (Optional[int]): The location of the Well Connection in the i direction.
            j (Optional[int]): The location of the Well Connection in the j direction.
            productivity_index (Optional[float]): Productivity index (PI).
        """

        self.bh_node_name = bh_node_name
        self.wh_node_name = wh_node_name
        self.stream = stream
        self.number = number
        self.scale = scale
        self.gradient_calc = gradient_cal
        self.bottomhole_measured_depth = bottomhole_measured_depth
        self.add_tubing = add_tubing
        self.tracer = tracer
        self.con_type = con_type
        self.pvt_method = pvt_method
        self.water_method = water_method
        self.bat_method = bat_method
        self.elevation_profile = elevation_profile
        self.temperature_profile = temperature_profile
        self.inj_mobility = inj_mobility
        self.on_time = on_time
        self.heat_transfer_coeff = heat_transfer_coeff
        self.well_index_mult = well_index_mult
        self.vip_productivity_index = vip_productivity_index
        self.productivity_index_phase = productivity_index_phase
        self.d_factor = d_factor
        self.non_darcy_flow_model = non_darcy_flow_model
        self.non_darcy_flow_method = non_darcy_flow_method
        self.gas_mobility = gas_mobility
        self.capillary_number_model = capillary_number_model
        self.dp_add = dp_add
        self.dt_add = dt_add
        self.rate_mult = rate_mult
        self.polymer = polymer
        self.station = station
        self.drill_queue = drill_queue
        self.drill_order_benefit = drill_order_benefit
        super().__init__(date_format=date_format, start_date=start_date, unit_system=unit_system, name=name, date=date,
                         properties_dict=properties_dict, bhdepth=bhdepth, datum_depth=datum_depth, x_pos=x_pos,
                         y_pos=y_pos, length=length, temperature=temperature, diameter=diameter, roughness=roughness,
                         inner_diameter=inner_diameter, productivity_index=productivity_index, hyd_method=hyd_method,
                         group=group, i=i, j=j, drainage_radius=drainage_radius, crossflow=crossflow,
                         crossshut=crossshut)

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
            'GASMOB': ('gas_mobility', str),
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
