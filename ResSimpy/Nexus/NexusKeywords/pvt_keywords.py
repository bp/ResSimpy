# TODO: Delete the keywords that are not tokens (i.e. that are only values in a table)

PVT_TYPE_KEYWORDS = ['BLACKOIL', 'WATEROIL', 'GASWATER', 'EOS']
PVT_BLACKOIL_PRIMARY_KEYWORDS = ['DENOIL', 'API', 'GOR', 'OGR', 'DENGAS', 'SPECG', 'MWOR']
PVT_EOS_METHODS = ['PR', 'PR_OLD', 'SRK', 'RK']
PVT_EOSOPTIONS_PRIMARY_WORDS = ['ZGIBBS', 'ZGIBBS_OFF', 'FLASH_GIBBS_ON', 'FLASH_GIBBS_OFF', 'VSHIFTOFF',
                                'STKATZOFF', 'CAPILLARYFLASH', 'VISPE']
PVT_EOSOPTIONS_PRIMARY_KEYS_FLOAT = ['LI_FACT', 'LI_GAS', 'LI_GAS_TEST', 'LI_OIL', 'LI_OIL_TEST', 'TOL', 'TOLSS',
                                     'TOLCRIT', 'ALPHAMU', 'LBC1', 'LBC2', 'LBC3', 'LBC4', 'LBC5', 'LBC6']
PVT_EOSOPTIONS_PRIMARY_KEYS_INT = ['MCO2', 'FUGERR']
PVT_EOSOPTIONS_TRANS_KEYS = ['NEIGHBOR', 'TEST', 'DELTA', 'VIP', 'B', 'ALL']
PVT_EOSOPTIONS_TRANS_TEST_KEYS = ['GIBBS', 'INCRP', 'PSAT']
PVT_EOSOPTIONS_PHASEID_KEYS = ['PREVIOUS', 'DENSITY', 'FLASH', 'OIL', 'GAS', 'PSAT', 'LI']
PVT_EOSOPTIONS_TERTIARY_KEYS = ['TCRIT', 'TDELZ', 'TDELP', 'PHASEFRAC', 'THRESHOLD']
PVT_TABLES_WITH_ENDWORDS = ['PROPS', 'BINA', 'PEDTUNE', 'VISKJ', 'VISKK', 'VISKKIJ']
PVT_TABLES_WITHOUT_ENDWORDS = ['SATURATED', 'OIL', 'GAS']
PVT_TABLE_KEYWORDS = PVT_TABLES_WITHOUT_ENDWORDS + PVT_TABLES_WITH_ENDWORDS
PVT_UNSAT_TABLE_KEYWORDS = ['UNSATOIL', 'UNSATGAS']
PVT_UNSAT_TABLE_INDICES = ['PSAT', 'RSSAT', 'PRES']
PVT_ALL_TABLE_KEYWORDS = PVT_TABLE_KEYWORDS + PVT_UNSAT_TABLE_KEYWORDS
PVT_GENERAL_KEYWORDS = ['ACENTR', 'API', 'APIGROUP', 'BG', 'BGFAC', 'BINA', 'BO', 'BOFAC', 'COMPONENT',
                        'COMPONENTS', 'DENGAS', 'DENOIL', 'DP', 'ENDBINA', 'ENDPROPS', 'ENGLISH', 'EOSOPTIONS',
                        'FAHR', 'GAS', 'INCLUDE', 'MOLWT', 'NHC', 'NOCHK', 'OIL', 'TRANSITION',
                        'TRANS_OPTIMIZATION' + 'TRANS_TEST', 'OMEGAA', 'OMEGAB', 'PC', 'PR', 'PRES', 'PROPS',
                        'PSAT', 'RS', 'RSSAT', 'RV', 'SATURATED', 'SPECG', 'TC', 'TEMP', 'UNSATGAS', 'UNSATOIL',
                        'VG', 'VGFAC', 'VO', 'VOFAC', 'VSHIFT', 'ZC']
PVT_KEYWORDS = PVT_TYPE_KEYWORDS + PVT_BLACKOIL_PRIMARY_KEYWORDS + PVT_EOS_METHODS + PVT_EOSOPTIONS_PRIMARY_WORDS + \
               PVT_EOSOPTIONS_PRIMARY_KEYS_FLOAT + PVT_EOSOPTIONS_PRIMARY_KEYS_INT + PVT_EOSOPTIONS_TRANS_KEYS + \
               PVT_ALL_TABLE_KEYWORDS + \
               PVT_EOSOPTIONS_TRANS_TEST_KEYS + PVT_EOSOPTIONS_PHASEID_KEYS + PVT_EOSOPTIONS_TERTIARY_KEYS + PVT_GENERAL_KEYWORDS
