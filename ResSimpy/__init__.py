"""A library to help read and manipulate input decks for reservoir simulators.

.. autosummary::
    :toctree: _autosummary
    :caption: API Reference
    :template: custom-module-template.rst
    :recursive:

    Nexus
    Utils
    Enums
"""

__version__ = "0.0.0"  # Set at build time

from ResSimpy.Nexus.NexusSimulator import NexusSimulator
from ResSimpy.OpenGoSim.OpenGoSimSimulator import OpenGoSimSimulator

# Useful regularly used objects
from ResSimpy.Time.ISODateTime import ISODateTime
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat


__all__ = [
    "NexusSimulator",
    "OpenGoSimSimulator",
    "ISODateTime",
    "UnitSystem",
    "DateFormat",
   ]
