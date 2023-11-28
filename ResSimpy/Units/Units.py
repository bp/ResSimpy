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
Critical Volume ft3/lbmole  m3/kgmole   m3/kgmole   m3/kgmole   cc/gmole
Density	lb/ft3	kg/m3	kg/m3	kg/m3	gm/cc
Formation Volume Factor (Oil)	rb/stb	m3/stm3	m3/stm3	m3/stm3	cc/stcc
Formation Volume Factor (Gas)	rb/mscf	m3/stm3	m3/stm3	m3/stm3	cc/stcc
Gas-Liquid Ratio (Gas-Oil Ratio)	mscf/stb	stm3/stm3	stm3/stm3	stm3/stm3	stcc/stcc
Gravity Gradient	psi/ft	kPa/m	kg/cm2/m	bars/m	psi/cm
Heat Capacity   BTU/lb-F    kJ/kg-K kJ/kg-K kJ/kg-K J/g-K
Length	ft	m	m	m	cm
Liquid-Gas Ratio (Oil-Gas Ratio)    stb/mscf    stm3/stm3	stm3/stm3	stm3/stm3	stcc/stcc
Moles	lb-moles	kg-moles	kg-moles	kg-moles	gm-moles
Molar Density	lb-moles/ft3	kg-moles/m3	kg-moles/m3	kg-moles/m3	gm-moles/cm3
Molar Rates	lb-moles/day	kg-moles/day	kg-moles/day	kg-moles/day	gm-moles/hour
Permeability	md	md	md	md	md
Pressure	psia	kPa	kg/cm2	bars	psia
Reservoir Rates	rb/day	m3/day	m3/day	m3/day	cc/hour
Reservoir Volumes	mrb	k m3	k m3	k m3	k cc
Saturation Fraction	fraction	fraction	fraction	fraction	fraction
Solution Gas-Oil Ratio	mscf/stb	stm3/stm3	stm3/stm3	stm3/stm3	stcc/stcc
Solution Oil-Gas Ratio	stb/mscf    stm3/stm3	stm3/stm3	stm3/stm3	stcc/stcc
Surface Rates (Liquid)	stb/day	stm3/day	stm3/day	stm3/day	stcc/hour
Surface Rates (Gas)	mscf/day	stm3/day	stm3/day	stm3/day	stcc/hour
Surface Volumes (Gas)	mmscf	k stm3	k stm3	k stm3	k stcc
Surface Volumes (Liquid)	mstb	k stm3	k stm3	k stm3	k stcc
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
    english = 'ft/sec(g/cm3)'
    metric = 'm/sec(kg/m3)'
    metkgcm2 = 'm/sec(kg/m3)'
    metbar = 'm/sec(kg/m3)'
    lab = 'cm/sec(g/cm3)'
    metric_atm = 'm/sec(kg/m3)'


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


class CriticalVolume(UnitDimension):
    """Units for critical volume."""
    english = 'ft3/lbmole'
    metric = 'm3/kgmole'
    metkgcm2 = 'm3/kgmole'
    metbar = 'm3/kgmole'
    lab = 'cc/gmole'
    metric_atm = 'm3/kgmole'


class Density(UnitDimension):
    """Units for density."""
    english = 'lb/ft3'
    metric = 'kg/m3'
    metkgcm2 = 'kg/m3'
    metbar = 'kg/m3'
    lab = 'gm/cc'
    metric_atm = 'kg/m3'


class FormationVolumeFactorLiquid(UnitDimension):
    """Units for formation volume factor oil."""
    english = 'rb/stb'
    metric = 'm3/stm3'
    metkgcm2 = 'm3/stm3'
    metbar = 'm3/stm3'
    lab = 'cc/stcc'
    metric_atm = 'm3/stm3'


class FormationVolumeFactorGas(UnitDimension):
    """Units for formation volume factor gas."""
    english = 'rb/mscf'
    metric = 'm3/stm3'
    metkgcm2 = 'm3/stm3'
    metbar = 'm3/stm3'
    lab = 'cc/stcc'
    metric_atm = 'm3/stm3'


