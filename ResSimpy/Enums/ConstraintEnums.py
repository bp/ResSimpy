from enum import Enum


class ConstraintControlMode(str, Enum):
    """Enum representing the control mode for a constraint."""
    OIL_RATE = 'ORAT'
    WATER_RATE = 'WRAT'
    GAS_RATE = 'GRAT'
    LIQUID_RATE = 'LRAT'
    COMBINED_RATE = 'CRAT'
    RESERVOIR_FLUID_RATE = 'RESV'
    BHP = 'BHP'
    THP = 'THP'
