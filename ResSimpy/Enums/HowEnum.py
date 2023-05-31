from enum import Enum


class OperationEnum(Enum):
    """Enum for defining what operation to apply to writing to memory."""

    REMOVE = 0
    ADD = 1
    MODIFY = 2
