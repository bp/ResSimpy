from dataclasses import dataclass

from ResSimpy import NexusSimulator
from ResSimpy.DataModelBaseClasses.DataObjectMixin import DataObjectMixin
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Nexus.DataModels.Network.NexusTarget import NexusTarget
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.DataModels.NexusWellList import NexusWellList
from ResSimpy.Time.ISODateTime import ISODateTime


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
        def store_dates_for_objects(all_network_objects: list[DataObjectMixin], date_storage: list[ISODateTime],
                                    data_object: DataObjectMixin) -> None:
            """Stores the dates for all objects in the model."""
            all_network_objects.append(data_object)
            object_date = data_object.iso_date
            if object_date not in date_storage:
                date_storage.append(object_date)

        if self.model.network is None:
            return full_schedule
        all_event_dates: list[ISODateTime] = []
        all_constraints: list[NexusConstraint] = []
        all_well_connections: list[NexusWellConnection] = []
        all_targets: list[NexusTarget] = []
        all_welllists: list[NexusWellList] = []
        all_nodes: list[NexusNode] = []
        all_connections: list[NexusNodeConnection] = []
        # get dates for all the items
        if self.model.network.welllists is not None:
            for welllist in self.model.network.welllists.welllists:
                store_dates_for_objects(all_welllists, all_event_dates, welllist)

        if self.model.network.constraints is not None:
            for constraint in self.model.network.constraints.constraints:
                store_dates_for_objects(all_constraints, all_event_dates, constraint)

        if self.model.network.well_connections is not None:
            for well_connection in self.model.network.well_connections.get_all():
                store_dates_for_objects(all_well_connections, all_event_dates, well_connection)

        if self.model.network.targets is not None:
            for target in self.model.network.targets.get_all():
                store_dates_for_objects(all_targets, all_event_dates, target)

        if self.model.network.connections is not None:
            for connection in self.model.network.connections.get_all():
                store_dates_for_objects(all_connections, all_event_dates, connection)

        if self.model.network.nodes is not None:
            for node in self.model.network.nodes.get_all():
                store_dates_for_objects(all_nodes, all_event_dates, node)

        # Sort the dates
        all_event_dates.sort()

        # Write out all events for each date
        for date in all_event_dates:
            if date != self.model.start_date:
                full_schedule += f"TIME {date.strftime_dateformat(self.model.date_format)}\n"

            well_connections_for_date = [x for x in all_well_connections if x.iso_date == date]

            if any(well_connections_for_date) and self.model.network.well_connections is not None:
                full_schedule += self.model.network.well_connections.to_string_for_date(date=date)
                full_schedule += '\n'
