# TODO: Not a complete list. Check manual for missing keywords.
# TODO: Delete the keywords that are not tokens (i.e. that are only values in a table)

RUNCONTROL_KEYWORDS = ['2PHASE', 'ADJUSTTOTIME', 'ALL', 'ALLOW', 'AQFLUX', 'ARRAYS', 'AUTO', 'AVGSG', 'AVGSO', 'AVGSW',
                       'BG', 'BHP', 'BOF', 'CGFLUX', 'CGI', 'CGLG', 'CGP', 'CLP', 'COFLUX', 'COMP', 'CONCENTRATION',
                       'CONNECTFILE', 'COP', 'CPR_PRESSURE_EQUATION', 'CRGI', 'CRGP', 'CROP', 'CRWI', 'CRWP', 'CWFLUX',
                       'CWI', 'CWP', 'DATE', 'DATEFORMAT', 'DCMAX', 'DD/MM/YYYY', 'DEBUG', 'DEN', 'DEPTHTAB',
                       'DISALLOW', 'DRDN', 'DRMX', 'DRSDT', 'DSGLIM', 'DSLIM', 'DT', 'DUAL_SOLVER', 'DVOLLIM', 'DZLIM',
                       'END', 'ENDDEBUG', 'ENDGRIDS', 'ENDMAPOUT', 'ENDOUTPUT', 'ENDOUTSTART', 'ENDPLOTOUT',
                       'ENDPOINTS', 'ENDREGIONOUT', 'ENDSPREADSHEET', 'ENDSSOUT', 'EQUILREGION', 'EXTENDED',
                       'FACILITIES', 'FIELD', 'FIELDPLOT', 'FREEGAS', 'FREQ', 'FULLMAPARRAYS', 'GAS', 'GLOBALTOL',
                       'GOR', 'GRIDS', 'GRIDSOLVER', 'HYDMAX', 'HYDRAULICS', 'ILU', 'IMPES', 'IMPES_COUPLING',
                       'IMPLICIT', 'IMPLICITMBAL', 'IMPLICIT_COUPLING', 'IMPLICIT_PRECON', 'IMPSTAB', 'INPLACE',
                       'ITERATIONS', 'KMCMT', 'KR', 'LIMIT', 'LOGOUT', 'MAPBINARY', 'MAPFORM', 'MAPOUT', 'MAPS',
                       'MAPVDB', 'MASS', 'MAX', 'MAXBADNETS', 'MAXINCREASE', 'MAXNEWTONS', 'METHOD', 'MIN', 'MOB',
                       'MONTHLY', 'NAME', 'NETPLOT', 'NETSUM', 'NETWORK', 'NOCPUOUT', 'NOCUT', 'NONE', 'NORECOUT',
                       'NSC', 'OFF', 'OIL', 'ON', 'ORDER2009', 'OREC', 'OUTPUT', 'OUTSTART', 'OVERSHOOT', 'P', 'PAVH',
                       'PAVT', 'PC', 'PCELL', 'PDATUMHC', 'PDATUMT', 'PDCOR', 'PERF', 'PERFPLOT', 'PERFREV', 'PERFS',
                       'PERFTRACER', 'PI', 'PIN', 'PLOTBINARY', 'PLOTFORM', 'PLOTOUT', 'PLOTVDB', 'PMAX', 'PMIN',
                       'PNODE', 'POUT', 'PSAT', 'PV', 'PVMLT', 'QGI', 'QGLG', 'QGP', 'QLP', 'QMAXINJ', 'QMAXPROD',
                       'QOP', 'QUARTERLY', 'QWI', 'QWP', 'REGIONOUT', 'REGIONPLOT', 'REGIONS', 'RESERVOIR', 'RESTART',
                       'RFT', 'RFTFILE', 'RGI', 'RGP', 'ROCK', 'ROP', 'RS', 'RVG', 'RVO', 'RVPVH', 'RVPVT', 'RVW',
                       'RWI', 'RWP', 'SAL', 'SAT', 'SEPARATOR', 'SOLVER', 'SPREADSHEET', 'SSCSV', 'SSNOSORT', 'SSOUT',
                       'SSTAB', 'START', 'STAT', 'STGIP', 'STOIP', 'STOP', 'STREAMCALC', 'STWIP', 'SW', 'TARGETPLOT',
                       'TARGETS', 'TC', 'THP', 'TIME', 'TIMES', 'TNEXT', 'TOLS', 'TOTAL', 'TRANS', 'TSNUM', 'VIPUNITS',
                       'VISC', 'VOLCON', 'WATER', 'WCUT', 'WELL', 'WELLPLOT', 'WELLS', 'WOR', 'WPAVE', 'WPPV', 'WPWBC',
                       'X', 'Y', 'YEARLY', 'Z']

