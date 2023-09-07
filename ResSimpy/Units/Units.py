"""Class for handling the mapping between unit systems and the units used for that unit system."""
from abc import ABC
from dataclasses import dataclass

from ResSimpy.Enums.UnitsEnum import UnitSystem

"""
Variable	English Oilfield Units	Metric Units (kPa)	Metric Units (kg/cm²)	Metric Units (bars)	Lab Units
Acoustic Impedance	ft/sec·(g/cm³)	m/sec·(kg/m³)	m/sec·(kg/m³)	m/sec·(kg/m³)	cm/sec·(g/cm³)
Acoustic Wave Velocity	ft/sec	m/sec	m/sec	m/sec	m/sec
Angle	degrees	degrees	degrees	degrees	degrees
Area	ft²	m²	m²	m²	cm²
Bulk Modulus	psia	kPa	kg/cm²	bars	psia
Compressibility	psi⁻¹	kPa⁻¹	(kg/cm²)⁻¹	(bars)⁻¹	psi⁻¹
Critical Pressure	psia	kPa	(kg/cm²)	bars	psia
Critical Temperature	degrees F	degrees C	degrees C	degrees C	degrees C
Density	lb/ft³	kg/m³	kg/m³	kg/m³	gm/cc
Formation Volume Factor (Oil)	RB/STB	m³/STM³	m³/STM³	m³/STM³	cc/stcc
Formation Volume Factor (Gas)	RB/MSCF	m³/STM³	m³/STM³	m³/STM³	cc/stcc
Gas-Liquid Ratio (Gas-Oil Ratio)	MSCF/STB	SM³/STM³	SM³/STM³	SM³/STM³	stcc/stcc
Gravity Gradient	psi/ft	kPa/m	kg/cm²/m	bars/m	psi/cm
Length	ft	m	m	m	cm
Moles	lb-moles	kg-moles	kg-moles	kg-moles	gmmoles
Molar Density	lb-moles/ft³	kg-moles/m³	kg-moles/m³	kg-moles/m³	gmmoles/cm³
Molar Rates	lb-moles/day	kg-moles/day	kg-moles/day	kg-moles/day	gmmoles/hour
Permeability	md	md	md	md	md
Pressure	psia	kPa	kg/cm²	bars	psia
Reservoir Rates	RB/day	m³/day	m³/day	m³/day	cc/hour
Reservoir Volumes	MRB	k m³	k m³	k m³	k cc
Saturation Fraction	fraction	fraction	fraction	fraction	fraction
Solution Gas-Oil Ratio	MSCF/STB	SM³/STM³	SM³/STM³	SM³/STM³	stcc/stcc
Surface Rates (Liquid)	STB/day	STM³/day	STM³/day	STM³/day	stcc/hour
Surface Rates (Gas)	MSCF/day	SM³/day	SM³/day	SM³/day	stcc/hour
Surface Volumes (Gas)	MMSCF	k STM³	k STM³	k STM³	k stcc
Surface Volumes (Liquid)	MSTB	k STM³	k STM³	k STM³	k stcc
Temperature	degrees F	degrees C	degrees C	degrees C	degrees C
Time	days	days	days	days	hours
Tracer Concentrations	fraction	fraction	fraction	fraction	fraction
Transmissibility	ft³·cp/day/psi	m³·cp/day/kPa	m³·cp/day/kg/cm²	m³·cp/day/bars	cc·cp/hour/psi
Viscosity	cp	cp	cp	cp	cp
Volume	ft³	m³	m³  m³	cc
"""


@dataclass
class UnitDimension(ABC):
    """Class for handling the mapping between unit systems and the units used for that unit system."""
    english = None
    metric = None
    lab = None
    metkgcm2 = None
    metbar = None
    metric_atm = None

    def unit_system_enum_to_variable(self, unit_system: UnitSystem) -> str:
        """Returns the unit variable for the given unit system."""
        match unit_system:
            case UnitSystem.ENGLISH:
                return self.english
            case UnitSystem.LAB:
                return self.lab
            case UnitSystem.METRIC:
                return self.metric
            case UnitSystem.METKGCM2:
                return self.metkgcm2
            case UnitSystem.METBAR:
                return self.metbar
            case UnitSystem.METRIC_ATM:
                return self.metric_atm
            case _:
                raise ValueError(f'Unit system {unit_system} not recognised.')


class Area(UnitDimension):
    """Units for area."""
    english = 'ft2'
    metric = 'm2'
    lab = 'cm2'
    metkgcm2 = 'm2'
    metbar = 'm2'
    metric_atm = 'm2'


class AcousticImpedance(UnitDimension):
    """Units for acoustic impedance."""
    english = 'ft/sec·(g/cm³)'
    metric = 'm/sec·(kg/m³)'
    lab = 'cm/sec·(g/cm³)'
    metkgcm2 = 'm/sec·(kg/m³)'
    metbar = 'm/sec·(kg/m³)'
    metric_atm = 'm/sec·(kg/m³)'


class AcousticWaveVelocity(UnitDimension):
    """Units for acoustic wave velocity."""
    english = 'ft/sec'
    metric = 'm/sec'
    metkgcm2 = 'm/sec'
    metbar = 'm/sec'
    lab = 'm/sec'


