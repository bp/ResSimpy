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
    timestepping_method: TimeSteppingMethod
    dt_auto: float | None
    dt_min: float | None
    dt_max: float | None
    dt_max_increase: float | None

    def _write_out_solver_param_block(self):
        raise NotImplementedError