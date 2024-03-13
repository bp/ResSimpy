from enum import Enum


class GridFunctionTypeEnum(Enum):
    """Enum representing the different grid function types."""
    POLYN = 'POLYN'
    ABS = 'ABS'
    EXP = 'EXP'
    EXP10 = 'EXP10'
    LOG = 'LOG'
    LOG10 = 'LOG10'
    SQRT = 'SQRT'
    GE = 'GE'
    LE = 'LE'
    ADD = 'ADD'
    SUBT = 'SUBT'
    DIV = 'DIV'
    MULT = 'MULT'
    MIN = 'MIN'
    MAX = 'MAX'
    FUNCTION_TABLE = 'FUNCTION_TABLE'
