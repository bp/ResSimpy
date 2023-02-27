# A list of valid Nexus Tokens. Please add to this as you find / use them.
GENERAL_KEYWORDS = ['DESC', 'LABEL']

WELLSPEC_KEYWORDS = ['WELLSPEC', 'CELL', 'KH', 'RADB', 'RADBP', 'PORTYPE', 'FM', 'RADW', 'RADWP', 'SKIN', 'WI',
                     'PPERF', 'IRELPM', 'SECT', 'STAT', 'GROUP', 'ZONE', 'LAYER', 'ANGLE', 'DEPTH', 'X', 'Y',
                     'TEMP', 'FLOWSECT', 'MD', 'PARENT', 'MDCON', 'IPTN', 'LENGTH', 'K', 'D', 'ND', 'DZ',
                     'IW', 'JW', 'GRID', 'ANGLA', 'ANGLV', 'KHMULT', 'L', 'DTOP', 'DBOT', 'WELLMOD']

RELPERM_ENDPT_KEYWORDS = ['SWL', 'SWR', 'SWU', 'SGL', 'SGR', 'SGU', 'SWRO', 'SGRO', 'SGRW', 'KRW_SWRO', 'KRW_SWU',
                          'KRG_SGRO', 'KRG_SGU', 'KRO_SWL', 'KRO_SWR', 'KRO_SGL', 'KRO_SGR', 'KRW_SGL', 'KRW_SGR',
                          'KRG_SGRW', 'SGTR', 'SOTR']

RUNCONTROL_KEYWORDS = ['TIME', 'RUNCONTROL']

UNIT_KEYWORDS = ['ENGLISH', 'METRIC', 'METKG/CM2', 'METBAR', 'LAB', 'FAHR', 'CELSIUS', 'KELVIN', 'RANKINE']

# Keywords that sometimes follow other keywords before the value
INTERMEDIATE_KEYWORDS = ['SET', 'METHOD', 'NETWORK']  # always followed by an int, then a file path

# Keywords that require another keyword after their declaration
STARTING_KEYWORDS = ['RESTART']

PVT_KEYWORDS = ['BLACKOIL', 'WATEROIL', 'GASWATER', 'EOS', 'DENOIL', 'API', 'GOR', 'OGR', 'DENGAS', 'SPECG',
                'MWOR', 'DRYGAS_MFP', 'TEMP', 'SATURATED', 'OIL', 'GAS', 'UNSATOIL', 'UNSATGAS',
                'PRES', 'BO', 'VO', 'RS', 'BG', 'VG', 'RV', 'CV', 'CP', 'PSAT', 'RSSAT', 'DP', 'BOFAC', 'VOFAC',
                'BGFAC', 'VGFAC', 'CVFAC', 'CPFAC'
                ]

# Combine all lists into the complete list
VALID_NEXUS_KEYWORDS = GENERAL_KEYWORDS + WELLSPEC_KEYWORDS + RUNCONTROL_KEYWORDS + UNIT_KEYWORDS \
                       + INTERMEDIATE_KEYWORDS + STARTING_KEYWORDS + RELPERM_ENDPT_KEYWORDS + PVT_KEYWORDS
