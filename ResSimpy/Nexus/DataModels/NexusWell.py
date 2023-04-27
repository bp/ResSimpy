import warnings
from dataclasses import dataclass
from typing import Optional, Tuple, Sequence, Union

from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Utils.generic_repr import generic_repr
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

        activations = filter(NexusCompletion.completion_is_perforation, self.__completions)
        return list(activations)

    @property
    def first_perforation(self) -> Optional[NexusCompletion]:
        """Returns the first perforation for the well"""
        if len(self.perforations) == 0:
            return None

        return self.perforations[0]

    @property
    def shutins(self) -> Sequence[NexusCompletion]:
        """Returns a list of all of the shut-ins for the well"""

        shutins = filter(NexusCompletion.completion_is_shutin, self.__completions)
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
    def completion_events(self) -> list[Tuple[str, Union[int, Tuple[float, float]]]]:
        """Returns a list of dates and values representing either the layer, or the depths of each perforation"""
        events = []
        using_k_values: Optional[bool] = None

        for completion in self.__completions:
            is_perforation = NexusCompletion.completion_is_perforation(completion)
            if not is_perforation:
                continue
            if completion.k is not None and using_k_values is not False:
                using_k_values = True
                events.append((completion.date, completion.k))
            elif completion.depth_to_top is not None and using_k_values is not True:
                using_k_values = False
                events.append((completion.date, (completion.depth_to_top, completion.depth_to_bottom)))

        return events

    def add_completion(self, date: str, perforation_properties: NexusCompletion.InputDictionary,
                       perforation_index: Optional[int] = None) -> None:
        """ adds a perforation with the properties specified in perforation_properties,
            if index is none then adds it to the end of the perforation list.
        Args:
            date (str): date at which the perforation should be added
            perforation_properties (dict[str, str | float | int]):
            perforation_index (Optional[int]):
        """
        perforation_properties['date'] = date
        new_completion = NexusCompletion.from_dict(perforation_properties)
        if perforation_index is None:
            perforation_index = len(self.__completions)
        self.__completions.insert(perforation_index, new_completion)

    def find_completions(self, perforation_properties: NexusCompletion.InputDictionary | NexusCompletion) -> \
            list[NexusCompletion]:
        matching_completions = []
        if isinstance(perforation_properties, NexusCompletion):
            perforation_properties = perforation_properties.to_dict()
            perforation_properties = {k: v for k, v in perforation_properties.items() if v is not None}
        for i, perf in enumerate(self.__completions):
            for prop, value in perforation_properties.items():
                if getattr(perf, prop) == value:
                    # go to the next perf if a value from the dictionary doesn't match
                    continue
                else:
                    break
            else:
                # if all the conditions match then append the perf to completions
                matching_completions.append(perf)
        return matching_completions

    def find_completion(self,
                        perforation_properties: NexusCompletion.InputDictionary | NexusCompletion) -> NexusCompletion:
        matching_completions = self.find_completions(perforation_properties)
        if len(matching_completions) != 1:
            raise ValueError(f'Could not find single unique completion that matches property provided. Instead found: '
                             f'{len(matching_completions)} completions')
        return matching_completions[0]

    def modify_completion(self) -> None:
        pass

    def modify_completions(self) -> None:
        pass

    def remove_completions(self, date: str, perforation_properties: NexusCompletion.InputDictionary | NexusCompletion,
                           remove_all_that_match: bool = False,
                           ) -> None:
        # TODO improve comparison of dates with datetime libs
        """ Removes perforation from the completions list in the well that match all the properties in the
        provided dictionary, does not write out to model yet.
        Args:
            date (str): the date to remove the perforation from
            perforation_properties (dict[str, str | float | int]): dictionary containing key value pairs for
            the properties to match
            remove_all_that_match (bool): If True removes all the perforations that match the perforation_properties
            dictionary. Otherwise if multiple perforations match it will not remove any completions.
        """
        matching_completions = self.find_completions(perforation_properties)
        if remove_all_that_match:
            for completion in matching_completions:
                self.__completions.remove(completion)
                print(f"Removing completion {completion}")
        else:
            if len(matching_completions) == 1:
                self.__completions.remove(matching_completions[0])
            else:
                warnings.warn("No completions removed - multiple completions matched the provided properties")

    def __repr__(self):
        return generic_repr(self)
