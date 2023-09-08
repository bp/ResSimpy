from typing import Mapping

from ResSimpy.Units.AttributeMappings.AttributeMappingBase import AttributeMapBase
from ResSimpy.Units.Units import UnitDimension, Length, Temperature, Diameter, Roughness, ReservoirRates, Dimensionless, \
    Pressure, HeatTransfer, Time


class NetworkUnits(AttributeMapBase):
    """Unit types for the attributes of a well connection, wellhead, wellbore, ."""
    attribute_map: Mapping[str, UnitDimension] = {
        'bhdepth': Length(),
        'depth': Length(),
        'datum_depth': Length(),
        'x_pos': Length(),
        'y_pos': Length(),
        'length': Length(),
        'temperature': Temperature(),
        'diameter': Diameter(),
        'roughness': Roughness(),
        'inner_diameter': Diameter(),
        'productivity_index': ReservoirRates(),
        'rate_mult': Dimensionless(),
        'dp_add': Pressure(),
        'dt_add': Temperature(),
        'water_inj_mult': Dimensionless(),
        'vip_productivity_index': ReservoirRates(),
        'd_factor': Dimensionless(),
        'gas_mobility': Dimensionless(),
        'drill_order_benefit': Dimensionless(),
        'heat_transfer_coeff': HeatTransfer(),
        'non_darcy_flow_model': Dimensionless(),
        'non_darcy_flow_method': Dimensionless(),
        'capillary_number_model': Dimensionless(),
        'on_time': Dimensionless(),
        'crossflow': Dimensionless(),
        'crossshut_method': Dimensionless(),
        'inj_mobility': Dimensionless(),
        'temperature_profile': Dimensionless(),
        'elevation_profile': Dimensionless(),
        'measured_depth_in': Length(),
        'measured_depth_out': Length(),
        'delta_depth': Length(),
        'temp': Temperature(),
        'hyd_method': Dimensionless(),
        'pvt_method': Dimensionless(),
        'water_method': Dimensionless(),
        'bat_method': Dimensionless(),
        'number': Dimensionless(),
        'gradient_calc': Dimensionless(),
        'add_tubing': Dimensionless(),
        'tracer': Dimensionless(),
        'con_type': Dimensionless(),
        'bore_type': Dimensionless(),

        # Units from Target class
        'control_quantity': Dimensionless(),
        'control_type': Dimensionless(),
        'control_condition': Dimensionless(),
        'control_method': Dimensionless(),
        'control_connections': Dimensionless(),
        'calculation_method': Dimensionless(),
        'calculation_conditions': Dimensionless(),
        'calculation_connections': Dimensionless(),
        'value': Dimensionless(),
        'add_value': Dimensionless(),
        'region': Dimensionless(),
        'priority': Dimensionless(),
        'minimum_rate': Dimensionless(),
        'minimum_rate_no_shut': Dimensionless(),
        'guide_rate': Dimensionless(),
        'max_change_pressure': Pressure(),
        'rank_dt': Time(),
        'calculation_type': Dimensionless(),
    }
