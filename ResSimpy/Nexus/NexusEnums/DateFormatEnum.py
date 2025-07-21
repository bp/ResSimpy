"""Enum representing Date Formats."""

from enum import Enum


class DateFormat(str, Enum):
    """Enum representing standard Nexus Date Formats (DATEFORMAT)."""
    DD_MM_YYYY = 'DD/MM/YYYY'  # e.g. 14/03/1999
    MM_DD_YYYY = 'MM/DD/YYYY'  # e.g. 03/14/1999
    DD_MMM_YYYY = 'MM DDD YYYY'  # e.g. 14 MAR 1999
    DD_MM_YYYY_h_m_s = 'DD/MM/YYYY(h:m:s)'  # e.g. 14/03/1999(09:43:18)
    MM_DD_YYYY_h_m_s = 'MM/DD/YYYY(h:m:s)'  # e.g. 03/14/1999(09:43:18)
