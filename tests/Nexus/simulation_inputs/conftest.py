import pytest


def nexus_run_mock(mocker):
    nexus_mock = mocker.Mock()
    nexus_mock.nexsub = mocker.Mock(return_value=456)

    def mock_status_message(job_id, force_refresh):
        return f"Nexsub status called, Job ID is: {job_id}"

    nexus_mock.status = mocker.Mock(side_effect=mock_status_message)
    return nexus_mock


def mock_imports(mocker):
    orig_import = __import__

    nexus_input_files_mock = mocker.MagicMock()
    execution_mock = mocker.MagicMock()
    generic_mock = mocker.MagicMock()

    def import_mock(name: str, *args, **kwargs):
        if name.endswith('nexus_input_files'):
            return nexus_input_files_mock(name, *args, **kwargs)
        if name.endswith('execution'):
            return execution_mock(name, *args, **kwargs)
        if name.endswith('nexus_run'):
            return nexus_run_mock(mocker)
        if name.endswith('envmodules') or name.endswith('env_modules_python'):
            return generic_mock(mocker, name, *args, **kwargs)
        if 'resqml' in name or 'resqpy' in name:
            return generic_mock(mocker, name, *args, **kwargs)
        return orig_import(name, *args, **kwargs)

    mocker.patch('builtins.__import__', side_effect=import_mock)


@pytest.fixture(scope="function", autouse=True)
def simulation(mocker):
    # If we've already loaded in the Simulation Inputs module, remove it, to allow us to mock out the imports
    import sys

    # if "bifrost.simulation.input" in sys.modules.keys():
    #     del sys.modules["bifrost.simulation.input"]

    listdir_mock = mocker.Mock(return_value=[])
    mocker.patch("os.listdir", listdir_mock)

    mock_imports(mocker)

