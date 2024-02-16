from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.DataModels.Network.NexusProc import NexusProc
from ResSimpy.Nexus.DataModels.Network.NexusProcs import NexusProcs
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusNetwork import NexusNetwork
from tests.utility_for_tests import get_fake_nexus_simulator


# text in between PROCS and ENDPROCS
def test_load_nexus_procedures_basic(mocker):
    # Arrange
    # mock out a surface file:
    # this is required
    start_date = '01/01/2023'

    surface_file_contents = """PROCS
THIS IS RANDOM TEXT
ENDPROCS
    """

    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())

    # create object
    # date must be the same as the start_date
    expected_proc = NexusProc(date='01/01/2023', contents=["THIS IS RANDOM TEXT"])

    # create a nexus network object
    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_model._start_date = start_date
    dummy_model.model_files.surface_files = {1: surface_file}

    nexus_net = NexusNetwork(model=dummy_model)

    # list of expected procedures
    expected_result = [expected_proc]

    nexus_procs = NexusProcs(parent_network=nexus_net)
    nexus_net.procs = nexus_procs

    # Act
    # nexus_procs.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_procs.get_all()

    # Assert
    assert result[0] == expected_result[0]
    assert result == expected_result


# single date

def test_load_nexus_procedures_date(mocker):
    # Arrange
    # mock out a surface file:
    # this is required
    start_date = '01/01/2023'

    surface_file_contents = """TIME 01/01/2024
PROCS
THIS IS RANDOM TEXT
ENDPROCS
    """

    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())

    # create object
    # date must be the same as the start_date
    expected_proc = NexusProc(date='01/01/2024', contents=["THIS IS RANDOM TEXT"])

    # create a nexus network object
    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_model._start_date = start_date
    dummy_model.model_files.surface_files = {1: surface_file}

    nexus_net = NexusNetwork(model=dummy_model)

    # list of expected procedures
    expected_result = [expected_proc]

    nexus_procs = NexusProcs(parent_network=nexus_net)
    nexus_net.procs = nexus_procs

    # Act
    # nexus_procs.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_procs.get_all()

    # Assert
    assert result[0] == expected_result[0]
    assert result == expected_result


# populate name and priority

def test_load_nexus_procedures_name_priority(mocker):
    # Arrange
    # mock out a surface file:
    # this is required
    start_date = '01/01/2023'

    surface_file_contents = """TIME 01/01/2024
PROCS NAME STATIC_VARS PRIORITY 1
THIS IS RANDOM TEXT
ENDPROCS
    """

    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())

    # create object
    # date must be the same as the start_date
    expected_proc = NexusProc(date='01/01/2024', name='STATIC_VARS', priority=1, contents=["THIS IS RANDOM TEXT"])

    # create a nexus network object
    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_model._start_date = start_date
    dummy_model.model_files.surface_files = {1: surface_file}

    nexus_net = NexusNetwork(model=dummy_model)

    # list of expected procedures
    expected_result = [expected_proc]

    nexus_procs = NexusProcs(parent_network=nexus_net)
    nexus_net.procs = nexus_procs

    # Act
    # nexus_procs.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_procs.get_all()

    # Assert
    assert result[0] == expected_result[0]
    assert result == expected_result


# multiple procs in one time

def test_load_nexus_procedures_multiple_procs_one_time(mocker):
    # Arrange
    # mock out a surface file:
    # this is required
    start_date = '01/01/2023'

    surface_file_contents = """TIME 01/01/2024
PROCS NAME STATIC_VARS PRIORITY 1
THIS IS RANDOM TEXT
ENDPROCS
PROCS NAME DYNAMIC_VARS PRIORITY 2
THIS IS MORE RANDOM TEXT
ENDPROCS
    """

    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())

    # create object
    # date must be the same as the start_date
    expected_proc1 = NexusProc(date='01/01/2024', name='STATIC_VARS', priority=1, contents=["THIS IS RANDOM TEXT"])
    expected_proc2 = NexusProc(date='01/01/2024', name='DYNAMIC_VARS', priority=2,
                               contents=["THIS IS MORE RANDOM TEXT"])

    # create a nexus network object
    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_model._start_date = start_date
    dummy_model.model_files.surface_files = {1: surface_file}

    nexus_net = NexusNetwork(model=dummy_model)

    # list of expected procedures
    expected_result = [expected_proc1, expected_proc2]

    nexus_procs = NexusProcs(parent_network=nexus_net)
    nexus_net.procs = nexus_procs

    # Act
    # nexus_procs.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_procs.get_all()

    # Assert
    assert result[0] == expected_result[0]
    assert result[1] == expected_result[1]
    assert result == expected_result


# same proc across multiple times

def test_load_nexus_procedures_same_proc_multiple_time(mocker):
    # Arrange
    # mock out a surface file:
    # this is required
    start_date = '01/01/2023'

    surface_file_contents = """TIME 01/01/2024
PROCS NAME STATIC_VARS PRIORITY 1
THIS IS RANDOM TEXT
ENDPROCS
TIME 01/01/2025
PROCS NAME STATIC_VARS PRIORITY 1
THIS IS RANDOM TEXT
ENDPROCS
    """

    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())

    # create object
    # date must be the same as the start_date
    expected_proc1 = NexusProc(date='01/01/2024', name='STATIC_VARS', priority=1, contents=["THIS IS RANDOM TEXT"])
    expected_proc2 = NexusProc(date='01/01/2025', name='STATIC_VARS', priority=1, contents=["THIS IS RANDOM TEXT"])

    # create a nexus network object
    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_model._start_date = start_date
    dummy_model.model_files.surface_files = {1: surface_file}

    nexus_net = NexusNetwork(model=dummy_model)

    # list of expected procedures
    expected_result = [expected_proc1, expected_proc2]

    nexus_procs = NexusProcs(parent_network=nexus_net)
    nexus_net.procs = nexus_procs

    # Act
    # nexus_procs.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_procs.get_all()

    # Assert
    assert result[0] == expected_result[0]
    assert result[1] == expected_result[1]
    assert result == expected_result


