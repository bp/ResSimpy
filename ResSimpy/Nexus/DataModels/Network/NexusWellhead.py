"""Class representing a single Wellhead in a Nexus Network."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.DataModelBaseClasses.Wellhead import Wellhead


@dataclass(kw_only=True)
class NexusWellhead(Wellhead):
    """Class representing a single Wellhead in a Nexus Network.

    Attributes:
        well (str):  Associates the wellhead to the well. (WELL)
        name (str):  The name of the wellhead. (NAME)
        type (str):  The type of well. (TYPE)
        depth (float):  The depth of the wellhead  (DEPTH)
        x_pos (float):  The x-coordinate location of the wellhead  (X)
        y_pos (float):  The y-coordinate location of the wellhead  (Y)
        pvt_method (int):  The PVT table numbers to be used for the well and wellhead connections. (IPVT)
        water_method (int):  The Water PVT table numbers to be used for the well and wellhead connections. (IWAT)
        bat_method (int):  The separator battery numbers associated with the well and wellhead connections. (IBAT)
        measured_depth_in (float):  The measured depth at the start of the well interval  (MDIN)
        measured_depth_out (float):  The measured depth at the end of the well interval  (MDOUT)
        hyd_method (int):  The hydraulic method used. (METHOD)
        number (int):  The well number. (NUMBER)
        diameter (float):  The wellbore diameter  (DIAM)
        inner_diameter (float):  The well inner diameter  (INNERDIAM)
        roughness (float):  The well roughness. (ROUGHNESS)
        length (float):  The length of the well  (LENGTH)
        temperature (float):  The temperature of the fluid in the well  (TEMP)
        elevation_profile (str):  The well elevation profile. (ELEVPR)
        temperature_profile (str):  The well temperature profile. (TEMPPR)
        dp_add (float):  The additional pressure drop across the well  (DPADD)
        rate_mult (float):  The rate multiplier for the well. (RATEMULT)
        delta_depth (float):  The depth difference between the two points in the connection  (DDEPTH)
        heat_transfer_coeff (float):  The heat transfer coefficient for the well  (HTC)
        dt_add (float):  The additional temperature difference across the well  (DTADD).
    """

    pvt_method: Optional[int] = None
    water_method: Optional[int] = None
    bat_method: Optional[int] = None
    measured_depth_in: Optional[float] = None
    measured_depth_out: Optional[float] = None
    hyd_method: Optional[int] = None
    number: Optional[int] = None
    diameter: Optional[float] = None
    inner_diameter: Optional[float] = None
    roughness: Optional[float] = None
    length: Optional[float] = None
    temperature: Optional[float] = None
    elevation_profile: Optional[str] = None
    temperature_profile: Optional[str] = None
    dp_add: Optional[float] = None
    rate_mult: Optional[float] = None
    delta_depth: Optional[float] = None
    heat_transfer_coeff: Optional[float] = None
    dt_add: Optional[float] = None

    def __init__(self, properties_dict: dict[str, None | int | str | float], date: Optional[str] = None,
                 date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 unit_system: Optional[UnitSystem] = None, name: Optional[str] = None, pvt_method: Optional[int] = None,
                 water_method: Optional[int] = None, bat_method: Optional[int] = None,
                 measured_depth_in: Optional[float] = None, measured_depth_out: Optional[float] = None,
                 hyd_method: Optional[int] = None, number: Optional[int] = None, diameter: Optional[float] = None,
                 inner_diameter: Optional[float] = None, roughness: Optional[float] = None,
                 length: Optional[float] = None, temperature: Optional[float] = None,
                 elevation_profile: Optional[str] = None, temperature_profile: Optional[str] = None,
                 dp_add: Optional[float] = None, rate_mult: Optional[float] = None, delta_depth: Optional[float] = None,
                 heat_transfer_coeff: Optional[float] = None, dt_add: Optional[float] = None,
                 well: Optional[str] = None, wellhead_type: Optional[str] = None, depth: Optional[float] = None,
                 x_pos: Optional[float] = None, y_pos: Optional[float] = None) -> None:
        """Initialises the NexusWellhead class.

        Args:
            properties_dict (dict): dict of the properties to set on the object.
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model. Required if the object uses a decimal TIME.
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
            name (Optional[str]): The name of the object.
            pvt_method (Optional[int]): The PVT table numbers to be used for the well and wellhead connections (IPVT).
            water_method (Optional[int]): The Water PVT table numbers to be used for the well and
            wellhead connections. (IWAT).
            bat_method (Optional[int]): The separator battery numbers associated with the well
            and wellhead connections (IBAT).
            measured_depth_in (Optional[float]): The measured depth at the start of the well interval (MDIN).
            measured_depth_out (Optional[float]): Measured depth of the output node (MDOUT).
            hyd_method (Optional[int]): hydraulic lift correlation method used (METHOD).
            number (Optional[int]): The well number (NUMBER).
            diameter (Optional[float]): The wellbore diameter (DIAM).
            inner_diameter (Optional[float]): The well inner diameter (INNERDIAM).
            roughness (Optional[float]): The well roughness (ROUGHNESS).
            length (optional[float]): The length of the well (LENGTH).
            temperature (Optional[float]): The temperature of the fluid in the well (TEMP).
            elevation_profile (Optional[str]): The well elevation profile (ELEVPR).
            temperature_profile (Optional[str]): The well temperature profile (TEMPPR).
            dp_add (Optional[float]): The additional pressure drop across the well (DPADD).
            rate_mult (Optional[float]): The rate multiplier for the well (RATEMULT).
            delta_depth (Optional[float]): The depth difference between the two points in the connection (DDEPTH).
            heat_transfer_coeff (Optional[float]): The heat transfer coefficient for the well (HTC).
            dt_add (Optional[float]): The additional temperature difference across the well (DTADD).
            well (Optional[str]): Associates the wellhead to the well.
            wellhead_type (Optional[str]): The type of well.
            depth (Optional[float]): The depth of the wellhead
            x_pos (Optional[float]): The x-coordinate of the wellhead (x).
            y_pos (Optional[float]): The y-coordinate of the wellhead (y).
        """

        self.pvt_method = pvt_method
        self.water_method = water_method
        self.bat_method = bat_method
        self.measured_depth_in = measured_depth_in
        self.measured_depth_out = measured_depth_out
        self.hyd_method = hyd_method
        self.number = number
        self.diameter = diameter
        self.inner_diameter = inner_diameter
        self.roughness = roughness
        self.length = length
        self.temperature = temperature
        self.elevation_profile = elevation_profile
        self.temperature_profile = temperature_profile
        self.dp_add = dp_add
        self.rate_mult = rate_mult
        self.delta_depth = delta_depth
        self.heat_transfer_coeff = heat_transfer_coeff
        self.dt_add = dt_add

        super().__init__(date_format=date_format, start_date=start_date, unit_system=unit_system, name=name, date=date,
                         properties_dict=properties_dict, well=well, wellhead_type=wellhead_type, depth=depth,
                         x_pos=x_pos, y_pos=y_pos)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
        nexus_mapping = {
            'WELL': ('well', str),
            'NAME': ('name', str),
            'TYPE': ('wellhead_type', str),
            'DEPTH': ('depth', float),
            'X': ('x_pos', float),
            'Y': ('y_pos', float),
            'IPVT': ('pvt_method', int),
            'IWAT': ('water_method', int),
            'IBAT': ('bat_method', int),
            'MDIN': ('measured_depth_in', float),
            'MDOUT': ('measured_depth_out', float),
            'METHOD': ('hyd_method', int),
            'NUMBER': ('number', int),
            'DIAM': ('diameter', float),
            'INNERDIAM': ('inner_diameter', float),
            'ROUGHNESS': ('roughness', float),
            'LENGTH': ('length', float),
            'TEMP': ('temperature', float),
            'ELEVPR': ('elevation_profile', str),
            'TEMPPR': ('temperature_profile', str),
            'DPADD': ('dp_add', float),
            'RATEMULT': ('rate_mult', float),
            'DDEPTH': ('delta_depth', float),
            'HTC': ('heat_transfer_coeff', float),
            'DTADD': ('dt_add', float),
        }

        return nexus_mapping
