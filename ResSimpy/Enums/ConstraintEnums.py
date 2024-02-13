from enum import Enum


class ConstraintControlMode(str, Enum):
    """Enum representing the control mode for a constraint."""
    ORAT = 'ORAT'
    WRAT = 'WRAT'
    GRAT = 'GRAT'
    LRAT = 'LRAT'
    CRAT = 'CRAT'
    RESV = 'RESV'
    BHP = 'BHP'
    THP = 'THP'
