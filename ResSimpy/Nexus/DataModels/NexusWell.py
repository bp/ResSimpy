"""Class for representing a well in Nexus. Consists of a list of completions and a well name."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Sequence, Union
from uuid import UUID

from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Utils.generic_repr import generic_repr, generic_str
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Well import Well


@dataclass(kw_only=True)
class NexusWell(Well):

    def __init__(self, well_name: str, completions: Sequence[NexusCompletion], unit_system: UnitSystem) -> None:
        if not isinstance(completions, list):
            completions = list(completions)
        super().__init__(well_name=well_name, completions=completions, unit_system=unit_system)

    def __repr__(self) -> str:
        return generic_repr(self)

    def __str__(self) -> str:
        return generic_str(self)

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
        matching_completions: list[NexusCompletion] = []
        if isinstance(completion_properties, NexusCompletion):
            perf_props = completion_properties.to_dict(add_units=False)
        else:
            perf_props = completion_properties
        perf_props_without_nones = {k: v for k, v in perf_props.items() if v is not None}
        for i, perf in enumerate(self._completions):
            for prop, value in perf_props_without_nones.items():
                if getattr(perf, prop) == value:
                    # go to the next perf if a value from the dictionary doesn't match
                    continue
                else:
                    break
            else:
                if isinstance(perf, NexusCompletion):
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

    def _add_completion_to_memory(self, date: str, completion_properties: dict[str, None | float | int | str],
                                  date_format: DateFormat, completion_index: Optional[int] = None) -> NexusCompletion:
        """Adds a perforation with the properties specified in completion_properties_list,
            if index is none then adds it to the end of the perforation list.

        Args:
        ----
            date (str): date at which the perforation should be added
            completion_properties (dict[str, str | float | int]):
            completion_index (Optional[int]):
        """
        completion_properties['date'] = date
        completion_properties['unit_system'] = self.unit_system
        new_completion = NexusCompletion.from_dict(completion_properties, date_format)
        if completion_index is None:
            completion_index = len(self._completions)
        self._completions.insert(completion_index, new_completion)
        return new_completion

    def _remove_completion_from_memory(self, completion_to_remove: NexusCompletion | UUID) -> None:
        if isinstance(completion_to_remove, NexusCompletion):
            completion_to_remove = self.find_completion(completion_to_remove)
            completion_to_remove = completion_to_remove.id
        completion_index_to_remove = [x.id for x in self._completions].index(completion_to_remove)
        self._completions.pop(completion_index_to_remove)

    def _modify_completion_in_memory(self, new_completion_properties: dict[str, Union[None, float, int, str]],
                                     completion_to_modify: NexusCompletion | UUID,
                                     ) -> None:
        if isinstance(completion_to_modify, NexusCompletion):
            completion = self.find_completion(completion_to_modify)
        else:
            completion = self.get_completion_by_id(completion_to_modify)
        completion.update(new_completion_properties)

    def get_completion_by_id(self, id: UUID) -> NexusCompletion:
        """Returns the completion that matches the id provided."""
        for completion in self._completions:
            if completion.id == id and isinstance(completion, NexusCompletion):
                return completion
        raise ValueError('No completion found for id: {id}')

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
