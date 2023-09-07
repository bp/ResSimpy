from abc import ABC
from typing import Mapping

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Units.Units import SurfaceRatesLiquid, SurfaceRatesGas, ReservoirRates, MolarRates, Pressure, Temperature, \
    SaturationFraction, GasLiquidRatio, LiquidGasRatio, SurfaceVolumesGas, SurfaceVolumesLiquid, UnitDimension


class AttributeMapBase(ABC):
    attribute_map: Mapping[str, UnitDimension]

    def get_unit_from_attribute(self, attribute_name: str, unit_system: UnitSystem, uppercase: bool = False) -> str:
        """Returns the unit variable for the given unit system.

        Args:
            attribute_name (str): name of the attribute to get the unit for
            unit_system (UnitSystem): unit system to get the unit for
            uppercase (bool): if True returns the unit in uppercase
        """
        unit_dimension = self.attribute_map.get(attribute_name, None)
        if unit_dimension is None:
            raise AttributeError(f'Attribute {attribute_name} not recognised and does not have a unit definition')
        unit = unit_dimension.unit_system_enum_to_variable(unit_system=unit_system)
        if uppercase:
            unit = unit.upper()
        return unit


class ConstraintUnits(AttributeMapBase):
    """Class for handling the mapping between unit systems and the units used for that unit system."""
    attribute_map: Mapping[str, UnitDimension] = {
        'max_surface_oil_rate': SurfaceRatesLiquid(),
        'max_surface_water_rate': SurfaceRatesLiquid(),
        'max_surface_gas_rate': SurfaceRatesGas(),
        'max_surface_liquid_rate': SurfaceRatesLiquid(),
        'max_reservoir_oil_rate': ReservoirRates(),
        'max_reservoir_water_rate': ReservoirRates(),
        'max_reservoir_gas_rate': ReservoirRates(),
        'max_reservoir_liquid_rate': ReservoirRates(),
        'max_hc_moles_rate': MolarRates(),
        'max_reverse_surface_oil_rate': SurfaceRatesLiquid(),
        'max_reverse_surface_water_rate': SurfaceRatesLiquid(),
        'max_reverse_surface_gas_rate': SurfaceRatesGas(),
        'max_reverse_surface_liquid_rate': SurfaceRatesLiquid(),
        'max_reverse_reservoir_oil_rate': ReservoirRates(),
        'max_reverse_reservoir_water_rate': ReservoirRates(),
        'max_reverse_reservoir_gas_rate': ReservoirRates(),
        'max_reverse_reservoir_liquid_rate': ReservoirRates(),
        'max_reverse_hc_moles_rate': MolarRates(),
        'min_pressure': Pressure(),
        'max_pressure': Pressure(),
        'min_temperature': Temperature(),
        'max_wag_water_pressure': Pressure(),
        'max_wag_gas_pressure': Pressure(),
        'bottom_hole_pressure': Pressure(),
        'tube_head_pressure': Pressure(),
        'min_surface_oil_rate': SurfaceRatesLiquid(),
        'min_surface_water_rate': SurfaceRatesLiquid(),
        'min_surface_gas_rate': SurfaceRatesGas(),
        'min_surface_liquid_rate': SurfaceRatesLiquid(),
        'min_reservoir_oil_rate': ReservoirRates(),
        'min_reservoir_water_rate': ReservoirRates(),
        'min_reservoir_gas_rate': ReservoirRates(),
        'min_reservoir_liquid_rate': ReservoirRates(),
        'min_hc_moles_rate': MolarRates(),
        'min_reverse_surface_oil_rate': SurfaceRatesLiquid(),
        'min_reverse_surface_water_rate': SurfaceRatesLiquid(),
        'min_reverse_surface_gas_rate': SurfaceRatesGas(),
        'min_reverse_surface_liquid_rate': SurfaceRatesLiquid(),
        'min_reverse_reservoir_oil_rate': ReservoirRates(),
        'min_reverse_reservoir_water_rate': ReservoirRates(),
        'min_reverse_reservoir_gas_rate': ReservoirRates(),
        'min_reverse_reservoir_liquid_rate': ReservoirRates(),
        'min_reverse_hc_moles_rate': MolarRates(),
        'max_watercut': SaturationFraction(),
        'max_watercut_plug:': SaturationFraction(),
        'max_watercut_plugplus': SaturationFraction(),
        'max_watercut_perf': SaturationFraction(),
        'max_watercut_perfplus': SaturationFraction(),
        'max_wor': SaturationFraction(),
        'max_wor_plug': SaturationFraction(),
        'max_wor_plugplus': SaturationFraction(),
        'max_wor_perf': SaturationFraction(),
        'max_wor_perfplus': SaturationFraction(),
        'max_gor': GasLiquidRatio(),
        'max_gor_plug': GasLiquidRatio(),
        'max_gor_plugplus': GasLiquidRatio(),
        'max_gor_perf': GasLiquidRatio(),
        'max_gor_perfplus': GasLiquidRatio(),
        'max_lgr': LiquidGasRatio(),
        'max_lgr_plug': LiquidGasRatio(),
        'max_lgr_plugplus': LiquidGasRatio(),
        'max_lgr_perf': LiquidGasRatio(),
        'max_lgr_perfplus': LiquidGasRatio(),
        'max_cum_gas_prod': SurfaceVolumesGas(),
        'max_cum_oil_prod': SurfaceVolumesLiquid(),
        'max_cum_water_prod': SurfaceVolumesLiquid(),
        'max_cum_liquid_prod': SurfaceVolumesLiquid(),
        'qmult_oil_rate': SurfaceRatesLiquid(),
        'qmult_water_rate': SurfaceRatesLiquid(),
        'qmult_gas_rate': SurfaceRatesGas(),
    }

