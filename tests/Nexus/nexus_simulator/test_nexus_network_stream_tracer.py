"""Tests for NexusStreamTracer, NexusStreamTracers, and the well-type classification
that flows from STREAM_TRACER blocks parsed in NexusNetwork."""

from unittest.mock import MagicMock, Mock

import pytest
from pytest_mock import MockerFixture

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Enums.WellTypeEnum import WellType
from ResSimpy.Nexus.DataModels.Network.NexusStreamTracer import NexusStreamTracer
from ResSimpy.Nexus.DataModels.Network.NexusStreamTracers import NexusStreamTracers
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator


# NexusStreamTracer unit tests

class TestNexusStreamTracer:

    def test_init_from_kwargs(self):
        """NexusStreamTracer can be initialised with explicit keyword arguments."""
        st = NexusStreamTracer(
            name='SEAWTR',
            component='WATER',
            tracer='SALT',
            concentration=1.0,
            date='01/01/2020',
            date_format=DateFormat.MM_DD_YYYY,
            unit_system=UnitSystem.ENGLISH,
        )
        assert st.name == 'SEAWTR'
        assert st.component == 'WATER'
        assert st.tracer == 'SALT'
        assert st.concentration == 1.0

    def test_init_from_properties_dict(self):
        """NexusStreamTracer can be initialised via properties_dict (table-parser path)."""
        props = {
            'date': '01/01/2020',
            'name': 'TRTWTR',
            'component': 'WATER',
            'tracer': 'SALT',
            'concentration': 1.0,
        }
        st = NexusStreamTracer(
            properties_dict=props,
            date_format=DateFormat.MM_DD_YYYY,
            unit_system=UnitSystem.ENGLISH,
        )
        assert st.name == 'TRTWTR'
        assert st.component == 'WATER'
        assert st.tracer == 'SALT'
        assert st.concentration == 1.0

    def test_optional_fields_default_none(self):
        """Tracer and concentration are optional and default to None."""
        st = NexusStreamTracer(name='MYSTREAM', component='GAS', date='01/01/2020',
                               date_format=DateFormat.MM_DD_YYYY, unit_system=UnitSystem.ENGLISH)
        assert st.tracer is None
        assert st.concentration is None

    def test_get_keyword_mapping(self):
        """get_keyword_mapping returns the expected column→attribute map."""
        mapping = NexusStreamTracer.get_keyword_mapping()
        assert mapping['NAME'] == ('name', str)
        assert mapping['COMPONENT'] == ('component', str)
        assert mapping['TRACER'] == ('tracer', str)
        assert mapping['CONCENTRATION'] == ('concentration', float)


# NexusStreamTracers unit tests

class TestNexusStreamTracers:

    def _make_container(self) -> NexusStreamTracers:
        mock_network = MagicMock()
        mock_network.get_load_status.return_value = None
        return NexusStreamTracers(parent_network=mock_network)

    def _make_tracer(self, name, component, tracer=None, concentration=None):
        return NexusStreamTracer(
            date='01/01/2020', date_format=DateFormat.MM_DD_YYYY, unit_system=UnitSystem.ENGLISH,
            name=name, component=component, tracer=tracer, concentration=concentration,
        )

    def test_get_all_returns_added_tracers(self):
        container = self._make_container()
        t1 = self._make_tracer('SEAWTR', 'WATER', 'SALT', 1.0)
        t2 = self._make_tracer('TRTWTR', 'WATER', 'SALT', 1.0)
        container._add_to_memory([t1, t2])
        result = list(container.get_all())
        assert len(result) == 2
        assert t1 in result
        assert t2 in result

    def test_get_by_name_case_insensitive(self):
        container = self._make_container()
        t = self._make_tracer('SEAWTR', 'WATER')
        container._add_to_memory([t])
        assert container.get_by_name('seawtr') is t
        assert container.get_by_name('SEAWTR') is t
        assert container.get_by_name('SeAwTr') is t

    def test_get_by_name_returns_none_for_missing(self):
        container = self._make_container()
        container._add_to_memory([self._make_tracer('SEAWTR', 'WATER')])
        assert container.get_by_name('NONEXISTENT') is None

    def test_component_map_keys_uppercased(self):
        container = self._make_container()
        container._add_to_memory([
            self._make_tracer('seawtr', 'water'),
            self._make_tracer('TRTWTR', 'WATER'),
            self._make_tracer('GASSTREAM', 'GAS'),
        ])
        cm = container.component_map
        assert cm == {'SEAWTR': 'WATER', 'TRTWTR': 'WATER', 'GASSTREAM': 'GAS'}

    def test_component_map_excludes_none_name_or_component(self):
        container = self._make_container()
        # Entry with None name should be excluded
        container._add_to_memory([
            NexusStreamTracer(name=None, component='WATER', date='01/01/2020', date_format=DateFormat.MM_DD_YYYY,
                              unit_system=UnitSystem.ENGLISH),
            NexusStreamTracer(name='VALID', component=None, date='01/01/2020', date_format=DateFormat.MM_DD_YYYY,
                              unit_system=UnitSystem.ENGLISH),
            NexusStreamTracer(name='GOOD', component='GAS', date='01/01/2020', date_format=DateFormat.MM_DD_YYYY,
                              unit_system=UnitSystem.ENGLISH),
        ])
        assert container.component_map == {'GOOD': 'GAS'}


# Integration: STREAM_TRACER parsed from surface file and well types set

