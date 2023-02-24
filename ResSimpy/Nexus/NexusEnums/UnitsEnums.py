from enum import Enum


# Enum representing the Nexus Salinity Units
class SUnits(Enum):
    MEQ_ML = 1
    PPM = 2


class TemperatureUnits(Enum):
    FAHR = 1
    CELSIUS = 2
    RANKINE = 3
    KELVIN = 4
