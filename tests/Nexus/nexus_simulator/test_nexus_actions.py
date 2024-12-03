import pytest

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusAction import NexusAction
from ResSimpy.Nexus.DataModels.Network.NexusActions import NexusActions
from ResSimpy.Nexus.DataModels.Network.NexusActivationChange import NexusActivationChange
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusEnums.ActivationChangeEnum import ActivationChangeEnum
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusNetwork import NexusNetwork
from tests.utility_for_tests import get_fake_nexus_simulator


def test_load_basic_network_action(mocker):
    # arrange
    # this tests a basic action table
    start_date = '01/01/2023'

    surface_file_contents = """
ACTIONS
ACTIONTIME  ACTION     CONNECTION
7500        ACTIVATE   WELL1      !this is a comment
8000        DEACTIVATE WELL2
ENDACTIONS
"""

    properties_dict1 = {'action_time': 7500.0, 'change': ActivationChangeEnum.ACTIVATE, 'connection': 'WELL1'}
    properties_dict2 = {'action_time': 8000.0, 'change': ActivationChangeEnum.DEACTIVATE, 'connection': 'WELL2'}
    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())

    expected_action1 = NexusAction(properties_dict1, date_format=DateFormat.MM_DD_YYYY, start_date=start_date)
    expected_action2 = NexusAction(properties_dict2, date_format=DateFormat.MM_DD_YYYY, start_date=start_date)

    # create a nexus network object
    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_model._start_date = start_date
    dummy_model.model_files.surface_files = {1: surface_file}

    nexus_net = NexusNetwork(model=dummy_model)
    expected_result = [expected_action1, expected_action2]

    nexus_actions = NexusActions(parent_network=nexus_net)
    nexus_net.actions = nexus_actions

    # Act
    result = nexus_actions.get_all()

    # Assert
    assert result[0] == expected_result[0]
    assert result[1] == expected_result[1]


def test_load_basic_network_action_blank(mocker):
    # arrange
    # this tests an empty action table
    start_date = '01/01/2023'

    surface_file_contents = """
ACTIONS
ENDACTIONS
"""

    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())

    # create a nexus network object
    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_model._start_date = start_date
    dummy_model.model_files.surface_files = {1: surface_file}

    nexus_net = NexusNetwork(model=dummy_model)

    nexus_actions = NexusActions(parent_network=nexus_net)
    nexus_net.actions = nexus_actions

    # Assert an error
    with pytest.raises(ValueError):
        nexus_actions.get_all()


def test_load_basic_network_action_spaces(mocker):
    # arrange
    # this tests an action table with lots of blank spaces
    start_date = '01/01/2023'

    surface_file_contents = """
ACTIONS
ACTIONTIME  ACTION     CONNECTION
7500        ACTIVATE   WELL1      !this is a comment





8000        DEACTIVATE WELL2
ENDACTIONS
"""

    properties_dict1 = {'action_time': 7500.0, 'change': ActivationChangeEnum.ACTIVATE, 'connection': 'WELL1'}
    properties_dict2 = {'action_time': 8000.0, 'change': ActivationChangeEnum.DEACTIVATE, 'connection': 'WELL2'}

    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())
    expected_action1 = NexusAction(properties_dict1, date_format=DateFormat.MM_DD_YYYY, start_date=start_date)
    expected_action2 = NexusAction(properties_dict2, date_format=DateFormat.MM_DD_YYYY, start_date=start_date)

    # create a nexus network object
    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_model._start_date = start_date
    dummy_model.model_files.surface_files = {1: surface_file}

    nexus_net = NexusNetwork(model=dummy_model)
    expected_result = [expected_action1, expected_action2]

    nexus_actions = NexusActions(parent_network=nexus_net)
    nexus_net.actions = nexus_actions

    # Act
    result = nexus_actions.get_all()

    # Assert
    assert result[0] == expected_result[0]
    assert result[1] == expected_result[1]


def test_load_basic_network_action_comments(mocker):
    # arrange
    # this tests an action table with comment thrown in the middle
    start_date = '01/01/2023'

    surface_file_contents = """
ACTIONS
ACTIONTIME  ACTION     CONNECTION
7500        ACTIVATE   WELL1      !this is a comment
! this is a random comment in the middle
8000        DEACTIVATE WELL2
ENDACTIONS
"""

    properties_dict1 = {'action_time': 7500.0, 'change': ActivationChangeEnum.ACTIVATE, 'connection': 'WELL1'}
    properties_dict2 = {'action_time': 8000.0, 'change': ActivationChangeEnum.DEACTIVATE, 'connection': 'WELL2'}

    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())
    expected_action1 = NexusAction(properties_dict1, date_format=DateFormat.MM_DD_YYYY, start_date=start_date)
    expected_action2 = NexusAction(properties_dict2, date_format=DateFormat.MM_DD_YYYY, start_date=start_date)

    # create a nexus network object
    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_model._start_date = start_date
    dummy_model.model_files.surface_files = {1: surface_file}

    nexus_net = NexusNetwork(model=dummy_model)
    expected_result = [expected_action1, expected_action2]

    nexus_actions = NexusActions(parent_network=nexus_net)
    nexus_net.actions = nexus_actions

    # Act
    result = nexus_actions.get_all()

    # Assert
    assert result[0] == expected_result[0]
    assert result[1] == expected_result[1]


