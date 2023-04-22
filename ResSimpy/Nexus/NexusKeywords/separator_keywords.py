# TODO: Not a complete list. Check manual for missing keywords.
# TODO: Delete the keywords that are not tokens (i.e. that are only values in a table)

EOS_SEPARATOR_KEYWORDS = ['STAGE', 'TEMP', 'PRES', 'METHOD', 'IDL1', 'IDL2', 'IDV1', 'IDV2', 'FDL1', 'FDV1', 'IGP',
                          'WATERMETHOD']
GAS_PLANT_KEYWORDS = ['KEYCPTLIST', 'GPTNUM', 'PRES_STD', 'TEMP_STD', 'EOSMETHOD', 'WATERMETHOD', 'RECFAC_TABLE'
                      'ENDRECFAC_TABLE', 'KEYCPTMF']

BLACKOIL_SEPARATOR_KEYWORDS = ['BOSEP', 'MWOIL', 'MWGAS', 'ZOIL', 'STAGE', 'KVOIL', 'KVGAS', 'IDL1', 'IDL2', 'IDV1',
                               'IDV2', 'FDL1', 'FDV1']

SEPARATOR_KEYS_INT = ['WATERMETHOD', 'EOSMETHOD', 'GPTNUM']

SEPARATOR_KEYS_FLOAT = ['MWOIL', 'MWGAS', 'ZOIL', 'PRES_STD', 'TEMP_STD']

SEPARATOR_KEYWORDS = EOS_SEPARATOR_KEYWORDS + GAS_PLANT_KEYWORDS + BLACKOIL_SEPARATOR_KEYWORDS
