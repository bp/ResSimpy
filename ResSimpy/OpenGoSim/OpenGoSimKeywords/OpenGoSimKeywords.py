# TODO: complete these lists

GENERAL_KEYWORDS = ['DATE', ' TIME', 'END']

# TODO: GRDECL KEYWORDS E.G DX, PERMX, ZCORN ETC

GRID_KEYWORDS = ['TYPE']

SIMULATION_KEYWORDS = ['MODE', 'ISOTHERMAL', 'NOSLVSOL', 'NOGASSOL', 'RESERVOIR_DEFAULTS', 'ANALYTICAL_JACOBIAN',
                       'HYSTERESIS', 'HYSTERESIS_PC', 'EHYST', 'RESTART', 'ERESTART', 'CHECKPOINT', 'TL_OMEGA',
                       'COMP_DEP_SFNS', 'STRAND', 'ABOUT', 'PREAMBLE', 'FLOWS', 'SATDEN', 'OPTIONS', 'MISCIBLE',
                       'LOCAL_DIAGONAL_TENSOR']

OUTPUT_KEYWORDS = ['MASS_BALANCE_FILE', 'PERIODIC TIMESTEP', 'PERIOD_SUM TIMESTEP', 'PERIOD_RST TIMESTEP',
                   'WRITE_DENSITY', 'LINEREPT', 'SOLUTION_MONITOR', 'TIME_UNITS', 'OUTFILE']

MATERIAL_PROP_KEYWORDS = ['ID', 'CHARACTERISTIC_CURVES', 'ROCK_COMPRESSIBILITY', 'ROCK_REFERENCE_PRESSURE',
                          'ROCK_COMPRESSIBILITY_FUNCTION', 'ROCK_DENSITY', 'SPECIFIC_HEAT', 'THERMAL_CONDUCTIVITY_DRY',
                          'THERMAL_CONDUCTIVITY_WET', 'SOIL_COMPRESSIBIITY', 'SOIL_REFERENCE_PRESSURE', 'TORTUOSITY']

# TODO: ANALYTIC APPROACH KEYWORDS ALTHOUGH TABLES IS PROBABLY MOST COMMON COVERED BY BELOW

SAT_FUNCTIONS_KEYWORDS = ['TABLE', 'PRESSURE_UNITS', 'SWFN', 'SGFN', 'SGFN', 'SGSFN', 'SOF2', 'SOF3']

EOS_KEYWORDS = ['WATER', 'OIL', 'GAS', 'SOLVENT', 'COMP', 'SURFACE_DENSITY', 'FORMULA_WEIGHT', 'DATABASE',
                'PREOS', 'SRKEOS', 'CNAME', 'TCRIT', 'PCRIT', 'ZCRIT', 'ZMF', 'ACF', 'PRCORR', 'MW', 'SHIFT',
                'OMEGAA', 'OMEGAB', 'BIC', 'GCOND', 'PARACHOR']

WELLS_KEYWORDS = ['WELL_TYPE', 'OPEN', 'SHUT', 'RADIUS', 'DIAMETER', 'USE_HIST_TARG', 'CIJK_D', 'CIJKL_D',
                  'SKIN_FACTOR', 'EFFECTIVE_KH', 'PRESSURE_RADIUS_R0', 'CONST_DRILL_DIR', 'BHPL', 'D_REF',
                  'Z_REF', 'INJECTION_ENTHALPY_P', 'INJECTION_ENTHALPY_T', 'ZINJ', 'MULTI_PI', 'GC_WEIGHT']

AQUIFER_KEYWORDS = ['BACKFLOW', 'DEPTH', 'ZAQUIFER', 'THETA_FRACTION', 'THETA', 'THICKNESS', 'WIDTH', 'RADIUS',
                    'PERM', 'PERMEABILITY', 'CMPR', 'COMPRESSIBILITY', 'PORO', 'POROSITY', 'VISC', 'VISCOSITY',
                    'PINIT', 'PRESSURE', 'TINIT', 'TEMPERATURE', 'GAS_IN_LIQUID_MOLE_FRACTION', 'IFT',
                    'CONN_D', 'CONN_Z', 'FET', 'PV', 'PI']

EQUILIBRATION_KEYWORDS = ['DATUM_D', 'PRESSURE', 'WGC_D', 'PCWG_WGC', 'OWC_D', 'PCOW_OWC', 'OGC_D', 'PCOG_OGC',
                          'BUBBLE_POINT_TABLE', 'RTEMP', 'TEMPERATURE_TABLE', 'SALT_TABLE',
                          'GAS_IN_LIQUID_MOLE_FRACTION', 'SOLVENT_IN_LIQUID_MOLE_FRACTION', 'ZMFVD',
                          'NUM_EQUIL_NODES']

OPENGOSIM_KEYWORDS = GENERAL_KEYWORDS + SIMULATION_KEYWORDS + OUTPUT_KEYWORDS + MATERIAL_PROP_KEYWORDS + \
                     SAT_FUNCTIONS_KEYWORDS + EOS_KEYWORDS + WELLS_KEYWORDS + AQUIFER_KEYWORDS + \
                     EQUILIBRATION_KEYWORDS
