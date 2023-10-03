"""Enum representing Date Formats."""

from enum import Enum


class DateFormat(Enum):
    """Enum representing standard Nexus Date Formats (DATEFORMAT)."""
    DD_MM_YYYY = 1
    MM_DD_YYYY = 2
