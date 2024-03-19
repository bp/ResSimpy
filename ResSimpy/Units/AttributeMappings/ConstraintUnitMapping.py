"""Class for handling the mapping between unit systems and the units used for that unit system."""

from typing import Mapping

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping
from ResSimpy.Units.Units import UnitDimension, SurfaceRatesLiquid, SurfaceRatesGas, ReservoirRates, MolarRates, \
    Pressure, Temperature, SaturationFraction, GasLiquidRatio, LiquidGasRatio, SurfaceVolumesGas, SurfaceVolumesLiquid


class ConstraintUnits(BaseUnitMapping):
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
        'max_watercut_plug': SaturationFraction(),
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

    def __init__(self, unit_system: None | UnitSystem) -> None:
        """Initialises the ConstraintUnits class.

        Args:
            unit_system (None | UnitSystem): The unit system to use for the unit mapping.
        """
        super().__init__(unit_system=unit_system)

    @property
    def max_surface_oil_rate(self) -> str:
        """Returns the unit for max_surface_oil_rate."""
        return self.get_unit_for_attribute('max_surface_oil_rate')

    @property
    def max_surface_water_rate(self) -> str:
        """Returns the unit for max_surface_water_rate."""
        return self.get_unit_for_attribute('max_surface_water_rate')

    @property
    def max_surface_gas_rate(self) -> str:
        """Returns the unit for max_surface_gas_rate."""
        return self.get_unit_for_attribute('max_surface_gas_rate')

    @property
    def max_surface_liquid_rate(self) -> str:
        """Returns the unit for max_surface_liquid_rate."""
        return self.get_unit_for_attribute('max_surface_liquid_rate')

    @property
    def max_reservoir_oil_rate(self) -> str:
        """Returns the unit for max_reservoir_oil_rate."""
        return self.get_unit_for_attribute('max_reservoir_oil_rate')

    @property
    def max_reservoir_water_rate(self) -> str:
        """Returns the unit for max_reservoir_water_rate."""
        return self.get_unit_for_attribute('max_reservoir_water_rate')

    @property
    def max_reservoir_gas_rate(self) -> str:
        """Returns the unit for max_reservoir_gas_rate."""
        return self.get_unit_for_attribute('max_reservoir_gas_rate')

    @property
    def max_reservoir_liquid_rate(self) -> str:
        """Returns the unit for max_reservoir_liquid_rate."""
        return self.get_unit_for_attribute('max_reservoir_liquid_rate')

    @property
    def max_hc_moles_rate(self) -> str:
        """Returns the unit for max_hc_moles_rate."""
        return self.get_unit_for_attribute('max_hc_moles_rate')

    @property
    def max_reverse_surface_oil_rate(self) -> str:
        """Returns the unit for max_reverse_surface_oil_rate."""
        return self.get_unit_for_attribute('max_reverse_surface_oil_rate')

    @property
    def max_reverse_surface_water_rate(self) -> str:
        """Returns the unit for max_reverse_surface_water_rate."""
        return self.get_unit_for_attribute('max_reverse_surface_water_rate')

    @property
    def max_reverse_surface_gas_rate(self) -> str:
        """Returns the unit for max_reverse_surface_gas_rate."""
        return self.get_unit_for_attribute('max_reverse_surface_gas_rate')

    @property
    def max_reverse_surface_liquid_rate(self) -> str:
        """Returns the unit for max_reverse_surface_liquid_rate."""
        return self.get_unit_for_attribute('max_reverse_surface_liquid_rate')

    @property
    def max_reverse_reservoir_oil_rate(self) -> str:
        """Returns the unit for max_reverse_reservoir_oil_rate."""
        return self.get_unit_for_attribute('max_reverse_reservoir_oil_rate')

    @property
    def max_reverse_reservoir_water_rate(self) -> str:
        """Returns the unit for max_reverse_reservoir_water_rate."""
        return self.get_unit_for_attribute('max_reverse_reservoir_water_rate')

    @property
    def max_reverse_reservoir_gas_rate(self) -> str:
        """Returns the unit for max_reverse_reservoir_gas_rate."""
        return self.get_unit_for_attribute('max_reverse_reservoir_gas_rate')

    @property
    def max_reverse_reservoir_liquid_rate(self) -> str:
        """Returns the unit for max_reverse_reservoir_liquid_rate."""
        return self.get_unit_for_attribute('max_reverse_reservoir_liquid_rate')

    @property
    def max_reverse_hc_moles_rate(self) -> str:
        """Returns the unit for max_reverse_hc_moles_rate."""
        return self.get_unit_for_attribute('max_reverse_hc_moles_rate')

    @property
    def min_pressure(self) -> str:
        """Returns the unit for min_pressure."""
        return self.get_unit_for_attribute('min_pressure')

    @property
    def max_pressure(self) -> str:
        """Returns the unit for max_pressure."""
        return self.get_unit_for_attribute('max_pressure')

    @property
    def min_temperature(self) -> str:
        """Returns the unit for min_temperature."""
        return self.get_unit_for_attribute('min_temperature')

    @property
    def max_wag_water_pressure(self) -> str:
        """Returns the unit for max_wag_water_pressure."""
        return self.get_unit_for_attribute('max_wag_water_pressure')

    @property
    def max_wag_gas_pressure(self) -> str:
        """Returns the unit for max_wag_gas_pressure."""
        return self.get_unit_for_attribute('max_wag_gas_pressure')

    @property
    def bottom_hole_pressure(self) -> str:
        """Returns the unit for bottom_hole_pressure."""
        return self.get_unit_for_attribute('bottom_hole_pressure')

    @property
    def tube_head_pressure(self) -> str:
        """Returns the unit for tube_head_pressure."""
        return self.get_unit_for_attribute('tube_head_pressure')

    @property
    def min_surface_oil_rate(self) -> str:
        """Returns the unit for min_surface_oil_rate."""
        return self.get_unit_for_attribute('min_surface_oil_rate')

    @property
    def min_surface_water_rate(self) -> str:
        """Returns the unit for min_surface_water_rate."""
        return self.get_unit_for_attribute('min_surface_water_rate')

    @property
    def min_surface_gas_rate(self) -> str:
        """Returns the unit for min_surface_gas_rate."""
        return self.get_unit_for_attribute('min_surface_gas_rate')

    @property
    def min_surface_liquid_rate(self) -> str:
        """Returns the unit for min_surface_liquid_rate."""
        return self.get_unit_for_attribute('min_surface_liquid_rate')

    @property
    def min_reservoir_oil_rate(self) -> str:
        """Returns the unit for min_reservoir_oil_rate."""
        return self.get_unit_for_attribute('min_reservoir_oil_rate')

    @property
    def min_reservoir_water_rate(self) -> str:
        """Returns the unit for min_reservoir_water_rate."""
        return self.get_unit_for_attribute('min_reservoir_water_rate')

    @property
    def min_reservoir_gas_rate(self) -> str:
        """Returns the unit for min_reservoir_gas_rate."""
        return self.get_unit_for_attribute('min_reservoir_gas_rate')

    @property
    def min_reservoir_liquid_rate(self) -> str:
        """Returns the unit for min_reservoir_liquid_rate."""
        return self.get_unit_for_attribute('min_reservoir_liquid_rate')

    @property
    def min_hc_moles_rate(self) -> str:
        """Returns the unit for min_hc_moles_rate."""
        return self.get_unit_for_attribute('min_hc_moles_rate')

    @property
    def min_reverse_surface_oil_rate(self) -> str:
        """Returns the unit for min_reverse_surface_oil_rate."""
        return self.get_unit_for_attribute('min_reverse_surface_oil_rate')

    @property
    def min_reverse_surface_water_rate(self) -> str:
        """Returns the unit for min_reverse_surface_water_rate."""
        return self.get_unit_for_attribute('min_reverse_surface_water_rate')

    @property
    def min_reverse_surface_gas_rate(self) -> str:
        """Returns the unit for min_reverse_surface_gas_rate."""
        return self.get_unit_for_attribute('min_reverse_surface_gas_rate')

    @property
    def min_reverse_surface_liquid_rate(self) -> str:
        """Returns the unit for min_reverse_surface_liquid_rate."""
        return self.get_unit_for_attribute('min_reverse_surface_liquid_rate')

    @property
    def min_reverse_reservoir_oil_rate(self) -> str:
        """Returns the unit for min_reverse_reservoir_oil_rate."""
        return self.get_unit_for_attribute('min_reverse_reservoir_oil_rate')

    @property
    def min_reverse_reservoir_water_rate(self) -> str:
        """Returns the unit for min_reverse_reservoir_water_rate."""
        return self.get_unit_for_attribute('min_reverse_reservoir_water_rate')

    @property
    def min_reverse_reservoir_gas_rate(self) -> str:
        """Returns the unit for min_reverse_reservoir_gas_rate."""
        return self.get_unit_for_attribute('min_reverse_reservoir_gas_rate')

    @property
    def min_reverse_reservoir_liquid_rate(self) -> str:
        """Returns the unit for min_reverse_reservoir_liquid_rate."""
        return self.get_unit_for_attribute('min_reverse_reservoir_liquid_rate')

    @property
    def min_reverse_hc_moles_rate(self) -> str:
        """Returns the unit for min_reverse_hc_moles_rate."""
        return self.get_unit_for_attribute('min_reverse_hc_moles_rate')

    @property
    def max_watercut(self) -> str:
        """Returns the unit for max_watercut."""
        return self.get_unit_for_attribute('max_watercut')

    @property
    def max_watercut_plug(self) -> str:
        """Returns the unit for max_watercut_plug."""
        return self.get_unit_for_attribute('max_watercut_plug')

    @property
    def max_watercut_plugplus(self) -> str:
        """Returns the unit for max_watercut_plugplus."""
        return self.get_unit_for_attribute('max_watercut_plugplus')

    @property
    def max_watercut_perf(self) -> str:
        """Returns the unit for max_watercut_perf."""
        return self.get_unit_for_attribute('max_watercut_perf')

    @property
    def max_watercut_perfplus(self) -> str:
        """Returns the unit for max_watercut_perfplus."""
        return self.get_unit_for_attribute('max_watercut_perfplus')

    @property
    def max_wor(self) -> str:
        """Returns the unit for max_wor."""
        return self.get_unit_for_attribute('max_wor')

    @property
    def max_wor_plug(self) -> str:
        """Returns the unit for max_wor_plug."""
        return self.get_unit_for_attribute('max_wor_plug')

    @property
    def max_wor_plugplus(self) -> str:
        """Returns the unit for max_wor_plugplus."""
        return self.get_unit_for_attribute('max_wor_plugplus')

    @property
    def max_wor_perf(self) -> str:
        """Returns the unit for max_wor_perf."""
        return self.get_unit_for_attribute('max_wor_perf')

    @property
    def max_wor_perfplus(self) -> str:
        """Returns the unit for max_wor_perfplus."""
        return self.get_unit_for_attribute('max_wor_perfplus')

    @property
    def max_gor(self) -> str:
        """Returns the unit for max_gor."""
        return self.get_unit_for_attribute('max_gor')

    @property
    def max_gor_plug(self) -> str:
        """Returns the unit for max_gor_plug."""
        return self.get_unit_for_attribute('max_gor_plug')

    @property
    def max_gor_plugplus(self) -> str:
        """Returns the unit for max_gor_plugplus."""
        return self.get_unit_for_attribute('max_gor_plugplus')

    @property
    def max_gor_perf(self) -> str:
        """Returns the unit for max_gor_perf."""
        return self.get_unit_for_attribute('max_gor_perf')

    @property
    def max_gor_perfplus(self) -> str:
        """Returns the unit for max_gor_perfplus."""
        return self.get_unit_for_attribute('max_gor_perfplus')

    @property
    def max_lgr(self) -> str:
        """Returns the unit for max_lgr."""
        return self.get_unit_for_attribute('max_lgr')

    @property
    def max_lgr_plug(self) -> str:
        """Returns the unit for max_lgr_plug."""
        return self.get_unit_for_attribute('max_lgr_plug')

    @property
    def max_lgr_plugplus(self) -> str:
        """Returns the unit for max_lgr_plugplus."""
        return self.get_unit_for_attribute('max_lgr_plugplus')

    @property
    def max_lgr_perf(self) -> str:
        """Returns the unit for max_lgr_perf."""
        return self.get_unit_for_attribute('max_lgr_perf')

    @property
    def max_lgr_perfplus(self) -> str:
        """Returns the unit for max_lgr_perfplus."""
        return self.get_unit_for_attribute('max_lgr_perfplus')

    @property
    def max_cum_gas_prod(self) -> str:
        """Returns the unit for max_cum_gas_prod."""
        return self.get_unit_for_attribute('max_cum_gas_prod')

    @property
    def max_cum_oil_prod(self) -> str:
        """Returns the unit for max_cum_oil_prod."""
        return self.get_unit_for_attribute('max_cum_oil_prod')

    @property
    def max_cum_water_prod(self) -> str:
        """Returns the unit for max_cum_water_prod."""
        return self.get_unit_for_attribute('max_cum_water_prod')

    @property
    def max_cum_liquid_prod(self) -> str:
        """Returns the unit for max_cum_liquid_prod."""
        return self.get_unit_for_attribute('max_cum_liquid_prod')

    @property
    def qmult_oil_rate(self) -> str:
        """Returns the unit for qmult_oil_rate."""
        return self.get_unit_for_attribute('qmult_oil_rate')

    @property
    def qmult_water_rate(self) -> str:
        """Returns the unit for qmult_water_rate."""
        return self.get_unit_for_attribute('qmult_water_rate')

    @property
    def qmult_gas_rate(self) -> str:
        """Returns the unit for qmult_gas_rate."""
        return self.get_unit_for_attribute('qmult_gas_rate')
