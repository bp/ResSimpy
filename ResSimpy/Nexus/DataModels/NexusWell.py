from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Sequence, Union
from uuid import UUID

from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Utils.generic_repr import generic_repr
from ResSimpy.Well import Well


@dataclass
class NexusWell(Well):
    __completions: list[NexusCompletion]

    def __init__(self, well_name: str, completions: Sequence[NexusCompletion], units: UnitSystem) -> None:
        if not isinstance(completions, list):
            completions = list(completions)
        self.__completions: list[NexusCompletion] = completions
        super().__init__(well_name=well_name, completions=completions, units=units)

    def __repr__(self) -> str:
        return generic_repr(self)

    @property
    def perforations(self) -> Sequence[NexusCompletion]:
        """Returns a list of all of the perforations for the well."""

        activations = filter(NexusCompletion.completion_is_perforation, self.__completions)
        return list(activations)

    @property
    def first_perforation(self) -> Optional[NexusCompletion]:
        """Returns the first perforation for the well."""
        if len(self.perforations) == 0:
            return None

        return self.perforations[0]

    @property
    def shutins(self) -> Sequence[NexusCompletion]:
        """Returns a list of all of the shut-ins for the well."""

        shutins = filter(NexusCompletion.completion_is_shutin, self.__completions)
        return list(shutins)

    @property
    def last_shutin(self) -> Optional[NexusCompletion]:
        """Returns the last shut-in for the well in the Wellspec file."""
        if len(self.shutins) == 0:
            return None

        return self.shutins[-1]

    @property
    def dates_of_completions(self) -> list[str]:
        """Returns a list of dates that the well was changed using a completion."""

        dates_changed: list[str] = []
        for completion in self.__completions:
            if completion.date not in dates_changed:
                dates_changed.append(completion.date)

        return dates_changed

    @property
    def printable_well_info(self) -> str:
        """Returns some printable well information in string format."""
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
    def completion_events(self) -> list[tuple[str, Union[int, tuple[float, float]]]]:
        """Returns a list of dates and values representing either the layer, or the depths of each perforation."""
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

    def find_completions(self, completion_properties:  dict[str, None | float | int | str] | NexusCompletion) -> \
            list[NexusCompletion]:
        """Returns a list of all completions that match the completion properties provided.

        Args:
        ----
            completion_properties (dict | NexusCompletion): keys as the attributes and values as the value to match \
            from the well.

        Returns:
        -------
            list[NexusCompletion] that match the completion properties provided
        """
        matching_completions = []
        if isinstance(completion_properties, NexusCompletion):
            perf_props = completion_properties.to_dict(add_units=False)
        else:
            perf_props = completion_properties
        perf_props_without_nones = {k: v for k, v in perf_props.items() if v is not None}
        for i, perf in enumerate(self.__completions):
            for prop, value in perf_props_without_nones.items():
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
                        completion_properties: dict[str, None | float | int | str] | NexusCompletion) \
            -> NexusCompletion:
        """Returns precisely one completion which matches all the properties provided.
            If several completions match it raise a ValueError.

        Args:
        ----
            completion_properties (dict | NexusCompletion):

        Returns:
        -------
            NexusCompletion that matches all completion properties provided.
        """
        matching_completions = self.find_completions(completion_properties)
        if len(matching_completions) != 1:
            raise ValueError(f'Could not find single unique completion that matches property provided. Instead found: '
                             f'{len(matching_completions)} completions')
        return matching_completions[0]

    def get_completion_by_id(self, id: UUID) -> NexusCompletion:
        """Returns the completion that matches the id provided."""
        for completion in self.__completions:
            if completion.id == id:
                return completion
        raise ValueError('No completion found for id: {id}')

    def _add_completion_to_memory(self, date: str, completion_properties: dict[str, None | float | int | str],
                                  completion_index: Optional[int] = None) -> NexusCompletion:
        """Adds a perforation with the properties specified in completion_properties_list,
            if index is none then adds it to the end of the perforation list.

        Args:
        ----
            date (str): date at which the perforation should be added
            completion_properties (dict[str, str | float | int]):
            completion_index (Optional[int]):
        """
        completion_properties['date'] = date
        new_completion = NexusCompletion.from_dict(completion_properties)
        if completion_index is None:
            completion_index = len(self.__completions)
        self.__completions.insert(completion_index, new_completion)
        return new_completion

    def _remove_completion_from_memory(self, completion_to_remove: NexusCompletion | UUID) -> None:
        if isinstance(completion_to_remove, NexusCompletion):
            completion_to_remove = self.find_completion(completion_to_remove)
            completion_to_remove = completion_to_remove.id
        completion_index_to_remove = [x.id for x in self.__completions].index(completion_to_remove)
        self.__completions.pop(completion_index_to_remove)

    def _modify_completion_in_memory(self, new_completion_properties: dict[str, Union[None, float, int, str]],
                                     completion_to_modify: NexusCompletion | UUID,
                                     ) -> None:
        if isinstance(completion_to_modify, NexusCompletion):
            completion = self.find_completion(completion_to_modify)
        else:
            completion = self.get_completion_by_id(completion_to_modify)
        completion.update(new_completion_properties)

    def _modify_completions_in_memory(self, new_completion_properties: dict[str, Union[None, float, int, str]],
                                      completions_to_modify: list[NexusCompletion | UUID]) -> None:
        for completion in completions_to_modify:
            if isinstance(completion, UUID):
                modify_this_completion = self.get_completion_by_id(completion)
                modify_this_completion.update(new_completion_properties)
            else:
                completion.update(new_completion_properties)

    def _remove_completions_from_memory(self, completions_to_remove: Sequence[NexusCompletion | UUID]) -> None:
        # TODO improve comparison of dates with datetime libs
        """Removes completions from a list of completions or completion IDs
        Args:
            completions_to_remove (list[NexusCompletion | UUID]): Completions to be removed.
        """
        for completion in completions_to_remove:
            self._remove_completion_from_memory(completion)
