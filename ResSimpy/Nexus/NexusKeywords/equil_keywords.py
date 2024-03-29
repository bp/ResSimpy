
EQUIL_KEYWORDS_VALUE_FLOAT = ['PINIT', 'DINIT', 'TINIT', 'GOC', 'WOC', 'PCGOC', 'PCWOC', 'PSAT', 'API', 'GWC',
                              'PCGWC', 'SALINITY', 'CHLORIDE', 'CALCIUM', 'LI_FACTOR', 'LI_AUTO',
                              'SORWMN', 'SORGMN', 'SGCMN', 'VAITS_TOLSG', 'VAITS_TOLSW',
                              'WOC_PALEO', 'GOC_PALEO']
EQUIL_KEYWORDS_VALUE_STR = ['OVERREAD', 'AUTOGOC_COMP', 'VIP_INIT']
EQUIL_OVERREAD_VALUES = ['PRESSURE', 'SW', 'SG', 'MOLEFRACTION']
EQUIL_SINGLE_KEYWORDS = ['WATERZONE_NEW_INIT', 'LI_AUTO_GAS', 'KEEPSG', 'KEEPSW', 'HONOR_GZONE', 'HONOR_WZONE',
                         'PCADJ_SCALING', 'NONEQ', 'SEDIMENTATION', 'MATCHVIPPRES', 'NOMATCHVIPPRES', 'CRINIT',
                         'HONOR_GASPRESSURE_GWC', 'POROSITY_INDEPENDENCE', 'POROSITY_DEPENDENCE']
EQUIL_INTSAT_KEYWORDS = ['INTSAT', 'VAITS']
EQUIL_TABLE_KEYWORDS = ['DEPTHVAR', 'OILMF', 'GASMF', 'COMPOSITION']
EQUIL_COMPOSITION_OPTIONS = ['X', 'Y']
EQUIL_TABLE_HEADERS = ['DEPTH', 'PSAT', 'TEMP', 'API', 'SALINITY', 'CHLORIDE', 'CALCIUM', 'X', 'Y']
EQUIL_KEYWORDS = EQUIL_KEYWORDS_VALUE_FLOAT + EQUIL_KEYWORDS_VALUE_STR + EQUIL_SINGLE_KEYWORDS + \
    EQUIL_INTSAT_KEYWORDS + EQUIL_TABLE_KEYWORDS