class Angle(UnitDimension):
    """Units for angle."""
    english = 'degrees'
    metric = 'degrees'
    lab = 'degrees'
    metkgcm2 = 'degrees'
    metbar = 'degrees'
    metric_atm = 'degrees'


class BulkModulus(UnitDimension):
    """Units for bulk modulus."""
    english = 'psia'
    metric = 'kPa'
    metkgcm2 = 'kg/cm²'
    metbar = 'bars'
    lab = 'psia'
    metric_atm = 'atm'


class Compressibility(UnitDimension):
    """Units for compressibility."""
    english = 'psi⁻¹'
    metric = 'kPa⁻¹'
    metkgcm2 = '(kg/cm²)⁻¹'
    metbar = '(bars)⁻¹'
    lab = 'psi⁻¹'
    metric_atm = '(atm)⁻¹'


class CriticalPressure(UnitDimension):
    """Units for critical pressure."""
    english = 'psia'
    metric = 'kPa'
    metkgcm2 = 'kg/cm²'
    metbar = 'bars'
    lab = 'psia'
    metric_atm = 'atm'


class CriticalTemperature(UnitDimension):
    """Units for critical temperature."""
    english = 'degrees F'
    metric = 'degrees C'
    metkgcm2 = 'degrees C'
    metbar = 'degrees C'
    lab = 'degrees C'


class Density(UnitDimension):
    """Units for density."""
    english = 'lb/ft³'
    metric = 'kg/m³'
    metkgcm2 = 'kg/m³'
    metbar = 'kg/m³'
    lab = 'gm/cc'
    metric_atm = 'kg/m³'


class FormationVolumeFactorOil(UnitDimension):
    """Units for formation volume factor oil."""
    english = 'RB/STB'
    metric = 'm³/STM³'
    metkgcm2 = 'm³/STM³'
    metbar = 'm³/STM³'
    lab = 'cc/stcc'
    metric_atm = 'm³/STM³'


class FormationVolumeFactorGas(UnitDimension):
    """Units for formation volume factor gas."""
    english = 'RB/MSCF'
    metric = 'm³/STM³'
    metkgcm2 = 'm³/STM³'
    metbar = 'm³/STM³'
    lab = 'cc/stcc'
    metric_atm = 'm³/STM³'


class GasLiquidRatio(UnitDimension):
    """Units for gas liquid ratio."""
    english = 'MSCF/STB'
    metric = 'SM³/STM³'
    metkgcm2 = 'SM³/STM³'
    metbar = 'SM³/STM³'
    lab = 'stcc/stcc'
    metric_atm = 'SM³/STM³'


class GravityGradient(UnitDimension):
    """Units for gravity gradient."""
    english = 'psi/ft'
    metric = 'kPa/m'
    metkgcm2 = 'kg/cm²/m'
    metbar = 'bars/m'
    lab = 'psi/cm'
    metric_atm = 'atm/m'


class Length(UnitDimension):
    """Units for length."""
    english = 'ft'
    metric = 'm'
    lab = 'cm'
    metkgcm2 = 'm'
    metbar = 'm'
    metric_atm = 'm'


class Moles(UnitDimension):
    """Units for moles."""
    english = 'lb-moles'
    metric = 'kg-moles'
    metkgcm2 = 'kg-moles'
    metbar = 'kg-moles'
    lab = 'gmmoles'
    metric_atm = 'kg-moles'


class MolarDensity(UnitDimension):
    """Units for molar density."""
    english = 'lb-moles/ft³'
    metric = 'kg-moles/m³'
    metkgcm2 = 'kg-moles/m³'
    metbar = 'kg-moles/m³'
    lab = 'gmmoles/cm³'
    metric_atm = 'kg-moles/m³'


class MolarRates(UnitDimension):
    """Units for molar rates."""
    english = 'lb-moles/day'
    metric = 'kg-moles/day'
    metkgcm2 = 'kg-moles/day'
    metbar = 'kg-moles/day'
    lab = 'gmmoles/hour'
    metric_atm = 'kg-moles/day'


class Permeability(UnitDimension):
    """Units for permeability."""
    english = 'md'
    metric = 'md'
    metkgcm2 = 'md'
    metbar = 'md'
    lab = 'md'
    metric_atm = 'md'


class Pressure(UnitDimension):
    """Units for pressure."""
    english = 'psia'
    metric = 'kPa'
    metkgcm2 = 'kg/cm²'
    metbar = 'bars'
    lab = 'psia'
    metric_atm = 'atm'


class ReservoirRates(UnitDimension):
    """Units for reservoir rates."""
    english = 'RB/day'
    metric = 'm³/day'
    metkgcm2 = 'm³/day'
    metbar = 'm³/day'
    lab = 'cc/hour'
    metric_atm = 'm³/day'


class ReservoirVolumes(UnitDimension):
    """Units for reservoir volumes."""
    english = 'MRB'
    metric = 'k m³'
    metkgcm2 = 'k m³'
    metbar = 'k m³'
    lab = 'k cc'
    metric_atm = 'k m³'


