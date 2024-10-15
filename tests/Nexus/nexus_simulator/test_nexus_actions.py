from ResSimpy.Nexus.DataModels.Network.NexusAction import NexusAction
from ResSimpy.Nexus.DataModels.Network.NexusActions import NexusActions
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
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

    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())
    expected_action1 = NexusAction(action_time='7500', action='ACTIVATE', connection='WELL1')
    expected_action2 = NexusAction(action_time='8000', action='DEACTIVATE', connection='WELL2')

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

    # Act
    result = nexus_actions.get_all()

    # Assert that the result is an empty list!
    assert not result


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

    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())
    expected_action1 = NexusAction(action_time='7500', action='ACTIVATE', connection='WELL1')
    expected_action2 = NexusAction(action_time='8000', action='DEACTIVATE', connection='WELL2')

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

    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())
    expected_action1 = NexusAction(action_time='7500', action='ACTIVATE', connection='WELL1')
    expected_action2 = NexusAction(action_time='8000', action='DEACTIVATE', connection='WELL2')

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

    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())
    expected_action1 = NexusAction(action_time='7500', action='ACTIVATE', connection='WELL1')
    expected_action2 = NexusAction(action_time='8000', action='DEACTIVATE', connection='WELL2')

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
