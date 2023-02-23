# A list of valid Nexus Tokens. Please add to this as you find / use them.
WELLSPEC_KEYWORDS = ['WELLSPEC', 'CELL', 'KH', 'RADB', 'RADBP', 'PORTYPE', 'FM', 'RADW', 'RADWP', 'SKIN', 'WI', 'PPERF',
                     'IRELPM',
                     'SECT', 'STAT', 'GROUP', 'ZONE', 'LAYER', 'ANGLE', 'DEPTH', 'X', 'Y', 'TEMP', 'FLOWSECT', 'MD',
                     'PARENT', 'MDCON',
                     'IPTN', 'LENGTH', 'K', 'D', 'ND', 'DZ', 'IW', 'JW', 'GRID', 'ANGLA', 'ANGLV', 'KHMULT', 'L',
                     'DTOP', 'DBOT', 'SWL',
                     'SWR', 'SWU', 'SGL', 'SGR', 'SGU', 'SWRO', 'SGRO', 'SGRW', 'KRW_SWRO', 'KRW_SWU', 'KRG_SGRO',
                     'KRG_SGU', 'KRO_SWL',
                     'KRO_SWR', 'KRO_SGL', 'KRO_SGR', 'KRW_SGL', 'KRW_SGR', 'KRG_SGRW', 'SGTR', 'SOTR', 'WELLMOD']

RUNCONTROL_KEYWORDS = ['TIME', 'RUNCONTROL']

UNIT_KEYWORDS = ['ENGLISH', 'METRIC', 'METKG/CM2', 'METBAR', 'LAB']

# Keywords that sometimes follow other keywords before the value
INTERMEDIATE_KEYWORDS = ['SET', 'METHOD', 'NETWORK']  # always followed by an int, then a file path

# Keywords that require another keyword after their declaration
STARTING_KEYWORDS = ['RESTART']
FCS_KEYWORDS = [
    'EQUIL', 'EOS_DEFAULTS', 'TRACER_INIT', 'STRUCTURED_GRID', 'OPTIONS', 'ROCK', 'RELPM', 'ADSORPTION', 'PVT',
    'SEPARATOR', 'ALPHAF', 'POLYMER', 'WATER', 'AQUIFER', 'FLUXIN', 'RUNCONTROL', 'WELLS', 'SURFACE', 'IPR', 'GASLIFT',
    'VALVE', 'HYD', 'PUMP', 'COMPRESSOR', 'CHOKE', 'EQUIL', 'ICD', 'ESP']
# Combine all lists into the complete list
VALID_NEXUS_KEYWORDS = WELLSPEC_KEYWORDS + RUNCONTROL_KEYWORDS + UNIT_KEYWORDS + INTERMEDIATE_KEYWORDS \
    + STARTING_KEYWORDS + FCS_KEYWORDS
