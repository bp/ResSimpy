"""Class for handling the mapping between unit systems and the units used for that unit system."""
from abc import ABC

from ResSimpy.Enums.UnitsEnum import UnitSystem

"""
Variable	English Oilfield Units	Metric Units (kPa)	Metric Units (kg/cm2)	Metric Units (bars)	Lab Units
Acoustic Impedance	ft/sec·(g/cm3)	m/sec·(kg/m3)	m/sec·(kg/m3)	m/sec·(kg/m3)	cm/sec·(g/cm3)
Acoustic Wave Velocity	ft/sec	m/sec	m/sec	m/sec	m/sec
Angle	degrees	degrees	degrees	degrees	degrees
Area	ft2	m2	m2	m2	cm2
Bulk Modulus	psia	kPa	kg/cm2	bars	psia
Compressibility	psi-1	kPa-1	(kg/cm2)-1	(bars)-1	psi-1
Critical Pressure	psia	kPa	(kg/cm2)	bars	psia
Critical Temperature	degrees F	degrees C	degrees C	degrees C	degrees C
Density	lb/ft3	kg/m3	kg/m3	kg/m3	gm/cc
Formation Volume Factor (Oil)	RB/STB	m3/STM3	m3/STM3	m3/STM3	cc/stcc
Formation Volume Factor (Gas)	RB/MSCF	m3/STM3	m3/STM3	m3/STM3	cc/stcc
Gas-Liquid Ratio (Gas-Oil Ratio)	MSCF/STB	SM3/STM3	SM3/STM3	SM3/STM3	stcc/stcc
Gravity Gradient	psi/ft	kPa/m	kg/cm2/m	bars/m	psi/cm
Length	ft	m	m	m	cm
Moles	lb-moles	kg-moles	kg-moles	kg-moles	gmmoles
Molar Density	lb-moles/ft3	kg-moles/m3	kg-moles/m3	kg-moles/m3	gmmoles/cm3
Molar Rates	lb-moles/day	kg-moles/day	kg-moles/day	kg-moles/day	gmmoles/hour
Permeability	md	md	md	md	md
Pressure	psia	kPa	kg/cm2	bars	psia
Reservoir Rates	RB/day	m3/day	m3/day	m3/day	cc/hour
Reservoir Volumes	MRB	k m3	k m3	k m3	k cc
Saturation Fraction	fraction	fraction	fraction	fraction	fraction
Solution Gas-Oil Ratio	MSCF/STB	SM3/STM3	SM3/STM3	SM3/STM3	stcc/stcc
Surface Rates (Liquid)	STB/day	STM3/day	STM3/day	STM3/day	stcc/hour
Surface Rates (Gas)	MSCF/day	SM3/day	SM3/day	SM3/day	stcc/hour
Surface Volumes (Gas)	MMSCF	k STM3	k STM3	k STM3	k stcc
Surface Volumes (Liquid)	MSTB	k STM3	k STM3	k STM3	k stcc
Temperature	degrees F	degrees C	degrees C	degrees C	degrees C
Time	days	days	days	days	hours
Tracer Concentrations	fraction	fraction	fraction	fraction	fraction
Transmissibility	ft3·cp/day/psi	m3·cp/day/kPa	m3·cp/day/kg/cm2	m3·cp/day/bars	cc·cp/hour/psi
Viscosity	cp	cp	cp	cp	cp
Volume	ft3	m3	m3  m3	cc
"""


class UnitDimension(ABC):
    """Class for handling the mapping between unit systems and the units used for that unit system."""
    english: str = ''
    metric: str = ''
    lab: str = ''
    metkgcm2: str = ''
    metbar: str = ''
    metric_atm: str = ''

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
    english = 'ft/sec·(g/cm3)'
    metric = 'm/sec·(kg/m3)'
    metkgcm2 = 'm/sec·(kg/m3)'
    metbar = 'm/sec·(kg/m3)'
    lab = 'cm/sec·(g/cm3)'
    metric_atm = 'm/sec·(kg/m3)'


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
    metkgcm2 = 'kg/cm2'
    metbar = 'bars'
    lab = 'psia'
    metric_atm = 'atm'


class Compressibility(UnitDimension):
    """Units for compressibility."""
    english = 'psi-1'
    metric = 'kPa-1'
    metkgcm2 = '(kg/cm2)-1'
    metbar = '(bars)-1'
    lab = 'psi-1'
    metric_atm = '(atm)-1'


class CriticalPressure(UnitDimension):
    """Units for critical pressure."""
    english = 'psia'
    metric = 'kPa'
    metkgcm2 = 'kg/cm2'
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
    english = 'lb/ft3'
    metric = 'kg/m3'
    metkgcm2 = 'kg/m3'
    metbar = 'kg/m3'
    lab = 'gm/cc'
    metric_atm = 'kg/m3'


class FormationVolumeFactorOil(UnitDimension):
    """Units for formation volume factor oil."""
    english = 'RB/STB'
    metric = 'm3/STM3'
    metkgcm2 = 'm3/STM3'
    metbar = 'm3/STM3'
    lab = 'cc/stcc'
    metric_atm = 'm3/STM3'


class FormationVolumeFactorGas(UnitDimension):
    """Units for formation volume factor gas."""
    english = 'RB/MSCF'
    metric = 'm3/STM3'
    metkgcm2 = 'm3/STM3'
    metbar = 'm3/STM3'
    lab = 'cc/stcc'
    metric_atm = 'm3/STM3'


