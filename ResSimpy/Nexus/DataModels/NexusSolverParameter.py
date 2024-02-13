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
    timestepping_method: TimeSteppingMethod = TimeSteppingMethod.impes
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

    def _write_out_solver_param_block(self):
        raise NotImplementedError

    @staticmethod
    def dt_keyword_mapping() -> dict[str, tuple[str, type]]:
        # DT keywords
        dt_keyword_map = {

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
    def keyword_mapping() -> dict[str, tuple[str, type]]:
        # DT keywords
        dt_keyword_map = NexusSolverParameter.dt_keyword_mapping()

        # Method keyword
        method_keyword_map = {
            'METHOD': ('timestepping_method', TimeSteppingMethod)
        }

        # Combine the keyword maps
        keyword_map = {**dt_keyword_map, **method_keyword_map}
        return keyword_map
