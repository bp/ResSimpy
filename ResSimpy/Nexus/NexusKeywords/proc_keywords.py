PREDEFINED_VARS = ["TIME", "ITIME", "NEWTON", "ALL1D", "ALL2D", "FIRST", "DAY", "MONTH", "YEAR", "SECOND", "MINUTE",
                   "HOUR", 'PRODWHCONS', "PRODBHCONS", "PRODWHNODES", "PRODBHNODES", "INJWHCONS", "INJBHCONS",
                   "INJWHNODES", "INJBHNODES", 'PRODWELLS', 'GASINJWELLS', 'WATERINJWELLS', 'CONSTRAINTS_CHANGED',
                   'NETWORK_CHANGED', 'NETWORK_TIME_INPUT', 'START_OF_RESTART']

CONDITIONAL_KEYWORDS = ['IF', 'ELSEIF', 'ELSE', 'THEN', 'EXIT', 'DO', 'CYCLE']

NEXUS_PROC_BASIC_FUNCS = ['ABS', 'ACCUMULATE', 'ANY', 'ALLOCATE', 'ALL', 'COUNT', 'MAX', 'MAXVAL', 'MIN', 'MINVAL',
                          'POWER', 'PRINTOUT', 'SET_VALUE', 'SIZE', 'SUM', 'EXP', 'LOG', 'LOG10', 'LOOKUP', 'OUTPUT',
                          'REDUCE', 'SPREADSHEET', 'SQRT']

NEXUS_PROC_PRINT_FUNCS = ['APPENDTOBUFFER', 'CLEARBUFFER', 'PRINTBUFFER', 'PRINTOUT', 'SETBUFFERPOSITION']

NEXUS_PROC_RETRIEVE_NETWORK_DATA_FUNCS = ['CONC', 'CONPARAM', 'CUM', 'GET_CONSTRAINT', 'GET_TARGET', 'GET_TGTCON',
                                          'GLR', 'GOR', 'IS_ACTIVE', 'IS_BACK_FLOWING', 'IS_FLOWING', 'IS_NOT_FLOWING',
                                          'IS_SHUTIN', 'OGR', 'P', 'PERF_LOOP', 'Q', 'QP', 'VALVE_SETTING', 'WAGPARAM',
                                          'WCUT', 'WGR', 'WOR', 'CALCULATE_AUTODRILL_BENEFIT', 'CONCAVG', 'CONINDEX',
                                          'CONINDICES', 'CONNECTEDDOWNSTREAM', 'CONNECTEDUPSTREAM', 'CPTFRAC',
                                          'CPTFRACP', 'CPTFRACS', 'CPTFRACSP', 'CPTRATE', 'CPTRATEP', 'CPTRATES',
                                          'CPPTRATESP', 'FIP', 'GASLIFTCONNECTION', 'GET_ACTIVE_PERFS', 'GET_COND',
                                          'GET_DEST', 'GET_DESTS', 'GET_DOWNSTREAM_MANIFOLD', 'GET_DOWNSTREAM_STATION',
                                          'GET_MAX_POSITION', 'GET_METHOD', 'GET_MIN_POSITION', 'GET_NODEIN',
                                          'GET_NODEOUT', 'GET_NUM_POSITIONS', 'GET_NUMBER_OF_PATTERNS', 'GET_OUTCONS',
                                          'GET_PATTERN_BALANCE', 'GET_PATTERN_INJECTION', 'GET_PATTERN_NUMBER',
                                          'GET_PATTERN_NUMBERS', 'GET_PATTERN_PRODUCTION', 'GET_PATTERN_RESERVOIR',
                                          'GET_PATTERN_RESERVOIRS', 'GET_PATTERN_WELLS', 'GET_POSITIONS', 'GET_PROP',
                                          'GET_QMULT', 'GET_STATION', 'GET_STATION_NODES', 'GET_STATION_PARENT',
                                          'GET_STATUS', 'GET_SYSTEM', 'GET_UPSTREAM_MANIFOLD', 'GET_UPSTREAM_STATION',
                                          'GET_VELOCITY', 'GET_WAGCYCLE', 'GET_WAGNCYCLE', 'GET_WAGSLUGSIZE',
                                          'GET_WELL_PATTERN', 'GET_WELL_PROP', 'GET_WELL_STATUS', 'GET_WELL_TYPE',
                                          'GET_WELLBH_METHOD', 'GET_WELLHEADCON', 'GET_WELLHEADNODE',
                                          'HASGASLIFTCONNECTION', 'HAS_POSITION', 'IS_ACTIVATED', 'LGR', 'NODEINDEX',
                                          'NODEINDICES', 'NUMBER_OF_WELLS_BROKEN', 'NUMBER_OF_WELLS_REPAIRED', 'PAVG',
                                          'PATTERN_ACTIVE', 'PATTERN_INDEX', 'PATTERN_INDICES', 'PDATAVG', 'PDATHCAVG',
                                          'PDATUM', 'PERF', 'PERF_PROP', 'PHCAVG', 'PP', 'RIGINDEX', 'RIGINDICES',
                                          'SALAVG', 'SAT', 'SATAVG', 'TAMB', 'TARGETINDEX', 'TARGETINDICES', 'TEMP',
                                          'VALVE_SETTING', 'WELLINDEX', 'WELLINDICES']


NEXUS_PROC_CHANGE_NETWORK_DATA_FUNS = ['ABANDON', 'ACTIVATE', 'ACTIVATE_NEXT', 'AUTODRILL', 'CONSTRAINT', 'DEACTIVATE',
                                       'DEACTIVATE_NEXT', 'DRILL', 'GLR_SHUT', 'NEXT_METHOD', 'QMULT', 'REDRILL',
                                       'RESET_RESERVOIR', 'SELECT_CON', 'SET_CONPARAM', 'SET_COND', 'SET_CONTEST',
                                       'SET_DEST', 'SET_METHOD', 'SET_PATTERN_BALANCE', 'SET_PDCORR', 'SET_PROP',
                                       'SET_RESERVOIR', 'SET_SERIES_METHOD', 'SET_STATION', 'SET_SYSTEM', 'SET_TAMB',
                                       'SET_TARGET', 'SET_TGTCON', 'SET_VALVE_SETTING', 'SET_WAGPARAM',
                                       'SET_WELL_METHOD', 'SET_WELL_PROP', 'SET_WELL_SERIES_METHOD', 'SHUTIN',
                                       'SOLVE_NETWORK', 'SOLVE_NETWORK_POTENTIAL', 'SOLVE_PARTIAL_POTENTIAL',
                                       'SOLVE_WELL_POTENTIAL', 'TEST_CON', 'TEST_WELL', 'UPDATE_NETWORK_CONFIG', 'WAG',
                                       'WCUTBACK', 'WELL_VALVE', 'WCUT_SHUT', 'WGR_SHUT', 'WOR_SHUT', 'WORKOVER',
                                       'WPLUG']


NEXUS_PROC_MANIP_LISTS_FUNCS = ["FILTER", "INTERSECT", "MASK", "UNION", "SORT"]

NEXUS_ALL_PROC_FUNCS = (NEXUS_PROC_BASIC_FUNCS + NEXUS_PROC_PRINT_FUNCS + NEXUS_PROC_MANIP_LISTS_FUNCS +
                        NEXUS_PROC_RETRIEVE_NETWORK_DATA_FUNCS + NEXUS_PROC_CHANGE_NETWORK_DATA_FUNS)
