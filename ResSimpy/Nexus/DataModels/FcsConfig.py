from dataclasses import dataclass


@dataclass
class FcsConfig:
    def __init__(self, destination, nexus_data_name="data") -> None:
        self.output_dir = destination
        self.use_reservoir_names = True
        self.abs_paths_to_keep: list[str] = []
        self.use_one_dir = True
        self.input_data_dir = ''
        self.path_components_to_keep = None
        self.locals_to_data = True
        self.output_data_dir = nexus_data_name
        self.dry_run = False
        self.compress = False
        self.output_log_file = False
