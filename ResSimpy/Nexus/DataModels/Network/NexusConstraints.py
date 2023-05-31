from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

import pandas as pd

from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe
import ResSimpy.Nexus.nexus_file_operations as nfo

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass
class NexusConstraints:
    __constraints: dict[str, list[NexusConstraint]] = field(default_factory=lambda: {})

    def __init__(self, parent_network: NexusNetwork) -> None:
        self.__parent_network: NexusNetwork = parent_network
        self.__constraints: dict[str, list[NexusConstraint]] = {}

    def get_constraints(self, object_name: Optional[str] = None, date: Optional[str] = None) -> \
            dict[str, list[NexusConstraint]]:
        """Get the constraints of the existing model with optional parameters to filter for name and date
        Args:
            object_name (Optional[str]): name of the connection, node or wellname to return. Defaults to None.
            date (Optional[str]): date in model format to filter the dates to in the constraints
        Returns: dict[str, list[NexusConstraint]] dictionary of all constraints defined within a model, keyed by the \
            name of the well/node.
        """
        self.__parent_network.get_load_status()

        if object_name is None:
            constraints_to_return = self.__constraints
        else:
            constraints_to_return = {k: v for k, v in self.__constraints.items() if k == object_name}

        if date is None:
            return constraints_to_return

        date_filtered_constraints = {}
        for constraint_name, constraint_list in constraints_to_return.items():
            new_constraint_list = [x for x in constraint_list if x.date == date]
            if len(new_constraint_list) > 0:
                date_filtered_constraints[constraint_name] = new_constraint_list
        return date_filtered_constraints

    def get_constraint_df(self) -> pd.DataFrame:
        """Creates a dataframe representing all processed constraint data in a surface file
        Returns:
            DataFrame: of the properties of the constraint through time with each row representing \
                a change in constraint.
        """
        self.__parent_network.get_load_status()
        list_constraints = []
        for well_constraints in self.__constraints.values():
            list_constraints.extend(well_constraints)
        obj_to_dataframe(list_constraints)

        return obj_to_dataframe(list_constraints)

    def get_constraint_overview(self) -> str:
        raise NotImplementedError('To be implemented')

    def load_constraints(self, surface_file: NexusFile, start_date: str, default_units: UnitSystem) -> None:
        # CONSTRAINT keyword represents a table with a header and columns.
        # CONSTRAINTS keyword represents a list of semi structured constraints with a well_name and then constraints
        new_constraints = nfo.collect_all_tables_to_objects(surface_file,
                                                            {
                                                                'CONSTRAINTS': NexusConstraint,
                                                                'CONSTRAINT': NexusConstraint,
                                                                'QMULT': NexusConstraint
                                                                },
                                                            start_date=start_date,
                                                            default_units=default_units)
        cons_list = new_constraints.get('CONSTRAINTS')
        if isinstance(cons_list, list):
            raise ValueError(
                'Incompatible data format for additional constraints. Expected type "dict" instead got "list"')
        self.add_constraints(cons_list)

    def add_constraints(self, additional_constraints: Optional[dict[str, list[NexusConstraint]]]) -> None:
        """Adds additional constraints to memory within the NexusConstraints object.
            If user adds constraints list this will not be reflected in the Nexus deck at this time.

        Args:
        ----
            additional_constraints (list[NexusConstraint]): additional constraints to add as a list
        """
        if additional_constraints is None:
            return
        self.__constraints.update(additional_constraints)
        # TODO sort by date:
        # # use the compare dates function stored in the runcontrol to sort the constraints
        # sorted(self.__constraints, key=lambda x:
        # self.__parent_network.model.Runcontrol.convert_date_to_number(x.date))