class SaturationFraction(UnitDimension):
    """Units for saturation fraction."""
    english = 'fraction'
    metric = 'fraction'
    lab = 'fraction'
    metkgcm2 = 'fraction'
    metbar = 'fraction'
    metric_atm = 'fraction'


class SolutionGasOilRatio(UnitDimension):
    """Units for solution gas oil ratio."""
    english = 'MSCF/STB'
    metric = 'SM³/STM³'
    metkgcm2 = 'SM³/STM³'
    metbar = 'SM³/STM³'
    lab = 'stcc/stcc'
    metric_atm = 'SM³/STM³'


class SurfaceRatesLiquid(UnitDimension):
    """Units for surface rates liquid."""
    english = 'STB/day'
    metric = 'STM³/day'
    metkgcm2 = 'STM³/day'
    metbar = 'STM³/day'
    lab = 'stcc/hour'
    metric_atm = 'STM³/day'


class SurfaceRatesGas(UnitDimension):
    """Units for surface rates gas."""
    english = 'MSCF/day'
    metric = 'SM³/day'
    metkgcm2 = 'SM³/day'
    metbar = 'SM³/day'
    lab = 'stcc/hour'
    metric_atm = 'SM³/day'


class SurfaceVolumesGas(UnitDimension):
    """Units for surface volumes gas."""
    english = 'MMSCF'
    metric = 'k STM³'
    metkgcm2 = 'k STM³'
    metbar = 'k STM³'
    lab = 'k stcc'
    metric_atm = 'k STM³'


class SurfaceVolumesLiquid(UnitDimension):
    """Units for surface volumes liquid."""
    english = 'MSTB'
    metric = 'k STM³'
    metkgcm2 = 'k STM³'
    metbar = 'k STM³'
    lab = 'k stcc'
    metric_atm = 'k STM³'


class Temperature(UnitDimension):
    """Units for temperature."""
    english = 'degrees F'
    metric = 'degrees C'
    metkgcm2 = 'degrees C'
    metbar = 'degrees C'
    lab = 'degrees C'
    metric_atm = 'degrees C'


class Time(UnitDimension):
    """Units for time."""
    english = 'days'
    metric = 'days'
    metkgcm2 = 'days'
    metbar = 'days'
    lab = 'hours'
    metric_atm = 'days'


class TracerConcentrations(UnitDimension):
    """Units for tracer concentrations."""
    english = 'fraction'
    metric = 'fraction'
    metkgcm2 = 'fraction'
    metbar = 'fraction'
    lab = 'fraction'
    metric_atm = 'fraction'


class Transmissibility(UnitDimension):
    """Units for transmissibility."""
    english = 'ft³·cp/day/psi'
    metric = 'm³·cp/day/kPa'
    metkgcm2 = 'm³·cp/day/kg/cm²'
    metbar = 'm³·cp/day/bars'
    lab = 'cc·cp/hour/psi'
    metric_atm = 'm³·cp/day/atm'


class Viscosity(UnitDimension):
    """Units for viscosity."""
    english = 'cp'
    metric = 'cp'
    metkgcm2 = 'cp'
    metbar = 'cp'
    lab = 'cp'
    metric_atm = 'cp'


class Volume(UnitDimension):
    """Units for volume."""
    english = 'ft³'
    metric = 'm³'
    metkgcm2 = 'm³'
    metbar = 'm³'
    lab = 'cc'
    metric_atm = 'm³'


class LiquidGasRatio(UnitDimension):
    """Liquid gas ratio units."""
    english = 'STB/MSCF'
    metric = 'STM³/SM³'
    metkgcm2 = 'STM³/SM³'
    metbar = 'STM³/SM³'
    lab = 'stcc/stcc'
    metric_atm = 'STM³/SM³'


class AttributeUnitDimension:
    """Class for handling the mapping between unit systems and the units used for that unit system."""
    attribute_map = {
        'max_surface_oil_rate': SurfaceVolumesLiquid(),
        'max_surface_water_rate': SurfaceVolumesLiquid(),
        'max_surface_gas_rate': SurfaceVolumesGas(),
        'max_surface_liquid_rate': SurfaceVolumesLiquid(),
        'max_reservoir_oil_rate': ReservoirRates(),
        'max_reservoir_water_rate': ReservoirRates(),
        'max_reservoir_gas_rate': ReservoirRates(),
        'max_reservoir_liquid_rate': ReservoirRates(),
        'max_hc_moles_rate': MolarRates(),
        'max_reverse_surface_oil_rate': SurfaceVolumesLiquid(),
        'max_reverse_surface_water_rate': SurfaceVolumesLiquid(),
        'max_reverse_surface_gas_rate': SurfaceVolumesGas(),
        'max_reverse_surface_liquid_rate': SurfaceVolumesLiquid(),
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
        'qmult_oil_rate': SurfaceVolumesLiquid(),
        'qmult_water_rate': SurfaceVolumesLiquid(),
        'qmult_gas_rate': SurfaceVolumesGas(),
    }

    def get_unit(self, attribute_name: str, unit_system: UnitSystem, uppercase: bool = False) -> str:
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
