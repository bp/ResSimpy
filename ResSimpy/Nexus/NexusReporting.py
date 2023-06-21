import ResSimpy.Nexus.nexus_file_operations as nfo


class Reporting:
    def __init__(self, model) -> None:
        self.__model = model

    def add_map_properties_to_start_of_grid_file(self):
        """Adds 'map' statements to the start of the grid file to ensure standalone outputs all the required \
        properties. Writes out to the same structured grid file path provided.

        Raises:
            ValueError: if no structured grid file path is specified in the class instance
        """
        structured_grid_path = self.__model.structured_grid_path
        if self.__model.structured_grid_path is None:
            raise ValueError("No file path given or found for structured grid file path. \
                Please update structured grid file path")
        file = nfo.load_file_as_list(structured_grid_path)

        if not nfo.value_in_file('MAPBINARY', file):
            new_file = ['MAPBINARY\n']
        else:
            new_file = []

        if not nfo.value_in_file('MAPVDB', file):
            new_file.extend(['MAPVDB\n'])

        if not nfo.value_in_file('MAPOUT', file):
            new_file.extend(['MAPOUT ALL\n'])
        else:
            line_counter = 0
            for line in file:
                if nfo.check_token('MAPOUT', line):
                    file[line_counter] = 'MAPOUT ALL\n'
                    break
                line_counter += 1

        new_file.extend(file)

        # Save the new file contents
        new_file_str = "".join(new_file)
        with open(structured_grid_path, "w") as text_file:
            text_file.write(new_file_str)
