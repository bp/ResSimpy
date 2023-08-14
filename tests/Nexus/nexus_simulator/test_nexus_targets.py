import pytest
from ResSimpy.Nexus.DataModels.Network import NexusTarget
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusConstraints import NexusConstraints
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusNetwork import NexusNetwork
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator

@pytest.mark.parametrize("file_contents", [
    # basic_test
    ('''TIME 01/01/2019
    TARGET
    NAME    CTRL   CTRLCOND   CTRLCONS   CTRLMETHOD   CALCMETHOD   CALCCOND   CALCCONS   VALUE   ADDVALUE   REGION   PRIORITY   QMIN   QMIN_NOSHUT   QGUIDE   MAXDPDT   RANKDT   CTRLTYPE   CALCTYPE
    target1   control1   ctrlcnd1   ctrlcons1   ctrlmthd1   calcmthd1   calccond1   calccons1   1.0   11.0   region1   1   1.5   1.8   1.9   1.6   0.9   type1   ctype1
    target2   control2   ctrlcnd2   ctrlcons2   ctrlmthd2   calcmthd2   calccond2   calccons2   2.0   21.0   region2   2   2.5   2.8   2.9   2.6   1.9   type2   ctype2
    ENDTARGET'''
    )
    ],ids=['basic_test'])
def test_read_target(mocker, fixture_for_osstat_pathlib, file_contents):
    # Arrange
    fcs_file_contents = '''
        RUN_UNITS ENGLISH
        DATEFORMAT DD/MM/YYYY
        RECURRENT_FILES
        RUNCONTROL /nexus_data/runcontrol.dat
        SURFACE Network 1  /surface_file_01.dat
        '''
    runcontrol_contents = '''START 01/01/2019'''

  

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/path/fcs_file.fcs': fcs_file_contents,
            '/surface_file_01.dat': file_contents,
            '/nexus_data/runcontrol.dat': runcontrol_contents}
            ).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)
    nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)

    # Act
    nexus_sim.network.load()
    result= nexus_sim.network.targets.get_df()
    # target1_props=({'name': 'target1', 'control_quantity': 'control1', 'control_conditions': 'ctrlcnd1', 'control_connections': 'ctrlcons1',
    #   'control_method': 'ctrlmthd1', 'calculation_method': 'calcmthd1', 'calculation_conditions': 'calccond1', 'calculation_connections': 'calccons1',
    #   'value': 1.0, 'add_value': 11.0, 'region': 'region1', 'priority': 1,
    #   'minimum_rate': 1.5, 'minimum_rate_no_shut': 1.8, 'guide_rate': 1.9, 'max_change_pressure': 1.6,
    #   'rank_dt': 0.9, 'control_type': 'type1', 'calculation_type': 'ctype1','unit_system': UnitSystem.ENGLISH})
    
    # target2_props=({'name': 'target2', 'control_quantity': 'control2', 'control_conditions': 'ctrlcnd2', 'control_connections': 'ctrlcons2',
    #   'control_method': 'ctrlmthd2', 'calculation_method': 'calcmthd2', 'calculation_conditions': 'calccond2', 'calculation_connections': 'calccons2',
    #   'value': 2.0, 'add_value': 21.0, 'region': 'region2', 'priority': 2,
    #   'minimum_rate': 2.5, 'minimum_rate_no_shut': 2.8, 'guide_rate': 2.9, 'max_change_pressure': 2.6,
    #   'rank_dt': 1.9, 'control_type': 'type2', 'calculation_type': 'ctype2','unit_system': UnitSystem.ENGLISH})
    # expected_result=[(NexusTarget(x) for x in target1_props),(NexusTarget(x) for x in target2_props)]
    # Assert
    assert result.shape[0] == 2
