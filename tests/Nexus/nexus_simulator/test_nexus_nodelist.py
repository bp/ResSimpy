from pytest_mock import MockerFixture

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusConList import NexusConList
from ResSimpy.Nexus.DataModels.Network.NexusNodeList import NexusNodeList
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusWellList import NexusWellList
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from ResSimpy.Nexus.nexus_load_list_table import load_table_to_lists


class TestNexusNodeList:
    file_content = """TIME 01/01/2020
    NODELIST nodelist_name
    ADD
    node3
    node4
    ! comment
    ENDNODELIST
"""

    def test_nexus_nodelist_add(self):
        # Arrange
        existing_nodelist = NexusNodeList(
            name="nodelist_name",
            elements_in_the_list=["node1", "node2"],
            date="01/12/2019",
            date_format=DateFormat.DD_MM_YYYY,
        )
        expected_nodelist = NexusNodeList(
            name="nodelist_name",
            elements_in_the_list=["node1", "node2", "node3", "node4"],
            date="01/01/2020",
            date_format=DateFormat.DD_MM_YYYY,
        )
        file_as_list = self.file_content.splitlines()

        existing_nodelist = NexusNodeList(
            name="nodelist_name",
            elements_in_the_list=["node1", "node2"],
            date="01/12/2019",
            date_format=DateFormat.DD_MM_YYYY,
        )
        expected_nodelist = NexusNodeList(
            name="nodelist_name",
            elements_in_the_list=["node1", "node2", "node3", "node4"],
            date="01/01/2020",
            date_format=DateFormat.DD_MM_YYYY,
        )
        file_as_list = self.file_content.splitlines()

        # Act
        nodelist = load_table_to_lists(
            file_as_list=file_as_list,
            row_object=NexusNodeList,
            current_date="01/01/2020",
            previous_lists=[existing_nodelist],
            date_format=DateFormat.DD_MM_YYYY,
            table_header="NODELIST",
            table_start_index=0,
        )[0][0]

        # Assert
        assert nodelist == expected_nodelist

    def test_nexus_nodelist_conlist_and_welllist(self, mocker: MockerFixture):
        # Arrange
        mocker.patch(
            "ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4", return_value="uuid_1"
        )
        expected_welllists = [
            NexusWellList(
                name="welllist_name",
                elements_in_the_list=["well_1", "well_2", "well_3"],
                date="01/01/2020",
                date_format=DateFormat.MM_DD_YYYY,
            ),
            NexusWellList(
                name="welllist_name",
                elements_in_the_list=["well_2", "well_3"],
                date="01/01/2023",
                date_format=DateFormat.MM_DD_YYYY,
            ),
        ]
        expected_conlists = [
            NexusConList(
                name="conlist_name",
                elements_in_the_list=["wellcon_1", "wellcon_3", "well_1"],
                date="01/01/2020",
                date_format=DateFormat.MM_DD_YYYY,
            ),
            NexusConList(
                name="conlist_name",
                elements_in_the_list=["wellcon_1", "well_1"],
                date="01/01/2023",
                date_format=DateFormat.MM_DD_YYYY,
            ),
        ]

        expected_nodelists = [
            NexusNodeList(
                name="nodelist_name",
                elements_in_the_list=["node_1", "node_2", "node_3"],
                date="01/01/2020",
                date_format=DateFormat.MM_DD_YYYY,
            ),
            NexusNodeList(
                name="nodelist_name",
                elements_in_the_list=["node_1", "node_2", "node_3", "node_4"],
                date="01/01/2023",
                date_format=DateFormat.MM_DD_YYYY,
            ),
            NexusNodeList(
                name="nodelist_name",
                elements_in_the_list=["node_1", "node_2", "node_4"],
                date="01/01/2023",
                date_format=DateFormat.MM_DD_YYYY,
            ),
        ]

        file_as_list = """
        TIME 01/01/2020
        WELLLIST welllist_name
        ADD
        well_1
        well_2

        well_3
        ENDWELLLIST
        CONLIST conlist_name
        ADD
        wellcon_1
        wellcon_3
        ! comment

        well_1
        ENDCONLIST
        NODELIST nodelist_name
        ADD
        node_1
        node_2
        node_3
        ENDNODELIST

        TIME 01/01/2023
        WELLLIST welllist_name
        REMOVE
        well_1
        ENDWELLLIST

        CONLIST conlist_name    !Comment
        REMOVE
        wellcon_3
        ENDCONLIST

        NODELIST nodelist_name
        ADD
        node_4
        ! comment
        ENDNODELIST

        NODELIST nodelist_name
        REMOVE
        node_3
        ENDNODELIST
        """.splitlines()

        nexus_file = NexusFile(location="", file_content_as_list=file_as_list)

        # Act
        nexus_obj_dict, _ = collect_all_tables_to_objects(
            nexus_file=nexus_file,
            table_object_map={
                "WELLLIST": NexusWellList,
                "CONLIST": NexusConList,
                "NODELIST": NexusNodeList,
            },
            start_date="01/01/2019",
            default_units=UnitSystem.ENGLISH,
            date_format=DateFormat.MM_DD_YYYY,
        )
        # Assert
        assert nexus_obj_dict["WELLLIST"] == expected_welllists
        assert nexus_obj_dict["CONLIST"] == expected_conlists
        assert nexus_obj_dict["NODELIST"] == expected_nodelists
