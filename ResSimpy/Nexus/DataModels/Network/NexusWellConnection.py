from dataclasses import dataclass
from typing import Optional

from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
import ResSimpy.Utils.to_dict_generic as to_dict_generic


@dataclass(kw_only=True)
class NexusWellConnection:
    """
    Attributes:
        stream (str): COMMENT (STREAM)
        number (int): COMMENT (NUMBER)
        scale (float): COMMENT (SCALE)
        bhdepth (float): COMMENT (BHDEPTH)
        datum_depth (float): COMMENT (DATUM)
        x_pos (float): COMMENT (X)
        y_pos (float): COMMENT (Y)
        gradient_calc (str): COMMENT (DATGRAD)
        length (float): COMMENT (LENGTH)
        bottomhole_measured_depth (float): COMMENT (BHMD)
        add_tubing (int): COMMENT (ADDTUBING)
        diameter (float): COMMENT (DIAM)
        inner_diameter (float): COMMENT (INNERDIAM)
        roughness (float): COMMENT (ROUGHNESS)
        tracer (str): COMMENT (TRACERS)
        con_type (str): COMMENT (TYPE)
        hyd_method (str): COMMENT (METHOD)
        pvt_method (int): COMMENT (IPVT)
        water_method (int): COMMENT (IWAT)
        bat_method (int): COMMENT (IBAT)
        temperature (float): COMMENT (TEMP)
        elevation_profile (str): COMMENT (ELEVPR)
        temperature_profile (str): COMMENT (TEMPPR)
        inj_mobility (str): COMMENT (INJMOB)
        crossshut_method (str): COMMENT (CROSS_SHUT)
        crossflow (str): COMMENT (CROSSFLOW)
        on_time (float): COMMENT (ONTIME)
        heat_transfer_coeff (float): COMMENT (HTC)
        water_inj_mult (float): COMMENT (WIMULT)
        productivity_index (float): COMMENT (PI)
        vip_productivity_index (float): COMMENT (VIPPI)
        productivity_index_phase (float): COMMENT (PIPHASE)
        d_factor (float): COMMENT (D)
        non_darcy_flow_model (str): COMMENT (ND)
        non_darcy_flow_method (str): COMMENT (DPERF)
        gas_mobility (float): COMMENT (GASMOB)
        capillary_number_model (str): COMMENT (CN)
        dp_add (float): COMMENT (DPADD)
        dt_add (float): COMMENT (DTADD)
        rate_mult (float): COMMENT (RATEMULT)
        polymer (str): COMMENT (POLYMER)
        station (str): COMMENT (STATION)
        drill_queue (str): COMMENT (ASSCDR)
        drill_order_benefit (float): COMMENT (BENEFIT)
    """
    name: Optional[str] = None
    date: Optional[str] = None
    unit_system: Optional[UnitSystem] = None
    bh_node_name: Optional[str] = None
    wh_node_name: Optional[str] = None

    stream: Optional[str] = None
    number: Optional[int] = None
    scale: Optional[float] = None
    bhdepth: Optional[float] = None
    datum_depth: Optional[float] = None
    x_pos: Optional[float] = None
    y_pos: Optional[float] = None
    gradient_calc: Optional[str] = None
    length: Optional[float] = None
    bottomhole_measured_depth: Optional[float] = None
    add_tubing: Optional[int] = None
    diameter: Optional[float] = None
    inner_diameter: Optional[float] = None
    roughness: Optional[float] = None
    tracer: Optional[str] = None
    con_type: Optional[str] = None
    hyd_method: Optional[str] = None
    pvt_method: Optional[int] = None
    water_method: Optional[int] = None
    bat_method: Optional[int] = None
    temperature: Optional[float] = None
    elevation_profile: Optional[str] = None
    temperature_profile: Optional[str] = None
    inj_mobility: Optional[str] = None
    crossshut_method: Optional[str] = None
    crossflow: Optional[str] = None
    on_time: Optional[float] = None
    heat_transfer_coeff: Optional[float] = None
    water_inj_mult: Optional[float] = None
    productivity_index: Optional[float] = None
    vip_productivity_index: Optional[float] = None
    productivity_index_phase: Optional[float] = None
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

    def __init__(self, properties_dict: dict[str, None | int | str | float]):
        for key, prop in properties_dict.items():
            self.__setattr__(key, prop)
        if self.name is not None:
            self.bh_node_name = self.name + '%bh'
            self.wh_node_name = self.name + '%wh'

    @staticmethod
    def get_nexus_mapping() -> dict[str, tuple[str, type]]:
        """gets the mapping of nexus keywords to attribute definitions"""
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
            'CROSS_SHUT': ('crossshut_method', str),
            'CROSSFLOW': ('crossflow', str),
            'ONTIME': ('on_time', float),
            'HTC': ('heat_transfer_coeff', float),
            'WIMULT': ('water_inj_mult', float),
            'PI': ('productivity_index', float),
            'VIPPI': ('vip_productivity_index', float),
            'PIPHASE': ('productivity_index_phase', float),
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

    def to_dict(self, keys_in_nexus_style: bool = False) -> dict[str, None | str | int | float]:
        """
            Returns a dictionary of the attributes of the well connection
        Args:
            keys_in_nexus_style (bool): if True returns the key values in Nexus keywords, otherwise returns the \
                attribute name as stored by ressimpy

        Returns:
            a dictionary keyed by attributes and values as the value of the attribute
        """
        result_dict = to_dict_generic.to_dict(self, keys_in_nexus_style, add_date=True, add_units=True)
        return result_dict