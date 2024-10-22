"""Data object storing the solver parameters at a given datetime for the Simulation runs."""
from dataclasses import dataclass
from abc import ABC


@dataclass
class SolverParameter(ABC):
    """Abstract Data object storing the solver parameters at a given datetime for the Simulation runs.

    Stored as a datetime dependent object as some sims can change these parameters with time.
    """
    date: str