# Keywords that follow DT in the runctrl file
DT_KEYWORDS = ['AUTO', 'MIN', 'MAX', 'MAXINCREASE', 'CON', 'VIPTS', 'QMAXPROD', 'QMAXINJ', 'CONNOPEN', 'MAXINCAFCUT',
               'ADJUSTTOTIME', 'REDUCEAFCUT', 'WCYCLE', 'GCYCLE', 'VIP_MAXINCREASE', 'VIP_MAXINCAFCUT']

# Keywords that follow DCMAX, DCRPT, D*_MAX_VIP, VOLRPT in the runctrl file
DCMAX_KEYWORDS = ['IMPES', 'IMPLICIT', 'ALL']

# Keywords that are found on their own with a token/value pair in the runctrl file
SOLO_KEYWORDS = ['MAXNEWTONS', 'MAXBADNETS', 'CUTFACTOR', 'NEGMASSCUT', 'DVOLLIM', 'DZLIM', 'DSLIM', 'DPLIM', 'DMOBLIM',
                 'DSGLIM', 'NEGFLOWLIM', 'NEGMASSAQU', 'KRDAMP', 'VOLERR_PREV', 'SGCTOL', 'EGSGTOL', 'SGCPERFTOL',
                 'LINE_SEARCH', 'PERFP_DAMP']

# Keywords that follow IMPSTAB in the runctrl file
IMPSTAB_KEYWORDS = ['OFF', 'ON', 'COATS', 'PEACEMAN', 'SKIPMASSCFL', 'USEMASSCFL',
                    'TARGETCFL', 'LIMITCFL', 'NOCUTS', 'MAXCUTS', 'SKIPBLOCKDCMAX']

# Keywords that follow TOLS in the runctrl file
TOLS_KEYWORDS = ['VOLCON', 'MASS', 'TARGET', 'WELLMBAL', 'PERF']

PERFREV_KEYWORDS = ['ALLOW', 'ALLOWALL', 'DISALLOW']

IMPLICITMBAL_KEYWORDS = ['OFF', 'ON', 'NEGMOB', 'NEGMASS', 'VBAL', 'NOVBAL']

# Keywords following SOLVER in the runctrl file
SOLVER_KEYWORDS = ['RESERVOIR', 'GLOBAL', 'ALL', 'CYCLELENGTH', 'MAXCYCLES', 'GLOBALTOL', 'ITERATIVE', 'DIRECT',
                   'NOCUT', 'CUT', 'PRECON_ILU', 'PRECON_AMG', 'PRECON_AMG_RS', 'DUAL_SOLVER', 'SYSTEM_REDUCED',
                   'NBAD', 'PRESSURE_COUPLING', 'KSUB_METHOD', 'FACILITIES', 'PSEUDO_SLACK', 'MUMPS_SOLVER']

SOLVER_SCOPE_KEYWORDS = ['RESERVOIR', 'GLOBAL', 'ALL']
SOLVER_SCOPED_KEYWORDS = ['CYCLELENGTH', 'MAXCYCLES', 'GLOBALTOL', 'ITERATIVE', 'DIRECT']

# Keywords following GRIDSOLVER in the runctrl file
GRIDSOLVER_KEYWORDS = ['IMPLICIT_COUPLING', 'IMPES_COUPLING', 'IMPLICIT_PRECON', 'CPR_PRESSURE_EQUATION', 'PRESS_RED',
                       'IMPLICIT_RED', 'GRID_RED']

MAX_CHANGE_KEYWORDS = ['DCMAX', 'DCRPT', 'VOLRPT', 'DZMAX_VIP', 'DPMAX_VIP', 'DSMAX_VIP', 'DVMAX_VIP', 'DCRPT_VIP']
