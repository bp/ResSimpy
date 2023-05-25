# TODO: Not a complete list. Check manual for missing keywords.
# TODO: Delete the keywords that are not tokens (i.e. that are only values in a table)

AQUIFER_TYPE_KEYWORDS = ['CARTER_TRACY', 'FETKOVICH']
AQUIFER_SINGLE_KEYWORDS = ['RADIAL', 'LINEAR', 'NOFLOW', 'CONSTP']
AQUIFER_KEYWORDS_VALUE_FLOAT = ['BAQ', 'CT', 'POR', 'H', 'RO', 'RE', 'S', 'W', 'L', 'TC', 'VISC', 'K', 'LINFAC',
                                'PAQI', 'DAQI', 'SALINITY', 'CHLORIDE', 'CALCIUM', 'PI', 'WEI', 'WAQI']
AQUIFER_KEYWORDS_VALUE_INT = ['ITDPD', 'IWATER']
AQUIFER_TABLE_KEYWORDS = ['TDPD', 'TRACER']

AQUIFER_KEYWORDS = AQUIFER_TYPE_KEYWORDS + AQUIFER_SINGLE_KEYWORDS + AQUIFER_KEYWORDS_VALUE_FLOAT + \
                   AQUIFER_KEYWORDS_VALUE_INT + AQUIFER_TABLE_KEYWORDS
