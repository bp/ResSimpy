from dataclasses import dataclass
from typing import Sequence, TypeVar

from ResSimpy import NexusSimulator
from ResSimpy.DataModelBaseClasses.DataObjectMixin import DataObjectMixin
from ResSimpy.Time.ISODateTime import ISODateTime

T = TypeVar('T', bound=DataObjectMixin)


@dataclass(kw_only=True)
class NexusModelFileGenerator:
    """A class to generate the contents of a NexusSimulator object as a set of model files."""
    __model: NexusSimulator
    __model_name: str

    def __init__(self, model: NexusSimulator, model_name: str) -> None:
        """Initializes the NexusModelFileGenerator."""
        self.__model = model
        self.__model_name = model_name

    @property
    def model(self) -> NexusSimulator:
        """The NexusSimulator model associated with this generator."""
        return self.__model

    def generate_base_model_file_contents(self) -> str:
        """Generates the base contents of the Nexus model file."""
        fcs_file_contents = self.model.model_files.to_string(dateformat=self.model.date_format,
                                                             run_units=self.model.run_units)
        return fcs_file_contents

    def output_surface_section(self) -> str:
        """Outputs the surface section of the Nexus model file."""
        full_schedule = ''

        def store_dates_for_objects(all_network_objects: Sequence[T], date_storage: list[ISODateTime],
                                    data_object: T) -> list[T]:
            """Stores the dates for all objects in the model."""
            if isinstance(all_network_objects, list):
                all_network_objects_as_list = all_network_objects
            else:
                all_network_objects_as_list = list(all_network_objects)
            all_network_objects_as_list.append(data_object)
            object_date = data_object.iso_date
            if object_date not in date_storage:
                date_storage.append(object_date)
            return all_network_objects_as_list

        if self.model.network is None:
            return full_schedule
        all_well_connections = self.model.network.well_connections.get_all()
        all_targets = self.model.network.targets.get_all()
        all_welllists = self.model.network.welllists.get_all()
        all_nodes = self.model.network.nodes.get_all()
        all_connections = self.model.network.connections.get_all()

        network_objects = [all_well_connections, all_targets, all_welllists, all_nodes, all_connections]

        all_constraints = self.model.network.constraints.get_all()

        all_event_dates: set[ISODateTime] = set()

        all_event_dates.add(self.model.start_iso_date)
        for name, constraints in all_constraints.items():
            all_event_dates.update({x.iso_date for x in constraints})

        # get dates for all the items
        for net_obj in network_objects:
            all_event_dates.update({x.iso_date for x in net_obj})

        # Sort the dates
        ordered_all_event_dates = sorted(all_event_dates)

        # Write out all events for each date
        for date in ordered_all_event_dates:
            if date != self.model.start_iso_date:
                full_schedule += f"TIME {date.strftime_dateformat(self.model.date_format)}\n"

            well_connections_for_date = [x for x in all_well_connections if x.iso_date == date]

            if any(well_connections_for_date) and self.model.network.well_connections is not None:
                full_schedule += self.model.network.well_connections.to_string_for_date(date=date)
                full_schedule += '\n'

            welllists_for_date = [x for x in all_welllists if x.iso_date == date]
            if any(welllists_for_date) and self.model.network.welllists is not None:
                full_schedule += self.model.network.welllists.to_string_for_date(date=date)
                full_schedule += '\n'
            nodes_for_date = [x for x in all_nodes if x.iso_date == date]
            if any(nodes_for_date) and self.model.network.nodes is not None:
                full_schedule += self.model.network.nodes.to_string_for_date(date=date)
                full_schedule += '\n'
            connections_for_date = [x for x in all_connections if x.iso_date == date]
            if any(connections_for_date) and self.model.network.connections is not None:
                full_schedule += self.model.network.connections.to_string_for_date(date=date)
                full_schedule += '\n'

            constraints_for_date = {k: [x for x in v if x.iso_date == date] for k,v in all_constraints.items()}
            if any(constraints_for_date) and self.model.network.constraints is not None:
                full_schedule += self.model.network.constraints.to_string_for_date(date=date)
                full_schedule += '\n'

            targets_for_date = [x for x in all_targets if x.iso_date == date]
            if any(targets_for_date) and self.model.network.targets is not None:
                full_schedule += self.model.network.targets.to_string_for_date(date=date)
                full_schedule += '\n'

        return full_schedule
