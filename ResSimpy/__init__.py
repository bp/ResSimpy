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

__all__ = [
    "NexusSimulator",
    "OpenGoSimSimulator",
   ]
