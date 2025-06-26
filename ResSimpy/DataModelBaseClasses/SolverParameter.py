"""Data object storing the solver parameters at a given datetime for the Simulation runs."""

from dataclasses import dataclass
from abc import ABC
from typing import Optional


@dataclass
class SolverParameter(ABC):
    """Abstract Data object storing the solver parameters at a given datetime for the Simulation runs.

    Stored as a datetime dependent object as some sims can change these parameters with time.

    Attributes:
        date (str): The date at which these parameters are valid.
        dsrdt_limit (Optional[float]): DRSDT limit to be set.
        dsrdt_two_phases (Optional[bool]): If True, limit is only applied to cells where both oil and gas phases exist.
    """
    date: str
    drsdt_limit: Optional[float] = None
    drsdt_two_phases: Optional[bool] = None
