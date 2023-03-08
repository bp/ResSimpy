# TODO: Not a complete list. Check manual for missing keywords.
# TODO: Delete the keywords that are not tokens (i.e. that are only values in a table)

PVT_TYPE_KEYWORDS = ['BLACKOIL', 'WATEROIL', 'GASWATER', 'EOS']
PVT_BLACKOIL_PRIMARY_KEYWORDS = ['DENOIL', 'API', 'GOR', 'OGR', 'DENGAS', 'SPECG', 'MWOR']
PVT_GENERAL_KEYWORDS = ['ACENTR', 'API', 'APIGROUP', 'BG', 'BGFAC', 'BINA', 'BO', 'BOFAC', 'COMPONENT',
                        'COMPONENTS', 'DENGAS', 'DENOIL', 'DP', 'ENDBINA', 'ENDPROPS', 'ENGLISH', 'EOSOPTIONS', 'FAHR',
                        'GAS', 'INCLUDE', 'LBC1', 'LBC2', 'LBC3', 'LBC4', 'LBC5', 'MOLWT', 'NHC', 'NOCHK', 'OIL',
                        'OMEGAA', 'OMEGAB', 'PC', 'PR', 'PRES', 'PROPS', 'PSAT', 'RS', 'RSSAT', 'RV', 'SATURATED',
                        'SPECG', 'TC', 'TEMP', 'UNSATGAS', 'UNSATOIL', 'VG', 'VGFAC', 'VO', 'VOFAC', 'VSHIFT', 'ZC']
PVT_KEYWORDS = PVT_TYPE_KEYWORDS + PVT_BLACKOIL_PRIMARY_KEYWORDS + PVT_GENERAL_KEYWORDS
