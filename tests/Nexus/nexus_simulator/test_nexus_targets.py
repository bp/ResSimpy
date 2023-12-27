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
    target1   control1   ctrlcnd1   ctrlcons1   ctrlmthd1   calcmthd1   calccond1   calccons1   1.0   11.0   region1   1   1.5   1.8   Formula  1.6   0.9   type1   ctype1
    target2   control2   ctrlcnd2   ctrlcons2   ctrlmthd2   calcmthd2   calccond2   calccons2   2.0   21.0   region2   2   2.5   2.8   NA   2.6   1.9   type2   ctype2
    ENDTARGET'''),
    ('''TIME 01/01/2019 ! This target below in guide rate table should be skipped.
    GUIDERATE
    TARGET       DTMIN   PHASE   A   B   C   D   E       F   INCREASE    DAMP
    targetformula    10      OIL     1   0   0.22   0.23   1   0.6 YES         1
    ENDGUIDERATE
      PROCS NAME FULL_GAS_BALANCE PRIORITY 20 
    PROD         = SUM, somestring, ALL1D), ALL1D)
    ENDPROCS
     TARGET
    NAME    CTRL   CTRLCOND   CTRLCONS   CTRLMETHOD   CALCMETHOD   CALCCOND   CALCCONS   VALUE   ADDVALUE   REGION   PRIORITY   QMIN   QMIN_NOSHUT   QGUIDE   MAXDPDT   RANKDT   CTRLTYPE   CALCTYPE
    target1   control1   ctrlcnd1   ctrlcons1   ctrlmthd1   calcmthd1   calccond1   calccons1   1.0   11.0   region1   1   1.5   1.8   Formula  1.6   0.9   type1   ctype1
    target2   control2   ctrlcnd2   ctrlcons2   ctrlmthd2   calcmthd2   calccond2   calccons2   2.0   21.0   region2   2   2.5   2.8   NA   2.6   1.9   type2   ctype2
    ENDTARGET'''
    )
    ],ids=['basic_test', 'guiderate with target column header'])
def test_read_target(mocker, file_contents):
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
    
     
    target1_props={'name': 'target1', 'control_quantity': 'control1', 'control_conditions': 'ctrlcnd1', 'control_connections': 'ctrlcons1',
      'control_method': 'ctrlmthd1', 'calculation_method': 'calcmthd1', 'calculation_conditions': 'calccond1', 'calculation_connections': 'calccons1',
      'value': 1.0, 'add_value': 11.0, 'region': 'region1', 'priority': 1,
      'minimum_rate': 1.5, 'minimum_rate_no_shut': 1.8, 'guide_rate': 'Formula', 'max_change_pressure': 1.6,
      'rank_dt': 0.9, 'control_type': 'type1', 'calculation_type': 'ctype1','unit_system': UnitSystem.ENGLISH}
    
      
    target3_props={'date':'01/01/2019','name': 'target3', 'control_quantity': 'control3', 'control_conditions': 'ctrlcnd3', 'control_connections': 'ctrlcons3',
      'control_method': 'ctrlmthd3', 'calculation_method': 'calcmthd3', 'calculation_conditions': 'calccond3', 'calculation_connections': 'calccons3',
      'value': 3.0, 'add_value': 31.0, 'region': 'region3', 'priority': 3,
      'minimum_rate': 3.5, 'minimum_rate_no_shut': 3.8, 'guide_rate': 'Formula', 'max_change_pressure': 3.6,
      'rank_dt': 4.9, 'control_type': 'type3', 'calculation_type': 'ctype3','unit_system': UnitSystem.ENGLISH}

    # Act    
    nexus_sim.network.load()
    
    record_count= nexus_sim.network.targets.get_df()
    target_record=nexus_sim.network.targets.get_by_name('target1')
    
    target_dict=target_record.to_dict()
    rec_to_remove=nexus_sim.network.targets.get_by_name('target2').to_dict()
    nexus_sim.network.targets.remove({'name': rec_to_remove['name']})
       
    nexus_sim.network.targets.add(target3_props)
    targets_list_after_add=nexus_sim.network.targets.get_all()
    
    # Assert
    for k in target1_props:
        assert target1_props[k] == target_dict[k]  
    assert record_count.shape[0] == 2
    assert nexus_sim.network.targets.get_by_name('target2') == None
    assert len(targets_list_after_add) == 2
