from dataclasses import dataclass
from typing import Sequence

from ResSimpy.Completion import Completion
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Enums.WellTypeEnum import WellType
from ResSimpy.OpenGoSim.DataModels.OpenGoSimCompletion import OpenGoSimCompletion
from ResSimpy.Well import Well


@dataclass(kw_only=True)
class OpenGoSimWell(Well):
    __well_type: WellType

    def __init__(self, well_name: str, completions: Sequence[Completion], well_type: WellType) -> None:
        self.__well_type = well_type
        if not isinstance(completions, list):
            completions = list(completions)

        super().__init__(well_name=well_name, completions=completions, unit_system=UnitSystem.ENGLISH)

    @property
    def well_type(self) -> WellType:
        """The Well Type."""
        return self.__well_type

    @property
    def printable_well_info(self) -> str:
        """Returns some printable well information in string format."""
        printable_dates_of_completions = ", ".join(self.dates_of_completions)
        well_info = \
            f"""
Well Name: {self.well_name}
Well Type: {self.well_type}
Completions:
{self.__get_completions_string()}
Dates well is Changed: {'N/A' if len(self.dates_of_completions) == 0 else printable_dates_of_completions}
"""

        return well_info

    def __get_completions_string(self) -> str:
        completions_string = ''
        previous_completions: list[Completion] = []
        for completion in self.completions:
            matching_previous_completions = [x for x in previous_completions if x.i == completion.i and
                                             x.j == completion.j and x.k == completion.k]

            # If we have already handled this completion, don't add it again.
            if len(matching_previous_completions) > 0:
                continue

            completion_string = completion.__repr__()  # + f" {completion.is_open} on {completion.date}"

            # Add the open and shut dates for the completion
            matching_future_completions = [x for x in self.completions if x.i == completion.i and
                                           x.j == completion.j and x.k == completion.k
                                           and isinstance(x, OpenGoSimCompletion)]

            for matching_completion in matching_future_completions:
                completion_string += f" |{'Opened' if matching_completion.is_open else 'Shut'} on \
                {matching_completion.date}"

            completions_string += completion_string + '\n'
            previous_completions.append(completion)

        return completions_string