def test_load_basic_network_action_funky(mocker):
    # arrange
    # this tests an action table with comment thrown in the middle
    start_date = '01/01/2023'

    surface_file_contents = """
ACTIONS
!comments
!comments


ACTIONTIME  ACTION     CONNECTION

7500        ACTIVATE   WELL1


8000        DEACTIVATE WELL2

!comment
ENDACTIONS
"""

    properties_dict1 = {'action_time': 7500.0, 'change': ActivationChangeEnum.ACTIVATE, 'connection': 'WELL1'}
    properties_dict2 = {'action_time': 8000.0, 'change': ActivationChangeEnum.DEACTIVATE, 'connection': 'WELL2'}

    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())
    expected_action1 = NexusAction(properties_dict1, date_format=DateFormat.MM_DD_YYYY, start_date=start_date)
    expected_action2 = NexusAction(properties_dict2, date_format=DateFormat.MM_DD_YYYY, start_date=start_date)

    # create a nexus network object
    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_model._start_date = start_date
    dummy_model.model_files.surface_files = {1: surface_file}

    nexus_net = NexusNetwork(model=dummy_model)
    expected_result = [expected_action1, expected_action2]

    nexus_actions = NexusActions(parent_network=nexus_net)
    nexus_net.actions = nexus_actions

    # Act
    result = nexus_actions.get_all()

    # Assert
    assert result[0] == expected_result[0]
    assert result[1] == expected_result[1]


def test_load_basic_network_action_activate_deactivate(mocker):
    # arrange
    # this tests an action table with activate/deactivate cards
    start_date = '01/01/2023'

    surface_file_contents = """
ACTIONS
ACTIONTIME  ACTION     CONNECTION
7500        ACTIVATE   WELL1
8000        DEACTIVATE WELL2
ENDACTIONS

TIME 01/01/2045
WELLS
NAME   STREAM DATUM 
WELL3 PRODUCER 1234 
WELL4 PRODUCER 5678
ENDWELLS

DEACTIVATE
CONNECTION
WELL3
WELL4
ENDDEACTIVATE
"""

    properties_dict1 = {'action_time': 7500.0, 'change': ActivationChangeEnum.ACTIVATE, 'connection': 'WELL1'}
    properties_dict2 = {'action_time': 8000.0, 'change': ActivationChangeEnum.DEACTIVATE, 'connection': 'WELL2'}
    welcon_props_1 = {'name': 'WELL3', 'stream': 'PRODUCER', 'datum_depth': 1234.0, 'date': '01/01/2045',
                      'unit_system': UnitSystem.ENGLISH}
    welcon_props_2 = {'name': 'WELL4', 'stream': 'PRODUCER', 'datum_depth': 5678.0, 'date': '01/01/2045',
                      'unit_system': UnitSystem.ENGLISH}

    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())
    expected_action1 = NexusAction(properties_dict1, date_format=DateFormat.MM_DD_YYYY, start_date=start_date)
    expected_action2 = NexusAction(properties_dict2, date_format=DateFormat.MM_DD_YYYY, start_date=start_date)

    exp_welcon_1 = NexusWellConnection(welcon_props_1, date_format=DateFormat.MM_DD_YYYY, start_date=start_date)
    exp_welcon_2 = NexusWellConnection(welcon_props_2, date_format=DateFormat.MM_DD_YYYY, start_date=start_date)

    # create a nexus network object
    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_model._start_date = start_date
    dummy_model.model_files.surface_files = {1: surface_file}

    nexus_net = NexusNetwork(model=dummy_model)
    expected_result = [expected_action1, expected_action2]
    expected_welcons = [exp_welcon_1, exp_welcon_2]

    expected_activation_change_1 = NexusActivationChange(name='WELL3', change=ActivationChangeEnum.DEACTIVATE,
                                                         date='01/01/2045', date_format=DateFormat.MM_DD_YYYY,
                                                         start_date='01/01/2023')
    expected_activation_change_2 = NexusActivationChange(name='WELL4', change=ActivationChangeEnum.DEACTIVATE,
                                                         date='01/01/2045', date_format=DateFormat.MM_DD_YYYY,
                                                         start_date='01/01/2023')
    expected_activation_changes = [expected_activation_change_1, expected_activation_change_2]

    nexus_actions = NexusActions(parent_network=nexus_net)
    nexus_net.actions = nexus_actions

    # Act
    result = nexus_actions.get_all()
    result_wellcons = dummy_model.network.well_connections.get_all()
    result_activation_changes = dummy_model.network.activation_changes.get_all()

    # Assert
    assert result == expected_result
    assert result_wellcons == expected_welcons
    assert result_activation_changes == expected_activation_changes

    # assert result[0] == expected_result[0]
    # assert result[1] == expected_result[1]
    # assert result_wellcons[0] == expected_welcons[0]
    # assert result_wellcons[1] == expected_welcons[1]

