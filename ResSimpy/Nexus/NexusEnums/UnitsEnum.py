from enum import Enum
class Units(str, Enum):
    ENGLISH = 'ENGLISH'     # defined as 'ENGLISH' in Nexus, 'FIELD' in Eclipse
    LAB = 'LAB'             # defined as 'LAB' in Nexus, 'LAB' in Eclipse
    METRIC = 'METRIC'       # defined as 'METRIC' in Nexus, undefined in Eclipse
    METKGCM2 = 'METKG/CM2'  # defined as 'METKG/CM2' in Nexus, undefined in Eclipse
    METBAR = 'METBAR'       # defined as 'METBAR' in Nexus, 'METRIC' in Eclipse
    METRIC_ATM = 'PVT-M'    # undefined in Nexus, PVT-M in Eclipse