# multiple procs across multiple times

def test_load_nexus_procedures_multiple_procs_multiple_times(mocker):
    # Arrange
    # mock out a surface file:
    # this is required
    start_date = '01/01/2023'

    surface_file_contents = """TIME 01/01/2024
PROCS NAME STATIC_VARS PRIORITY 1
THIS IS RANDOM TEXT
ENDPROCS
TIME 01/01/2025
PROCS NAME STATIC_VARS PRIORITY 1
THIS IS RANDOM TEXT
ENDPROCS
PROCS NAME DYNAMIC_VARS PRIORITY 2
THIS IS DIFFERENT RANDOM TEXT
ENDPROCS
    """

    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())

    # create object
    # date must be the same as the start_date
    expected_proc1 = NexusProc(date='01/01/2024', name='STATIC_VARS', priority=1, contents=["THIS IS RANDOM TEXT"])
    expected_proc2 = NexusProc(date='01/01/2025', name='STATIC_VARS', priority=1, contents=["THIS IS RANDOM TEXT"])
    expected_proc3 = NexusProc(date='01/01/2025', name='DYNAMIC_VARS', priority=2,
                               contents=["THIS IS DIFFERENT RANDOM TEXT"])

    # create a nexus network object
    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_model._start_date = start_date
    dummy_model.model_files.surface_files = {1: surface_file}

    nexus_net = NexusNetwork(model=dummy_model)

    # list of expected procedures
    expected_result = [expected_proc1, expected_proc2, expected_proc3]

    nexus_procs = NexusProcs(parent_network=nexus_net)
    nexus_net.procs = nexus_procs

    # Act
    # nexus_procs.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_procs.get_all()

    # Assert
    assert result[0] == expected_result[0]
    assert result[1] == expected_result[1]
    assert result[2] == expected_result[2]
    assert result == expected_result


def test_load_nexus_procedures_class_props(mocker):
    # Arrange
    # mock out a surface file:
    # this is required
    start_date = '01/01/2023'

    surface_file_contents = """PROCS NAME STATIC_VARS PRIORITY 1
THIS IS RANDOM TEXT
THIS IS MORE RANDOM TEXT
ENDPROCS
    """

    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())

    # create a nexus network object
    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_model._start_date = start_date
    dummy_model.model_files.surface_files = {1: surface_file}

    nexus_net = NexusNetwork(model=dummy_model)

    nexus_procs = NexusProcs(parent_network=nexus_net)
    nexus_net.procs = nexus_procs

    # Act
    # nexus_procs.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_procs.get_all()

    # Assert
    assert result[0].date == '01/01/2023'
    assert result[0].contents == ['THIS IS RANDOM TEXT', 'THIS IS MORE RANDOM TEXT']
    assert result[0].priority == 1
    assert result[0].name == 'STATIC_VARS'
    # assert result == expected_result


def test_load_nexus_procedures_proc_func_counts_basic(mocker):
    # Arrange
    # mock out a surface file:
    # this is required
    start_date = '01/01/2023'

    surface_file_contents = """PROCS
IF(MAX(X) > MIN(X)) THEN
PRINTOUT(X)
ENDIF
ENDPROCS
    """

    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())

    # create a nexus network object
    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_model._start_date = start_date
    dummy_model.model_files.surface_files = {1: surface_file}

    nexus_net = NexusNetwork(model=dummy_model)

    nexus_procs = NexusProcs(parent_network=nexus_net)
    nexus_net.procs = nexus_procs

    # Act
    # nexus_procs.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_procs.get_all()

    # Assert
    assert result[0].date == '01/01/2023'
    assert result[0].contents == ['IF(MAX(X) > MIN(X)) THEN', 'PRINTOUT(X)', 'ENDIF']
    assert result[0].contents_breakdown['MAX'] == 1
    assert result[0].contents_breakdown['MIN'] == 1
    assert result[0].contents_breakdown['PRINTOUT'] == 1
    #


def test_load_nexus_procedures_proc_func_multiple_counts(mocker):
    # Arrange
    # mock out a surface file:
    # this is required
    start_date = '01/01/2023'

    surface_file_contents = """PROCS
IF(ABS(-MAX(X)) > MIN(X)) THEN
PRINTOUT(2*ABS(X))
PRINTOUT(5*ABS(X))
ENDIF
ENDPROCS
    """

    surface_file = NexusFile(location='surface.dat', file_content_as_list=surface_file_contents.splitlines())

    # create a nexus network object
    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_model._start_date = start_date
    dummy_model.model_files.surface_files = {1: surface_file}

    nexus_net = NexusNetwork(model=dummy_model)

    nexus_procs = NexusProcs(parent_network=nexus_net)
    nexus_net.procs = nexus_procs

    # Act
    # nexus_procs.load(surface_file, start_date, default_units=UnitSystem.ENGLISH)
    result = nexus_procs.get_all()

    # Assert
    assert result[0].date == '01/01/2023'
    assert result[0].contents == ['IF(ABS(-MAX(X)) > MIN(X)) THEN', 'PRINTOUT(2*ABS(X))', 'PRINTOUT(5*ABS(X))', 'ENDIF']
    assert result[0].contents_breakdown['MAX'] == 1
    assert result[0].contents_breakdown['MIN'] == 1
    assert result[0].contents_breakdown['PRINTOUT'] == 2
    assert result[0].contents_breakdown['ABS'] == 3
