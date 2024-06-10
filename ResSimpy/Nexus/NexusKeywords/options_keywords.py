# TODO: Not a complete list. Check manual for missing keywords.
# TODO: Delete the keywords that are not tokens (i.e. that are only values in a table)

OPT_KEYWORDS_VALUE_FLOAT = ['PSTD', 'TSTD', 'RES_TEMP', 'MWOIL', 'MWGAS', 'MWOIL_L', 'MWOIL_H', 'DEF_DATUM',
                            'FUG_XY_TOL']
OPT_SINGLE_KEYWORDS = ['IRF_REPORT', 'LGRSTATIC', 'ZOLTAN']
OPT_ARRAY_KEYWORDS = ['BOUNDARY_FLUXIN_SECTORS']
OPT_GLOBAL_METHOD_OVERRIDES_KEYWORDS = ['NONEQ', 'STONE1', 'STONE2', 'KROINT',
                                        'NOCHK_HYS', 'STONE1_WAT', 'STONE2_WAT', 'KRWINT',
                                        'VIP_INJ_PERF_KR_SCALING', 'NOCHK_SAL_TEMP']

OTHER_OPTIONS_KEYWORDS = ['ALL', 'AQUIFER', 'AUTO', 'CENTER', 'DATUM', 'DEF_DATUM', 'DESC', 'DP',
                          'ENDGLOBAL_METHOD_OVERRIDES', 'ENDGRIDTOPROC', 'ENDREGBLK', 'ENDREGDATA', 'ENDSUBREGIONS',
                          'EQ_LIST', 'FLEXDP', 'GLOBAL_METHOD_OVERRIDES', 'GRID', 'GRIDBLOCKS', 'GRIDTOPROC', 'INTSAT',
                          'NAME', 'NOCHK_SAL_TEMP', 'NUMBER', 'OFF', 'OVERREAD', 'PATTERN', 'PC', 'PD',
                          'POROSITY_INDEPENDENCE', 'PROCESS', 'REGBLK', 'REGDATA', 'RESERVOIR', 'SOMOPT1',
                          'STONE1', 'SUBREGION', 'SUBREGIONS', 'SW', 'VIP_INJ_PERF_KR_SCALING']

OPTIONS_KEYWORDS = OPT_KEYWORDS_VALUE_FLOAT + OPT_SINGLE_KEYWORDS + OPT_GLOBAL_METHOD_OVERRIDES_KEYWORDS \
    + OTHER_OPTIONS_KEYWORDS
