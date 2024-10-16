"""Data object storing the solver parameters for the Nexus Simulation runs."""

from dataclasses import dataclass

from ResSimpy.Enums.TimeSteppingMethodEnum import TimeSteppingMethod
from ResSimpy.DataModelBaseClasses.SolverParameter import SolverParameter


@dataclass(kw_only=True)
class NexusSolverParameter(SolverParameter):
    """Data object storing the solver parameters for the Nexus Simulation runs.

    Nexus is time-dependent for the solver parameters.
    """

    # Time Stepping options
    timestepping_method: TimeSteppingMethod | None = None
    dt_auto: float | None = None
    dt_min: float | None = None
    dt_max: float | None = None
    dt_max_increase: float | None = None
    dt_con: float | None = None
    dt_vipts: float | None = None
    dt_qmaxprod: float | None = None
    dt_qmaxinj: float | None = None
    dt_connopen: float | None = None
    dt_maxincafcut: float | None = None
    dt_adjusttotime: float | None = None
    dt_reduceafcut: float | None = None
    dt_wcycle: float | None = None
    dt_gcycle: float | None = None
    dt_vip_maxincrease: float | None = None
    dt_vip_maxincafcut: float | None = None

    # Solver Options for grid/specific reservoir/all
    solver_reservoir_cycle_length: float | None = None
    solver_reservoir_max_cycles: float | None = None
    solver_reservoir_globaltol: float | None = None
    solver_reservoir_equation_solver: str | None = None
    solver_global_cycle_length: float | None = None
    solver_global_max_cycles: float | None = None
    solver_global_globaltol: float | None = None
    solver_global_equation_solver: str | None = None
    solver_all_cycle_length: float | None = None
    solver_all_max_cycles: float | None = None
    solver_all_globaltol: float | None = None
    solver_all_equation_solver: str | None = None

    # Independent Solver options and settings
    solver_timestep_cut: bool = True  # Default is CUT
    solver_precon: str | None = None
    solver_precon_setting: str | None = None
    solver_precon_value: float | None = None
    solver_facilities: str | None = None
    solver_ksub_method: str | None = None
    solver_dual_solver: bool = True  # Default is ON
    solver_system_reduced: bool = True  # Default is ON
    solver_nbad: float | None = None
    solver_pressure_coupling: str | None = None
    solver_pseudo_slack: bool | None = None
    solver_mumps_solver: str | None = None

    # Material balance options
    implicit_mbal: str | None = None

    # Implicit stability (IMPSTAB) options
    impstab_on: bool = False  # Default is OFF
    impstab_criteria: str | None = None
    impstab_skip_mass_cfl: bool = False  # Default is USEMASSCFL
    impstab_target_cfl: float | None = None
    impstab_limit_cfl: float | None = None
    impstab_no_cuts: float | None = None
    impstab_max_cuts: float | None = None
    impstab_skip_block_dcmax: float | None = None

    # Gridsolver options
    gridsolver_implicit_coupling_setting: str | None = None
    gridsolver_impes_coupling_setting: str | None = None
    gridsolver_implicit_precon_setting: str | None = None
    gridsolver_cpr_pressure_equation: str | None = None
    gridsolver_press_reduction: float | None = None
    gridsolver_implicit_reduction: float | None = None
    gridsolver_grid_reduction: float | None = None

    # PERFREV options
    perfrev: str | None = None

    # maximum change and other settings for the simulation
    maxnewtons: float | None = None
    maxbadnets: float | None = None
    cutfactor: float | None = None
    negmasscut: float | None = None
    dvollim: float | None = None
    dzlim: float | None = None
    dslim: float | None = None
    dplim: float | None = None
    dmoblim: float | None = None
    dsglim: float | None = None
    negflowlim: float | None = None
    negmassaqu: float | None = None
    krdamp: float | None = None
    volerr_prev: float | None = None
    sgctol: float | None = None
    egsgtol: float | None = None
    sgcperftol: float | None = None
    line_search: float | None = None
    perfp_damp: float | None = None

    # tolerances
    tols_volcon: float | None = None
    tols_mass: float | None = None
    tols_target: float | None = None
    tols_wellmbal: float | None = None
    tols_perf: float | None = None

    # settings for implicit, impes grids.
    dcmax_implicit: float | None = None
    dcmax_impes: float | None = None
    dcmax_all: float | None = None

    dcrpt_implicit: float | None = None
    dcrpt_impes: float | None = None
    dcrpt_all: float | None = None

    volrpt_implicit: float | None = None
    volrpt_impes: float | None = None
    volrpt_all: float | None = None

    dcrpt_vip_implicit: float | None = None
    dcrpt_vip_impes: float | None = None
    dcrpt_vip_all: float | None = None

    dzmax_vip_implicit: float | None = None
    dzmax_vip_impes: float | None = None
    dzmax_vip_all: float | None = None

    dpmax_vip_implicit: float | None = None
    dpmax_vip_impes: float | None = None
    dpmax_vip_all: float | None = None

    dvmax_vip_implicit: float | None = None
    dvmax_vip_impes: float | None = None
    dvmax_vip_all: float | None = None

    dsmax_vip_implicit: float | None = None
    dsmax_vip_impes: float | None = None
    dsmax_vip_all: float | None = None

    def _write_out_solver_param_block(self) -> None:
        """Writes out the solver parameter block for an instance of NexusSolverParameter."""
        raise NotImplementedError

    @staticmethod
    def dt_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the keyword mapping from simulator keyword to ResSimpy attribute and the type of the object.

        Associated with the DT keywords in Nexus. e.g. of the form "DT MAX 50".
        """
        # DT keywords
        dt_keyword_map: dict[str, tuple[str, type]] = {

            'AUTO': ('dt_auto', float),
            'MIN': ('dt_min', float),
            'MAX': ('dt_max', float),
            'MAXINCREASE': ('dt_max_increase', float),
            'CON': ('dt_con', float),
            'VIPTS': ('dt_vipts', float),
            'QMAXPROD': ('dt_qmaxprod', float),
            'QMAXINJ': ('dt_qmaxinj', float),
            'CONNOPEN': ('dt_connopen', float),
            'MAXINCAFCUT': ('dt_maxincafcut', float),
            'ADJUSTTOTIME': ('dt_adjusttotime', float),
            'REDUCEAFCUT': ('dt_reduceafcut', float),
            'WCYCLE': ('dt_wcycle', float),
            'GCYCLE': ('dt_gcycle', float),
            'VIP_MAXINCREASE': ('dt_vip_maxincrease', float),
            'VIP_MAXINCAFCUT': ('dt_vip_maxincafcut', float),
        }
        return dt_keyword_map

    @staticmethod
    def solver_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the keyword mapping from simulator keyword to ResSimpy attribute and the type of the object.

        Associated with the SOLVER keywords in Nexus. e.g. of the form "SOLVER ALL CYCLELENGTH 10".
        """
        # Solver keywords
        solver_keyword_map = {
            'ALL CYCLELENGTH': ('solver_all_cycle_length', float),
            'ALL MAXCYCLES': ('solver_all_max_cycles', float),
            'ALL GLOBALTOL': ('solver_all_globaltol', float),
            'ALL ITERATIVE': ('solver_all_equation_solver', str),
            'ALL DIRECT': ('solver_all_equation_solver', str),

            'RESERVOIR CYCLELENGTH': ('solver_reservoir_cycle_length', float),
            'RESERVOIR MAXCYCLES': ('solver_reservoir_max_cycles', float),
            'RESERVOIR GLOBALTOL': ('solver_reservoir_globaltol', float),
            'RESERVOIR ITERATIVE': ('solver_reservoir_equation_solver', str),
            'RESERVOIR DIRECT': ('solver_reservoir_equation_solver', str),

            'GLOBAL CYCLELENGTH': ('solver_global_cycle_length', float),
            'GLOBAL MAXCYCLES': ('solver_global_max_cycles', float),
            'GLOBAL GLOBALTOL': ('solver_global_globaltol', float),
            'GLOBAL ITERATIVE': ('solver_global_equation_solver', str),
            'GLOBAL DIRECT': ('solver_global_equation_solver', str),

            'NOCUT': ('solver_timestep_cut', bool),
            'CUT': ('solver_timestep_cut', bool),

            'PRECON_ILU': ('solver_precon', str),
            'PRECON_AMG': ('solver_precon', str),
            'PRECON_AMG_RS': ('solver_precon', str),

            'DUAL_SOLVER': ('solver_dual_solver', bool),
            'SYSTEM_REDUCED': ('solver_system_reduced', bool),
            'NBAD': ('solver_nbad', float),
            'PRESSURE_COUPLING': ('solver_pressure_coupling', str),
            'KSUB_METHOD': ('solver_ksub_method', str),
            'FACILITIES': ('solver_facilities', str),
            'PSEUDO_SLACK': ('solver_pseudo_slack', bool),
            'MUMPS_SOLVER': ('solver_mumps_solver', str),
        }
        return solver_keyword_map

    @staticmethod
    def impstab_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the keyword mapping from simulator keyword to ResSimpy attribute and the type of the object.

        Associated with the IMPSTAB keywords in Nexus. e.g. of the form "IMPSTAB TARGETCFL 0.5".
        """
        # IMPSTAB keywords
        impstab_keyword_map = {
            'OFF': ('impstab_on', bool),
            'ON': ('impstab_on', bool),
            'COATS': ('impstab_criteria', str),
            'PEACEMAN': ('impstab_criteria', str),
            'SKIPMASSCFL': ('impstab_skip_mass_cfl', bool),
            'USEMASSCFL': ('impstab_skip_mass_cfl', bool),
            'TARGETCFL': ('impstab_target_cfl', float),
            'LIMITCFL': ('impstab_limit_cfl', float),
            'NOCUTS': ('impstab_no_cuts', float),
            'MAXCUTS': ('impstab_max_cuts', float),
            'SKIPBLOCKDCMAX': ('impstab_skip_block_dcmax', float),
        }
        return impstab_keyword_map

    @staticmethod
    def gridsolver_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the keyword mapping from simulator keyword to ResSimpy attribute and the type of the object.

        Associated with the GRIDSOLVER keywords in Nexus. e.g. of the form "GRIDSOLVER PRESS_RED 0.5".
        """
        # GRIDSOLVER keywords
        gridsolver_keyword_map = {
            'IMPLICIT_COUPLING': ('gridsolver_implicit_coupling_setting', str),
            'IMPES_COUPLING': ('gridsolver_impes_coupling_setting', str),
            'IMPLICIT_PRECON': ('gridsolver_implicit_precon_setting', str),
            'CPR_PRESSURE_EQUATION': ('gridsolver_cpr_pressure_equation', str),
            'PRESS_RED': ('gridsolver_press_reduction', float),
            'IMPLICIT_RED': ('gridsolver_implicit_reduction', float),
            'GRID_RED': ('gridsolver_grid_reduction', float),
        }
        return gridsolver_keyword_map

    @staticmethod
    def solo_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the keyword mapping from simulator keyword to ResSimpy attribute and the type of the object.

        Associated with the keywords that are found on their own in a runcontrol file.".
        """
        # Solo keywords
        solo_keyword_map: dict[str, tuple[str, type]] = {
            'MAXNEWTONS': ('maxnewtons', float),
            'MAXBADNETS': ('maxbadnets', float),
            'CUTFACTOR': ('cutfactor', float),
            'NEGMASSCUT': ('negmasscut', float),
            'DVOLLIM': ('dvollim', float),
            'DZLIM': ('dzlim', float),
            'DSLIM': ('dslim', float),
            'DPLIM': ('dplim', float),
            'DMOBLIM': ('dmoblim', float),
            'DSGLIM': ('dsglim', float),
            'NEGFLOWLIM': ('negflowlim', float),
            'NEGMASSAQU': ('negmassaqu', float),
            'KRDAMP': ('krdamp', float),
            'VOLERR_PREV': ('volerr_prev', float),
            'SGCTOL': ('sgctol', float),
            'EGSGTOL': ('egsgtol', float),
            'SGCPERFTOL': ('sgcperftol', float),
            'LINE_SEARCH': ('line_search', float),
            'PERFP_DAMP': ('perfp_damp', float),
        }
        return solo_keyword_map

    @staticmethod
    def tols_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the keyword mapping from simulator keyword to ResSimpy attribute and the type of the object.

        Associated with the TOLS keywords in Nexus. e.g. of the form "TOLS VOLCON 100.5".
        """
        # TOLS keywords
        tols_keyword_map: dict[str, tuple[str, type]] = {
            'VOLCON': ('tols_volcon', float),
            'MASS': ('tols_mass', float),
            'TARGET': ('tols_target', float),
            'WELLMBAL': ('tols_wellmbal', float),
            'PERF': ('tols_perf', float),
        }
        return tols_keyword_map

    @staticmethod
    def dcmax_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the keyword mapping from simulator keyword to ResSimpy attribute and the type of the object.

        Associated with the DCMAX keywords in Nexus. e.g. of the form "DCMAX IMPES 0.5".
        """
        # DCMAX keywords
        dcmax_keyword_map: dict[str, tuple[str, type]] = {
            'IMPES': ('dcmax_impes', float),
            'IMPLICIT': ('dcmax_implicit', float),
            'ALL': ('dcmax_all', float),
        }
        return dcmax_keyword_map

    @staticmethod
    def keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the keyword mapping from simulator keyword to ResSimpy attribute and the type of the object.

        Compiled keywords for all ResSimpy attributes apart from the DCMAX keywords.
        """
        # DT keywords
        dt_keyword_map = NexusSolverParameter.dt_keyword_mapping()
        solver_keyword_map = NexusSolverParameter.solver_keyword_mapping()
        gridsolver_keyword_map = NexusSolverParameter.gridsolver_keyword_mapping()
        tols_keyword_map = NexusSolverParameter.tols_keyword_mapping()
        impstab_keyword_map = NexusSolverParameter.impstab_keyword_mapping()
        solo_keyword_map = NexusSolverParameter.solo_keyword_mapping()

        # Method keyword
        misc_keyword_map = {
            'METHOD': ('timestepping_method', TimeSteppingMethod),
            'IMPLICITMBAL': ('implicit_mbal', str),
            'PERFREV': ('perfrev', str),
        }

        # Combine the keyword maps
        keyword_map = {**dt_keyword_map, **misc_keyword_map, **solver_keyword_map, **gridsolver_keyword_map,
                       **tols_keyword_map, **impstab_keyword_map, **solo_keyword_map}
        return keyword_map

    @staticmethod
    def get_max_change_attribute_name(keyword: str, value: str) -> tuple[str, type]:
        """Keywords of the form 'DCRPT, DCMAX, D*_MAX_VIP, VOLRPT' have a different attribute name for the value.

        Args:
            keyword (str): The keyword to get the attribute for
            value (str): the value following the keyword to get the attribute for e.g. 'IMPES', 'IMPLICIT', 'ALL'

        Returns:
            str, type: The attribute name for the value, the type of the value
        """
        attribute = keyword.lower()
        return attribute+'_'+value.lower(), float
