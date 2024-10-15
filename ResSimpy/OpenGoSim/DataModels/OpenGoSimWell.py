from dataclasses import dataclass
from typing import Sequence, Optional

from ResSimpy.DataModelBaseClasses.Completion import Completion
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Enums.WellTypeEnum import WellType
from ResSimpy.OpenGoSim.DataModels.OpenGoSimCompletion import OpenGoSimCompletion
from ResSimpy.DataModelBaseClasses.Well import Well


@dataclass(kw_only=True)
class OpenGoSimWell(Well):

    def __init__(self, well_name: str, completions: Sequence[Completion], well_type: WellType) -> None:
        """Initialises the OpenGoSimWell class.

        Args:
            well_name (str): The name of the well.
            completions (Sequence[Completion]): The completions of the well.
            well_type (WellType): The type of the well as a WellType Enum.
        """
        if not isinstance(completions, list):
            completions = list(completions)

        super().__init__(well_name=well_name, completions=completions, unit_system=UnitSystem.ENGLISH,
                         well_type=well_type)

    @property
    def printable_well_info(self) -> str:
        """Returns some printable well information in string format."""
        printable_dates_of_completions = ", ".join(self.dates_of_completions)
        well_info = \
            f"""
Well Name: {self.well_name}
Well Type: {self.well_type.value if self.well_type is not None else 'Error: No well type defined'}
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

            completion_string = completion.__repr__()

            # Add the open and shut dates for the completion
            matching_future_completions = [x for x in self.completions if x.i == completion.i and
                                           x.j == completion.j and x.k == completion.k
                                           and isinstance(x, OpenGoSimCompletion)]

            existing_status: Optional[bool] = None
            for matching_completion in matching_future_completions:
                if matching_completion.completion_is_perforation != existing_status:
                    status_string = 'Opened' if matching_completion.is_open else 'Shut'
                    completion_string += f" | {status_string} on {matching_completion.date}"
                    existing_status = matching_completion.completion_is_perforation

            completions_string += completion_string + '\n'
            previous_completions.append(completion)

        return completions_string
