from dataclasses import dataclass
from typing import Optional, Tuple, Sequence

from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Well import Well


@dataclass
class NexusWell(Well):
    __completions: list[NexusCompletion]

    def __init__(self, well_name: str, completions: list[NexusCompletion], units: UnitSystem):
        self.__completions = completions
        super().__init__(well_name=well_name, completions=completions, units=units)

    @property
    def perforations(self) -> Sequence[NexusCompletion]:
        """Returns a list of all of the perforations for the well"""

        def completion_is_perforation(completion: NexusCompletion):
            # If we don't have any non-none values for these properties, no perforation present
            if completion.partial_perf is None and completion.well_indices is None and completion.status is None:
                return False

            return ((completion.partial_perf is None or completion.partial_perf > 0) and
                    (completion.well_indices is None or completion.well_indices > 0) and
                    (completion.status != 'OFF'))

        activations = filter(completion_is_perforation, self.__completions)
        return list(activations)

    @property
    def first_perforation(self) -> Optional[NexusCompletion]:
        """Returns the first perforation for the well"""
        if len(self.perforations) == 0:
            return None

        return self.perforations[0]

    @staticmethod
    def completion_is_shutin(completion: NexusCompletion):
        # If we don't have any non-none values for these properties, assume this is a shutin
        if completion.partial_perf is None and completion.well_indices is None and completion.status is None:
            return True

        return completion.partial_perf == 0 or completion.well_indices == 0 or completion.status == 'OFF'

    @property
    def shutins(self) -> Sequence[NexusCompletion]:
        """Returns a list of all of the shut-ins for the well"""

        shutins = filter(self.completion_is_shutin, self.__completions)
        return list(shutins)

    @property
    def last_shutin(self) -> Optional[NexusCompletion]:
        """Returns the last shut-in for the well in the Wellspec file"""
        if len(self.shutins) == 0:
            return None

        return self.shutins[-1]

    @property
    def dates_of_completions(self) -> list[str]:
        """Returns a list of dates that the well was changed using a completion"""

        dates_changed: list[str] = []
        for completion in self.__completions:
            if completion.date not in dates_changed:
                dates_changed.append(completion.date)

        return dates_changed

    @property
    def printable_well_info(self) -> str:
        """Returns some printable well information in string format"""
        printable_dates_of_completions = ", ".join(self.dates_of_completions)
        well_info = \
            f"""
    Well Name: {self.well_name}
    First Perforation: {'N/A' if self.first_perforation is None else self.first_perforation.date}
    Last Shut-in: {'N/A' if self.last_shutin is None else self.last_shutin.date}
    Dates Changed: {'N/A' if len(self.dates_of_completions) == 0 else printable_dates_of_completions}
    """

        return well_info

    @property
    def completion_events(self) -> list[Tuple[str, int]]:
        """Returns a list of dates and a boolean representing whether the well was switched on or off on that date"""
        events = []

        for completion in self.__completions:
            is_perforation = not (self.completion_is_shutin(completion))
            if is_perforation:
                events.append((completion.date, completion.k))

        return events