class TestNexusNetworkStreamTracerIntegration:
    """Tests that NexusNetwork correctly parses STREAM_TRACER blocks from surface
    files and uses the component_map to classify injector well types."""

    start_date = '01/01/2020'

    # Minimal surface file with a STREAM_TRACER block and a WELLS table
    surface_content = """\
BLACKOIL

STREAM_TRACER
NAME       COMPONENT   TRACER   CONCENTRATION
SEAWTR     WATER       SALT     1.0
TRTWTR     WATER       SALT     1.0
GASSTREAM  GAS         GASTR    0.5
ENDSTREAM_TRACER

WELLS
NAME       STREAM      DATUM    ONTIME
PROD_WELL  PRODUCER    15000    1.0
WINJ_SEA   SEAWTR      16000    1.0
WINJ_TRT   TRTWTR      16100    1.0
GINJ_1     GASSTREAM   15500    1.0
ENDWELLS
"""

    fcs_content = """\
DESC test model
RUN_UNITS ENGLISH
DEFAULT_UNITS ENGLISH
DATEFORMAT DD/MM/YYYY

RECURRENT_FILES
RUNCONTROL /runcontrol.dat
WELLS Set 1 /wells.dat
SURFACE Network 1 /surface.dat
"""

    runcontrol_content = f"""\
START {start_date}
TIME 01/01/2021
"""

    wells_content = """\
WELLSPEC PROD_WELL
IW JW LW RADW
1 1 1 0.354

WELLSPEC WINJ_SEA
IW JW LW RADW
2 1 1 0.354

WELLSPEC WINJ_TRT
IW JW LW RADW
3 1 1 0.354

WELLSPEC GINJ_1
IW JW LW RADW
4 1 1 0.354
"""

    def test_stream_tracers_parsed(self, mocker: MockerFixture):
        """NexusNetwork.stream_tracers contains all rows from the STREAM_TRACER block."""
        def mock_open_wrapper(filename, mode='r'):
            return mock_multiple_files(mocker, filename, potential_file_dict={
                '/fcs_file.fcs': self.fcs_content,
                '/surface.dat': self.surface_content,
                '/wells.dat': self.wells_content,
                '/runcontrol.dat': self.runcontrol_content,
            }).return_value

        mocker.patch('builtins.open', mock_open_wrapper)
        mocker.patch('os.path.isfile', Mock(return_value=True))
        mocker.patch('os.listdir', Mock(return_value=[]))

        nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/fcs_file.fcs', mock_open=False)
        nexus_sim.start_date = self.start_date

        stream_tracers = list(nexus_sim.network.stream_tracers.get_all())

        names = {st.name.upper() for st in stream_tracers if st.name is not None}
        assert 'SEAWTR' in names
        assert 'TRTWTR' in names
        assert 'GASSTREAM' in names

        seawtr = nexus_sim.network.stream_tracers.get_by_name('SEAWTR')
        assert seawtr is not None
        assert seawtr.component is not None
        assert seawtr.component.upper() == 'WATER'
        assert seawtr.tracer is not None
        assert seawtr.tracer.upper() == 'SALT'
        assert seawtr.concentration == pytest.approx(1.0)

    def test_component_map_populated(self, mocker: MockerFixture):
        """stream_tracer_map and stream_tracers.component_map return the correct dict."""
        def mock_open_wrapper(filename, mode='r'):
            return mock_multiple_files(mocker, filename, potential_file_dict={
                '/fcs_file.fcs': self.fcs_content,
                '/surface.dat': self.surface_content,
                '/wells.dat': self.wells_content,
                '/runcontrol.dat': self.runcontrol_content,
            }).return_value

        mocker.patch('builtins.open', mock_open_wrapper)
        mocker.patch('os.path.isfile', Mock(return_value=True))
        mocker.patch('os.listdir', Mock(return_value=[]))

        nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/fcs_file.fcs', mock_open=False)
        nexus_sim.start_date = self.start_date

        cm = nexus_sim.network.stream_tracer_map
        assert cm.get('SEAWTR') == 'WATER'
        assert cm.get('TRTWTR') == 'WATER'
        assert cm.get('GASSTREAM') == 'GAS'

    def test_water_injectors_classified_correctly(self, mocker: MockerFixture):
        """Wells whose STREAM maps to WATER via STREAM_TRACER are classified as WATER_INJECTOR."""
        def mock_open_wrapper(filename, mode='r'):
            return mock_multiple_files(mocker, filename, potential_file_dict={
                '/fcs_file.fcs': self.fcs_content,
                '/surface.dat': self.surface_content,
                '/wells.dat': self.wells_content,
                '/runcontrol.dat': self.runcontrol_content,
            }).return_value

        mocker.patch('builtins.open', mock_open_wrapper)
        mocker.patch('os.path.isfile', Mock(return_value=True))
        mocker.patch('os.listdir', Mock(return_value=[]))

        nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/fcs_file.fcs', mock_open=False)
        nexus_sim.start_date = self.start_date

        # Force network load
        _ = nexus_sim.network.stream_tracers.get_all()

        producer = nexus_sim.wells.get('PROD_WELL')
        winj_sea = nexus_sim.wells.get('WINJ_SEA')
        winj_trt = nexus_sim.wells.get('WINJ_TRT')
        ginj = nexus_sim.wells.get('GINJ_1')

        if producer is not None:
            assert producer.well_type == WellType.PRODUCER
        if winj_sea is not None:
            assert winj_sea.well_type == WellType.WATER_INJECTOR, \
                f"Expected WATER_INJECTOR for WINJ_SEA (stream=SEAWTR), got {winj_sea.well_type}"
        if winj_trt is not None:
            assert winj_trt.well_type == WellType.WATER_INJECTOR, \
                f"Expected WATER_INJECTOR for WINJ_TRT (stream=TRTWTR), got {winj_trt.well_type}"
        if ginj is not None:
            assert ginj.well_type == WellType.GAS_INJECTOR, \
                f"Expected GAS_INJECTOR for GINJ_1 (stream=GASSTREAM), got {ginj.well_type}"
