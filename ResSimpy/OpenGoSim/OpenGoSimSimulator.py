from dataclasses import dataclass
from typing import Optional

from ResSimpy.OpenGoSim.Enums.SimulationTypeEnum import SimulationType
from ResSimpy.OpenGoSim.OpenGoSimWells import OpenGoSimWells
from ResSimpy.Simulator import Simulator


@dataclass(kw_only=True)
class OpenGoSimSimulator(Simulator):
    __simulation_type: SimulationType

    def __init__(self, origin: str):
        self._origin = origin
        self._wells: OpenGoSimWells = OpenGoSimWells()

        self.load_model()

    @property
    def simulation_type(self) -> SimulationType:
        return self.__simulation_type

    def load_model(self) -> None:
        """Loads the full OGS model"""
        pass

    @staticmethod
    def get_fluid_type(surface_file_name: str) -> str:
        raise NotImplementedError("Not implemented for OGS yet")

    def set_output_path(self, path: str) -> None:
        raise NotImplementedError("Not implemented for OGS yet")

    def get_date_format(self) -> str:
        """Returns date format as a string."""
        raise NotImplementedError("Not implemented for OGS yet")

    def write_out_new_model(self, new_location: str, new_model_name: str) -> None:
        """Writes out a new version of the model to the location supplied.

        Args:
        new_location (str): Path to write the contents of the model to.
        """
        raise NotImplementedError("Not implemented for OGS yet")