class GasLiquidRatio(UnitDimension):
    """Units for gas liquid ratio."""
    english = 'mscf/stb'
    metric = 'stm3/stm3'
    metkgcm2 = 'stm3/stm3'
    metbar = 'stm3/stm3'
    lab = 'stcc/stcc'
    metric_atm = 'stm3/stm3'


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
    lab = 'gm-moles'
    metric_atm = 'kg-moles'


class MolarDensity(UnitDimension):
    """Units for molar density."""
    english = 'lb-moles/ft3'
    metric = 'kg-moles/m3'
    metkgcm2 = 'kg-moles/m3'
    metbar = 'kg-moles/m3'
    lab = 'gm-moles/cm3'
    metric_atm = 'kg-moles/m3'


class MolarRates(UnitDimension):
    """Units for molar rates."""
    english = 'lb-moles/day'
    metric = 'kg-moles/day'
    metkgcm2 = 'kg-moles/day'
    metbar = 'kg-moles/day'
    lab = 'gm-moles/hour'
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
    english = 'rb/day'
    metric = 'm3/day'
    metkgcm2 = 'm3/day'
    metbar = 'm3/day'
    lab = 'cc/hour'
    metric_atm = 'm3/day'


class ReservoirVolumeThousand(UnitDimension):
    """Units for reservoir volumes, in thousands."""
    english = 'mrb'
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
    english = 'mscf/stb'
    metric = 'stm3/stm3'
    metkgcm2 = 'stm3/stm3'
    metbar = 'stm3/stm3'
    lab = 'stcc/stcc'
    metric_atm = 'stm3/stm3'


class SolutionOilGasRatio(UnitDimension):
    """Units for solution oil gas ratio."""
    english = 'stb/mscf'
    metric = 'stm3/stm3'
    metkgcm2 = 'stm3/stm3'
    metbar = 'stm3/stm3'
    lab = 'stcc/stcc'
    metric_atm = 'stm3/stm3'


class SurfaceRatesLiquid(UnitDimension):
    """Units for surface rates liquid."""
    english = 'stb/day'
    metric = 'stm3/day'
    metkgcm2 = 'stm3/day'
    metbar = 'stm3/day'
    lab = 'stcc/hour'
    metric_atm = 'stm3/day'


class SurfaceRatesGas(UnitDimension):
    """Units for surface rates gas."""
    english = 'mscf/day'
    metric = 'stm3/day'
    metkgcm2 = 'stm3/day'
    metbar = 'stm3/day'
    lab = 'stcc/hour'
    metric_atm = 'stm3/day'


class SurfaceVolumesGas(UnitDimension):
    """Units for surface volumes gas."""
    english = 'mmscf'
    metric = 'k stm3'
    metkgcm2 = 'k stm3'
    metbar = 'k stm3'
    lab = 'k stcc'
    metric_atm = 'k stm3'


class SurfaceVolumesLiquid(UnitDimension):
    """Units for surface volumes liquid."""
    english = 'mstb'
    metric = 'k stm3'
    metkgcm2 = 'k stm3'
    metbar = 'k stm3'
    lab = 'k stcc'
    metric_atm = 'k stm3'


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


class InverseTime(UnitDimension):
    """Units for 1/time."""
    english = '1/days'
    metric = '1/days'
    metkgcm2 = '1/days'
    metbar = '1/days'
    lab = '1/hours'
    metric_atm = '1/days'


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
    english = 'ft3*cp/day/psi'
    metric = 'm3*cp/day/kPa'
    metkgcm2 = 'm3*cp/day/kg/cm2'
    metbar = 'm3*cp/day/bars'
    lab = 'cc*cp/hour/psi'
    metric_atm = 'm3*cp/day/atm'


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


