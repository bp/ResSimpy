# TODO: Not a complete list. Check manual for missing keywords.
# TODO: Delete the keywords that are not tokens (i.e. that are only values in a table)

INTEGER_ARRAYS = ['ICOARS', 'IEQUIL', 'IPVT', 'IWATER', 'IALPHAF', 'IPOLYMER', 'IRELPM', 'IROCK', 'IREGION',
                  'IADSORPTION', 'ITRAN', 'ITRACER', 'DEADCELL', 'LIVECELL', 'IGRID', 'ISECTOR']

WORK_ARRAYS = ['WORKA1', 'WORKA2', 'WORKA3', 'WORKA4', 'WORKA5', 'WORKA6', 'WORKA7', 'WORKA8', 'WORKA9']

ROCK_ARRAYS = ['SWL', 'SWR', 'SGL', 'SGR', 'SWRO', 'SWRO_LS', 'SGRO', 'SGRW', 'KRW_SWRO', 'KRWS_LS', 'KRW_SWU',
               'KRG_SGRO', 'KRG_SGU', 'KRO_SWL', 'KRO_SGL', 'KRO_SGR', 'KRW_SGL', 'KRW_SGR', 'KRG_SGRW', 'SGTR',
               'SOTR', 'SWLPC', 'SGLPC', 'PCW_SWL', 'PCG_SGU']

USER_INIT_ARRAYS = ['SW', 'SG', 'PRESSURE', 'TEMPERATURE', 'CHLORIDE', 'CALCIUM', 'SALINITY', 'API',
                    'WORKA1', 'WORKA2', 'WORKA3', 'WORKA4', 'WORKA5', 'WORKA6', 'WORKA7', 'WORKA8', 'WORKA9']

MULTIPLIER_ARRAYS = ['TMX', 'TMY', 'TMZ', 'MULTBV']

PROPERTY_ARRAYS = ['POROSITY', 'POR', 'POROSITY', 'PV', 'KX', 'KY', 'KZ', 'COMPR', 'CR', 'NETGRS', 'KWX',
                   'KWY', 'KWZ', 'PEMDMAT', 'PEMGMAT', 'PEMKMAT', 'BW_SAL', 'BW_T']

GRID_GEOMETRY_ARRAYS = ['CORP', 'EIGHT', 'DX', 'DY', 'DZ', 'DXB', 'DYB', 'DZB', 'MDEPTH', 'DEPTH', 'DBZNET']

GRID_OPERATION_KEYWORDS = ['ADD', 'SUB', 'DIV', 'MULT', 'EQ']

GRID_ARRAY_FORMAT_KEYWORDS = ['CON', 'VALUE', 'XVAR', 'YVAR', 'ZVAR', 'MULT', 'LAYER', 'DIP', 'NONE']

GRID_ARRAY_KEYWORDS = INTEGER_ARRAYS + WORK_ARRAYS + ROCK_ARRAYS + USER_INIT_ARRAYS + MULTIPLIER_ARRAYS + \
                      PROPERTY_ARRAYS + GRID_GEOMETRY_ARRAYS

STRUCTURED_GRID_KEYWORDS = ['ADD', 'ALL', 'ANALYT', 'ARRAYS', 'B', 'BLOCKS', 'C', 'CARTREF', 'COARSEN', 'COMPR', 'CON',
                            'CONCENTRATION', 'CORNER', 'CORP', 'CORTOL', 'DEADCELL', 'DECOMP', 'DEPTH', 'DIP', 'DIV',
                            'DX', 'DY', 'DZ', 'END', 'ENDAQ', 'ENDDEC', 'ENDREF', 'EXP', 'FNAME', 'FRAC', 'FTRANS',
                            'FUNCTION', 'GE', 'GRID', 'ID', 'IEQUIL', 'IINF', 'INCLUDE', 'INFLUX', 'IPVT', 'IREGION',
                            'IRELPM', 'IROCK', 'ITRAN', 'IWATER', 'JINF', 'KINF', 'KRG_SGRW', 'KRO_SWL', 'KRW_SWRO',
                            'KRW_SWU', 'KX', 'KXEFF', 'KY', 'KYEFF', 'KZ', 'KZEFF', 'LAYER', 'LE', 'LGR', 'LIVECELL',
                            'LX', 'LY', 'LZ', 'MAPBINARY', 'MAPOUT', 'MAPVDB', 'MDEPTH', 'MIN', 'MINUS', 'MOD', 'MODX',
                            'MODY', 'MODZ', 'MULT', 'MULTBV', 'MULTFL', 'MULTIR', 'NETGRS', 'NEWTRAN', 'NOLIST', 'NONE',
                            'NONSTD', 'NX', 'NY', 'NZ', 'OMIT', 'OUTPUT', 'OVER', 'PINCHOUT', 'POR', 'POROSITY',
                            'PRINT', 'PV', 'PVMULT', 'RANGE', 'RIGHTHANDED', 'ROOT', 'SALINITY', 'SG', 'SGL', 'SGR',
                            'SGRO', 'SGRW', 'SGU', 'SINF', 'STD', 'SW', 'SWL', 'SWR', 'SWRO', 'SWRO_LS', 'SWU', 'TMX',
                            'TMY', 'TMZ', 'TOLPV', 'TX', 'TY', 'TZ', 'V98', 'VALUE', 'WATER', 'WINDOW', 'WORKA1', 'X',
                            'XREG', 'Z', 'ZVAR', 'LIST']
