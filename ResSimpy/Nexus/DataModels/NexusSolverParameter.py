"""Data object storing the solver parameters for the Nexus Simulation runs."""

from dataclasses import dataclass

from ResSimpy.Enums.TimeSteppingMethodEnum import TimeSteppingMethod
from ResSimpy.SolverParameter import SolverParameter


@dataclass
class NexusSolverParameter(SolverParameter):
    """Data object storing the solver parameters for the Nexus Simulation runs.
    Nexus is time-dependent for the solver parameters.
    """
    date: str
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

    implicit_mbal: str | None = None

    impstab_on: bool = False  # Default is OFF
    impstab_criteria: str | None = None
    impstab_skip_mass_cfl: bool = False  # Default is USEMASSCFL
    impstab_target_cfl: float | None = None
    impstab_limit_cfl: float | None = None
    impstab_no_cuts: float | None = None
    impstab_max_cuts: float | None = None
    impstab_skip_block_dcmax: float | None = None

    gridsolver_implicit_coupling_setting: str | None = None
    gridsolver_impes_coupling_setting: str | None = None
    gridsolver_implicit_precon_setting: str | None = None
    gridsolver_cpr_pressure_equation: str | None = None
    gridsolver_press_reduction: float | None = None
    gridsolver_implicit_reduction: float | None = None
    gridsolver_grid_reduction: float | None = None

    def _write_out_solver_param_block(self):
        raise NotImplementedError

    @staticmethod
    def dt_keyword_mapping() -> dict[str, tuple[str, type]]:
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
    def keyword_mapping() -> dict[str, tuple[str, type]]:
        # DT keywords
        dt_keyword_map = NexusSolverParameter.dt_keyword_mapping()
        solver_keyword_map = NexusSolverParameter.solver_keyword_mapping()
        # Method keyword
        misc_keyword_map = {
            'METHOD': ('timestepping_method', TimeSteppingMethod),
            'IMPLICITMBAL': ('implicit_mbal', str),
        }

        # Combine the keyword maps
        keyword_map = {**dt_keyword_map, **misc_keyword_map, **solver_keyword_map}
        return keyword_map
