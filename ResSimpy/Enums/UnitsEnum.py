from enum import Enum


# Class representing the different unit systems that can be used
class Units(Enum):
    OILFIELD = 1  # defined as 'ENGLISH' in Nexus
    LAB = 2
    METRIC_KPA = 3
    METRIC_KGCM2 = 4
    METRIC_BARS = 5
    METRIC_ATMOSPHERES = 6
