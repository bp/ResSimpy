from __future__ import annotations
from dataclasses import dataclass
from typing import TypeVar, TYPE_CHECKING

from ResSimpy.DataModelBaseClasses.DataObjectMixin import DataObjectMixin
from ResSimpy.Enums.FluidTypeEnums import PvtType
from ResSimpy.Time.ISODateTime import ISODateTime
if TYPE_CHECKING:
    from ResSimpy import NexusSimulator
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
                                                             run_units=self.model.run_units,
                                                             default_units=self.model.default_units)
        return fcs_file_contents

    def output_surface_section(self) -> str:
        """Outputs the surface section of the Nexus model file."""
        full_schedule = ''

        # add the pvt type and EOS properties:

        if self.model.pvt_type == PvtType.EOS and self.model.eos_details is not None:
            full_schedule += self.model.eos_details
        else:
            full_schedule += self.model.pvt_type.name
        full_schedule += '\n\n'

        if self.model.network is None:
            return full_schedule
        all_well_connections = self.model.network.well_connections.get_all()
        all_targets = self.model.network.targets.get_all()
        all_welllists = self.model.network.welllists.get_all()
        all_nodes = self.model.network.nodes.get_all()
        all_connections = self.model.network.connections.get_all()
        all_activations = self.model.network.activation_changes.get_all()

        network_objects = [all_well_connections, all_targets, all_welllists, all_nodes, all_connections,
                           all_activations]

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

            constraints_for_date = {k: [x for x in v if x.iso_date == date] for k, v in all_constraints.items()}
            if any(x for x in constraints_for_date.values()) and self.model.network.constraints is not None:
                full_schedule += self.model.network.constraints.to_string_for_date(date=date)
                full_schedule += '\n'

            targets_for_date = [x for x in all_targets if x.iso_date == date]
            if any(targets_for_date) and self.model.network.targets is not None:
                full_schedule += self.model.network.targets.to_string_for_date(date=date)
                full_schedule += '\n'

            activations_for_date = [x for x in all_activations if x.iso_date == date]
            if any(activations_for_date) and self.model.network.activation_changes is not None:
                full_schedule += self.model.network.activation_changes.to_string_for_date(date=date)
                full_schedule += '\n'

        return full_schedule

    def output_wells_section(self) -> str:
        """Outputs the wells section of the Nexus model file."""
        if not self.model.wells._wells_loaded:
            return ''

        full_wells = ''

        all_well_completions = []
        all_well_mods = []
        for well in self.model.wells.get_all():
            all_well_completions.extend(well.completions)
            all_well_mods.extend(well.wellmods)

        well_mod_dates = {x.iso_date for x in all_well_mods}

        all_event_dates: set[ISODateTime] = self.model.wells.get_wells_iso_dates()
        all_event_dates.add(self.model.start_iso_date)
        all_event_dates.update(well_mod_dates)

        # Sort the dates
        ordered_all_event_dates = sorted(all_event_dates)

        # Write out all events for each date
        for date in ordered_all_event_dates:
            if date != self.model.start_iso_date:
                full_wells += f"TIME {date.strftime_dateformat(self.model.date_format)}\n"
            for well in self.model.wells.get_all():
                full_wells += well.to_string_for_date(date=date)

        return full_wells

    def output_options_section(self) -> str:
        """Outputs the options section of the Nexus model file."""
        options_file_content = ''
        if self.model.options is not None:
            options_file_content += self.model.options.to_string()
        # add the gridtoprocs to options:
        if self.model.sim_controls.grid_to_proc is not None:
            options_file_content += '\n'
            options_file_content += self.model.sim_controls.grid_to_proc.to_string()
        return options_file_content

    def output_runcontrol_section(self) -> str:
        """Outputs the run control section of the Nexus model file."""
        run_control_content = f'START {self.model.start_iso_date.strftime_dateformat(self.model.date_format)}\n\n'

        # collect all the dates from the solver controls
        all_dates: set[ISODateTime] = {self.model.start_iso_date}
        for solver_param in self.model.sim_controls.solver_parameters.get_all():
            all_dates.add(solver_param.iso_date)
        # collect all the dates from the reporting controls
        all_dates.update(self.model.reporting.get_all_reporting_dates())

        # add all the TIME cards:
        all_dates.update(set(self.model.sim_controls.times_iso_date))

        # Sort the dates
        ordered_all_dates = sorted(all_dates)

        for date in ordered_all_dates:
            if date != self.model.start_iso_date:
                run_control_content += f'\nTIME {date.strftime_dateformat(self.model.date_format)}\n'

            run_control_content += self.model.sim_controls.solver_parameters.to_string_for_date(date=date)
            run_control_content += self.model.reporting.to_string_for_date(date=date)

        return run_control_content