class ReservoirVolume(UnitDimension):
    """Units for reservoir volume."""
    english = 'rb'
    metric = 'm3'
    metkgcm2 = 'm3'
    metbar = 'm3'
    lab = 'cc'
    metric_atm = 'm3'


class LiquidGasRatio(UnitDimension):
    """Liquid gas ratio units."""
    english = 'stb/mscf'
    metric = 'stm3/stm3'
    metkgcm2 = 'stm3/stm3'
    metbar = 'stm3/stm3'
    lab = 'stcc/stcc'
    metric_atm = 'stm3/stm3'


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
    english = 'BTU/(hr*ft2*F)'
    metric = 'W/(m2*K)'
    metkgcm2 = 'W/(m2*K)'
    metbar = 'W/(m2*K)'
    lab = 'W/(cm2*K)'
    metric_atm = 'W/(m2*K)'


class ThermalConductivity(UnitDimension):
    """Thermal conductivity units."""
    english = 'BTU/(hr*ft*F)'
    metric = 'W/(m*K)'
    metkgcm2 = 'W/(m*K)'
    metbar = 'W/(m*K)'
    lab = 'W/(cm*K)'
    metric_atm = 'W/(m*K)'


class HeatCapacity(UnitDimension):
    """Heat capacity units."""
    english = 'BTU/(lb*F)'
    metric = 'kJ/(kg*K)'
    metkgcm2 = 'kJ/(kg*K)'
    metbar = 'kJ/(kg*K)'
    lab = 'J/(g*K)'
    metric_atm = 'kJ/(kg*K)'


class DiffusionCoefficient(UnitDimension):
    """Diffusion coefficient units."""
    english = 'ft2/day'
    metric = 'm2/day'
    metkgcm2 = 'm2/day'
    metbar = 'm2/day'
    lab = 'cm2/hr'
    metric_atm = 'm2/day'


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
    english = 'day/mscf'
    metric = 'day/stm3'
    metkgcm2 = 'day/stm3'
    metbar = 'day/stm3'
    lab = 'hour/stcc'
    metric_atm = 'day/stm3'


class ProductivityIndex(UnitDimension):
    """Productivity index units."""
    english = 'stb/day/psi'
    metric = 'stm3/day/kPa'
    metkgcm2 = 'stm3/day/kg/cm2'
    metbar = 'stm3/day/bars'
    lab = 'stcc/hour/psi'
    metric_atm = 'stm3/day/atm'


class ReservoirProductivityIndex(UnitDimension):
    """Productivity index reservoir units."""
    english = 'rb/day/psi'
    metric = 'm3/day/kPa'
    metkgcm2 = 'm3/day/kg/cm2'
    metbar = 'm3/day/bars'
    lab = 'cc/hour/psi'
    metric_atm = 'm3/day/atm'


class ReservoirVolumeOverPressure(UnitDimension):
    """Reservoir volume over pressure, for instance as needed for Carter-Tracy constant."""
    english = 'rb/psia'
    metric = 'm3/kPa'
    metkgcm2 = 'm3/kg/cm2'
    metbar = 'm3/bars'
    lab = 'cc/psia'
    metric_atm = 'stm3/day/atm'


class ValveCoefficient(UnitDimension):
    """Valve coefficient units."""
    english = 'psi(lb/ft3)/(lb/s)2'
    metric = 'kPa(kg/m3)/(kg/s)2'
    metkgcm2 = '(kg/cm2) (kg/m3)/(kg/s)2'
    metbar = 'bar(kg/m3)/(kg/s)2'
    lab = 'psi(gm/cc)/(gm/s)2'
    metric_atm = 'atm(kg/m3)/(kg/s)2'


class InterfacialTension(UnitDimension):
    """Interfacial tension units."""
    english = 'dynes/cm'
    metric = 'dynes/cm'
    metkgcm2 = 'dynes/cm'
    metbar = 'dynes/cm'
    lab = 'dynes/cm'
    metric_atm = 'dynes/cm'
