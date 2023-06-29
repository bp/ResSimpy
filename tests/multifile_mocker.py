from pytest_mock import MockerFixture


def mock_multiple_files(mocker: MockerFixture, passed_filename: str, potential_file_dict: dict[str, str]):
    """Mock method that returns different test file contents that are stored in the potential file dict.
    Called via a mocker wrapper within a test for example:
        from multifile_mocker import mock_multiple_files
        def mock_open_wrapper(filename, mode):
            mock_open = mock_multiple_files(mocker, filename, potential_file_dict={'key':value, }).return_value
            return mock_open
        mocker.patch("builtins.open", mock_open_wrapper)

    Args:
        mocker (MockerFixture): Mocking fixture, left as a mocker input in a function
        passed_filename (str): file name in the test function when patched in
        potential_file_dict (dict[str, str]): dictionary taking the form: 'filename': filecontents

    Raises:
        FileNotFoundError: if the filename is not found within the dictionary passed to the mocker

    Returns:
        Mock: returns a mocker that gives the file contents corresponding to the key
    """
    try:
        file_contents = potential_file_dict[passed_filename]
    except KeyError:
        raise FileNotFoundError(f'{passed_filename=} did not match any of the provided files within \
                                {potential_file_dict=}')
    open_mock = mocker.mock_open(read_data=file_contents)
    return open_mock
