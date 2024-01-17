"""Collection of Enumerations for Units used in ResSimpy."""
from enum import Enum


# Enum representing the Salinity Units
class SUnits(str, Enum):
    MEQ_ML = 'MEQ/ML'
    PPM = 'PPM'


class TemperatureUnits(str, Enum):
    FAHR = 'FAHR'
    CELSIUS = 'CELSIUS'
    RANKINE = 'RANKINE'
    KELVIN = 'KELVIN'


class UnitSystem(str, Enum):
    ENGLISH = 'ENGLISH'  # defined as 'ENGLISH' in Nexus, 'FIELD' in Eclipse
    LAB = 'LAB'  # defined as 'LAB' in Nexus, 'LAB' in Eclipse
    METRIC = 'METRIC'  # defined as 'METRIC' in Nexus, undefined in Eclipse
    METKGCM2 = 'METKG/CM2'  # defined as 'METKG/CM2' in Nexus, undefined in Eclipse
    METBAR = 'METBAR'  # defined as 'METBAR' in Nexus, 'METRIC' in Eclipse
    METRIC_ATM = 'PVT-M'  # undefined in Nexus, PVT-M in Eclipse
    UNDEFINED = 'UNDEFINED'  # Undefined by the simulator