class GasLiquidRatio(UnitDimension):
    """Units for gas liquid ratio."""
    english = 'MSCF/STB'
    metric = 'SM3/STM3'
    metkgcm2 = 'SM3/STM3'
    metbar = 'SM3/STM3'
    lab = 'stcc/stcc'
    metric_atm = 'SM3/STM3'


class GravityGradient(UnitDimension):
    """Units for gravity gradient."""
    english = 'psi/ft'
    metric = 'kPa/m'
    metkgcm2 = 'kg/cm2/m'
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
    english = 'lb-moles/ft3'
    metric = 'kg-moles/m3'
    metkgcm2 = 'kg-moles/m3'
    metbar = 'kg-moles/m3'
    lab = 'gmmoles/cm3'
    metric_atm = 'kg-moles/m3'


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
    metkgcm2 = 'kg/cm2'
    metbar = 'bars'
    lab = 'psia'
    metric_atm = 'atm'


class DeltaPressure(UnitDimension):
    """Units for pressure."""
    english = 'psi'
    metric = 'kPa'
    metkgcm2 = 'kg/cm2'
    metbar = 'bars'
    lab = 'psi'
    metric_atm = 'atm'


class ReservoirRates(UnitDimension):
    """Units for reservoir rates."""
    english = 'RB/day'
    metric = 'm3/day'
    metkgcm2 = 'm3/day'
    metbar = 'm3/day'
    lab = 'cc/hour'
    metric_atm = 'm3/day'


class ReservoirVolumes(UnitDimension):
    """Units for reservoir volumes."""
    english = 'MRB'
    metric = 'k m3'
    metkgcm2 = 'k m3'
    metbar = 'k m3'
    lab = 'k cc'
    metric_atm = 'k m3'


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
    metric = 'SM3/STM3'
    metkgcm2 = 'SM3/STM3'
    metbar = 'SM3/STM3'
    lab = 'stcc/stcc'
    metric_atm = 'SM3/STM3'


class SurfaceRatesLiquid(UnitDimension):
    """Units for surface rates liquid."""
    english = 'STB/day'
    metric = 'STM3/day'
    metkgcm2 = 'STM3/day'
    metbar = 'STM3/day'
    lab = 'stcc/hour'
    metric_atm = 'STM3/day'


class SurfaceRatesGas(UnitDimension):
    """Units for surface rates gas."""
    english = 'MSCF/day'
    metric = 'SM3/day'
    metkgcm2 = 'SM3/day'
    metbar = 'SM3/day'
    lab = 'stcc/hour'
    metric_atm = 'SM3/day'


class SurfaceVolumesGas(UnitDimension):
    """Units for surface volumes gas."""
    english = 'MMSCF'
    metric = 'k STM3'
    metkgcm2 = 'k STM3'
    metbar = 'k STM3'
    lab = 'k stcc'
    metric_atm = 'k STM3'


class SurfaceVolumesLiquid(UnitDimension):
    """Units for surface volumes liquid."""
    english = 'MSTB'
    metric = 'k STM3'
    metkgcm2 = 'k STM3'
    metbar = 'k STM3'
    lab = 'k stcc'
    metric_atm = 'k STM3'


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
    english = 'ft3·cp/day/psi'
    metric = 'm3·cp/day/kPa'
    metkgcm2 = 'm3·cp/day/kg/cm2'
    metbar = 'm3·cp/day/bars'
    lab = 'cc·cp/hour/psi'
    metric_atm = 'm3·cp/day/atm'


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
    english = 'ft3'
    metric = 'm3'
    metkgcm2 = 'm3'
    metbar = 'm3'
    lab = 'cc'
    metric_atm = 'm3'


class LiquidGasRatio(UnitDimension):
    """Liquid gas ratio units."""
    english = 'STB/MSCF'
    metric = 'STM3/SM3'
    metkgcm2 = 'STM3/SM3'
    metbar = 'STM3/SM3'
    lab = 'stcc/stcc'
    metric_atm = 'STM3/SM3'


class Roughness(UnitDimension):
    """Roughness units."""
    english = 'in'
    metric = 'mm'
    metkgcm2 = 'mm'
    metbar = 'mm'
    lab = 'mm'
    metric_atm = 'mm'


class Diameter(UnitDimension):
    """Diameter units."""
    english = 'in'
    metric = 'cm'
    metkgcm2 = 'cm'
    metbar = 'cm'
    lab = 'cm'
    metric_atm = 'cm'


class HeatTransfer(UnitDimension):
    """Heat transfer units."""
    english = 'BTU/(hr*ft²*F)'
    metric = 'W/(m2*K)'
    metkgcm2 = 'W/(m2*K)'
    metbar = 'W/(m2*K)'
    lab = 'W/(cm2*K)'
    metric_atm = 'W/(m2*K)'


class Dimensionless(UnitDimension):
    """For attributes which do not have a dimension."""
    english = ''
    metric = ''
    metkgcm2 = ''
    metbar = ''
    lab = ''
    metric_atm = ''


class PermeabilityThickness(UnitDimension):
    """Permeability thickness units."""
    english = 'md*ft'
    metric = 'md*m'
    metkgcm2 = 'md*m'
    metbar = 'md*m'
    lab = 'md*m'
    metric_atm = 'md*m'


class NonDarcySkin(UnitDimension):
    """Non darcy skin units."""
    english = 'day/MSCF'
    metric = 'day/SM3'
    metkgcm2 = 'day/SM3'
    metbar = 'day/SM3'
    lab = 'hour/stcc'
    metric_atm = 'day/SM3'
