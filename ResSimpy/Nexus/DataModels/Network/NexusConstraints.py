from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

import pandas as pd

from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass
class NexusConstraints:
    __constraints: list[NexusConstraint] = field(default_factory=lambda: [])

    def __init__(self, parent_network: NexusNetwork):
        self.__parent_network: NexusNetwork = parent_network
        self.__constraints: list[NexusConstraint] = []

    def get_constraints(self) -> list[NexusConstraint]:
        self.__parent_network.get_load_status()
        return self.__constraints

    def get_constraint(self, name: str) -> Optional[list[NexusConstraint]]:
        # TODO: make this a date based approach as well or return a list?
        # TODO: improve the usability of this?
        self.__parent_network.get_load_status()
        constraints_to_return = filter(lambda x: False if x.name is None else x.name.upper() == name.upper(),
                                       self.__constraints)
        return next(constraints_to_return, None)

    def get_constraint_df(self) -> pd.DataFrame:
        """ Creates a dataframe representing all processed constraint data in a surface file
        Returns:
            DataFrame: of the properties of the constraint through time with each row representing a change in constraint.
        """
        self.__parent_network.get_load_status()
        return obj_to_dataframe(self.__constraints)
