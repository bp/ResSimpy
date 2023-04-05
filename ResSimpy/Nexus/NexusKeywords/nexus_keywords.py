# A list of valid Nexus Tokens. Please add to this as you find / use them.
from ResSimpy.Nexus.NexusKeywords.aquifer_keywords import AQUIFER_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.equil_keywords import EQUIL_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.fcs_keywords import FCS_ALL_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.gaslift_keywords import GASLIFT_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.hyd_keywords import HYD_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.options_keywords import OPTIONS_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.pvt_keywords import PVT_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.relpm_keywords import RELPM_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.rock_keywords import ROCK_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.runcontrol_keywords import RUNCONTROL_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.separator_keywords import SEPARATOR_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.structured_grid_keywords import GRID_ARRAY_KEYWORDS, STRUCTURED_GRID_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.surface_keywords import SURFACE_KEYWORDS, CONNECTION_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.valve_keywords import VALVE_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.water_keywords import WATER_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.wells_keywords import WELLS_KEYWORDS

GENERAL_KEYWORDS = ['DESC', 'LABEL']

RELPERM_ENDPT_KEYWORDS = ['SWL', 'SWR', 'SWU', 'SGL', 'SGR', 'SGU', 'SWRO', 'SGRO', 'SGRW', 'KRW_SWRO', 'KRW_SWU',
                          'KRG_SGRO', 'KRG_SGU', 'KRO_SWL', 'KRO_SWR', 'KRO_SGL', 'KRO_SGR', 'KRW_SGL', 'KRW_SGR',
                          'KRG_SGRW', 'SGTR', 'SOTR']

UNIT_KEYWORDS = ['ENGLISH', 'METRIC', 'METKG/CM2', 'METBAR', 'LAB', 'FAHR', 'CELSIUS', 'KELVIN', 'RANKINE']

# Keywords that sometimes follow other keywords before the value
INTERMEDIATE_KEYWORDS = ['SET', 'METHOD', 'NETWORK']  # always followed by an int, then a file path

# Keywords that require another keyword after their declaration
STARTING_KEYWORDS = ['RESTART']

# Combine all lists into the complete list
VALID_NEXUS_KEYWORDS = GENERAL_KEYWORDS + RUNCONTROL_KEYWORDS + UNIT_KEYWORDS \
                       + INTERMEDIATE_KEYWORDS + STARTING_KEYWORDS + RELPERM_ENDPT_KEYWORDS + PVT_KEYWORDS \
                       + FCS_ALL_KEYWORDS + WELLS_KEYWORDS + WATER_KEYWORDS + VALVE_KEYWORDS + SURFACE_KEYWORDS + \
                       CONNECTION_KEYWORDS + GRID_ARRAY_KEYWORDS + STRUCTURED_GRID_KEYWORDS + SEPARATOR_KEYWORDS + \
                       ROCK_KEYWORDS + AQUIFER_KEYWORDS + EQUIL_KEYWORDS + GASLIFT_KEYWORDS + HYD_KEYWORDS + \
                       OPTIONS_KEYWORDS + PVT_KEYWORDS + RELPM_KEYWORDS + WELLS_KEYWORDS
