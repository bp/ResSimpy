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
    ENGLISH = 'ENGLISH'
    LAB = 'LAB'
    METRIC = 'METRIC'
    METKGCM2 = 'METKG/CM2'
    METBAR = 'METBAR'
    METRIC_ATM = 'PVT-M'
    UNDEFINED = 'UNDEFINED'
