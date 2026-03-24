"""Container class for Nexus STREAM_TRACER entries."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Sequence, TYPE_CHECKING

from ResSimpy.Nexus.DataModels.Network.NexusStreamTracer import NexusStreamTracer

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass(kw_only=True)
class NexusStreamTracers:
    """Container for all :class:`NexusStreamTracer` objects parsed from STREAM_TRACER blocks.

    Also exposes a :py:attr:`component_map` property that returns a ``dict[str, str]``
    mapping each stream name (uppercased) to its declared COMPONENT, which is used by
    :class:`~ResSimpy.Nexus.NexusNetwork.NexusNetwork` to classify well types.
    """

    __stream_tracers: list[NexusStreamTracer] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        """Initialises the NexusStreamTracers class.

        Args:
            parent_network (NexusNetwork): The network that these stream tracers belong to.
        """
        self.__parent_network: NexusNetwork = parent_network
        self.__stream_tracers: list[NexusStreamTracer] = []

    def get_all(self) -> Sequence[NexusStreamTracer]:
        """Returns all loaded :class:`NexusStreamTracer` objects."""
        self.__parent_network.get_load_status()
        return self.__stream_tracers

    def get_by_name(self, name: str) -> NexusStreamTracer | None:
        """Returns the first :class:`NexusStreamTracer` whose stream name matches *name* (case-insensitive).

        Args:
            name (str): Stream name to look up.

        Returns:
            NexusStreamTracer | None: Matching object, or ``None`` if not found.
        """
        self.__parent_network.get_load_status()
        name_upper = name.upper()
        for st in self.__stream_tracers:
            if st.name is not None and st.name.upper() == name_upper:
                return st
        return None

    @property
    def component_map(self) -> dict[str, str]:
        """Returns a ``dict`` mapping stream name → component (both uppercased).

        Example::

            {'SEAWTR': 'WATER', 'TRTWTR': 'WATER', 'GASSTREAM': 'GAS'}
        """
        self.__parent_network.get_load_status()
        return {
            st.name.upper(): st.component.upper()
            for st in self.__stream_tracers
            if st.name is not None and st.component is not None
        }

    def _add_to_memory(self, stream_tracers_to_add: list[NexusStreamTracer] | None) -> None:
        """Appends a list of :class:`NexusStreamTracer` objects to the internal store."""
        if stream_tracers_to_add is None:
            return
        self.__stream_tracers.extend(stream_tracers_to_add)
