"""Enum representing Date Formats."""

from enum import Enum


class DateFormat(Enum):
    """Enum representing standard Nexus Date Formats (DATEFORMAT)."""
    DD_MM_YYYY = 1  # e.g. 14/03/1999
    MM_DD_YYYY = 2  # e.g. 03/14/1999
    DD_MMM_YYYY = 3  # e.g. 14 MAR 1999
    DD_MM_YYYY_h_m_s = 4  # e.g. 14/03/1999(09:43:18)
    MM_DD_YYYY_h_m_s = 5  # e.g. 03/14/1999(09:43:18)
