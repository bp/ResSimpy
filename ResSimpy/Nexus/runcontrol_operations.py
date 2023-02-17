import ResSimpy.Nexus.nexus_file_operations as nfo


def get_times(times_file: list[str]) -> list[str]:
    """Retrieves a list of TIMES from the supplied Runcontrol / Include file

    Args:
        times_file (list[str]): list of strings with each line from the file a new entry in the list

    Returns:
        list[str]: list of all the values following the TIME keyword in supplied file, \
            empty list if no values found
    """
    times = []
    for line in times_file:
        if nfo.check_token('TIME', line):
            value = nfo.get_token_value('TIME', line, times_file)
            if value is not None:
                times.append(value)

    return times


def delete_times(file_content: list[str]) -> list[str]:
    """ Deletes times from file contents
    Args:
        file_content (list[str]):  list of strings with each line from the file a new entry in the list

    Returns:
        list[str]: the modified file without any TIME cards in
    """
    new_file: list[str] = []
    previous_line_is_time = False
    for line in file_content:
        if "TIME " not in line and (previous_line_is_time is False or line != '\n'):
            new_file.append(line)
            previous_line_is_time = False
        elif "TIME " in line:
            previous_line_is_time = True
        else:
            previous_line_is_time = False
    return new_file


def remove_times_from_file(file_content: list[str], output_file_path: str):
    """Removes the times from a file - used for replacing with new times
    Args:
        file_content (list[str]): a list of strings containing each line of the file as a new entry
        output_file_path (str): path to the file to output to
    """
    new_file_content = delete_times(file_content)

    new_file_str = "".join(new_file_content)

    with open(output_file_path, "w") as text_file:
        text_file.write(new_file_str)
