"""This module contains the NexusConstraint class, which is used to represent a constraint in the Nexus model."""
from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Constraint import Constraint
from ResSimpy.Enums.UnitsEnum import UnitSystem


@dataclass(repr=False)
class NexusConstraint(Constraint):
    """Attributes:
    name (str): name of the well (NAME)
    max_surface_oil_rate (float): max surface oil rate (QOSMAX)
    max_surface_gas_rate (float): max surface gas rate (QGSMAX)
    max_surface_water_rate (float): max surface (QWSMAX)
    max_surface_liquid_rate (float): max surface liquid rate (QLIQSMAX)
    max_hc_molar_rate (float): Max hc molar rate (QMHCMAX)
    max_reverse_surface_oil_rate (float): max reverse surface oil rate (QOSMAX-)
    max_reverse_surface_gas_rate (float): max reverse surface gas rate (QGSMAX-)
    max_reverse_surface_water_rate (float): max reverse surface water rate (QWSMAX-)
    max_reverse_surface_liquid_rate (float): max reverse surface liquid rate (QLIQSMAX-)
    max_reservoir_oil_rate (float): max reservoir oil rate (QOMAX)
    max_reservoir_gas_rate (float): max reservoir gas rate (QGMAX)
    max_reservoir_water_rate (float): max reservoir water rate (QWMAX)
    max_reservoir_liquid_rate (float): max reservoir liquid rate (QLIQMAX)
    max_reservoir_total_fluids_rate (float): max reservoir total fluids rate (QALLMAX)
    max_reservoir_hc_rate (float): max reservoir hc rate (QHCMAX)
    max_reverse_reservoir_oil_rate (float): max reverse reservoir oil rate (QOMAX-)
    max_reverse_reservoir_gas_rate (float): max reverse reservoir gas rate (QGMAX-)
    max_reverse_reservoir_water_rate (float): max reverse reservoir water rate (QWMAX-)
    max_reverse_reservoir_liquid_rate (float): max reverse reservoir liquid rate (QLIQMAX-)
    max_reverse_reservoir_total_fluids_rate (float): max reverse reservoir total fluids rate (QALLMAX-)
    max_reverse_reservoir_hc_rate (float): max reverse reservoir hc rate (QHCMAX-)
    min_pressure (float): min pressure (PMIN)
    max_pressure (float): max pressure (PMAX)
    max_wag_water_pressure (float): max wag water pressure (PWMAX)
    max_wag_gas_pressure (float): max wag gas pressure (PGMAX)
    bottom_hole_pressure (float): bottom hole pressure (BHP)
    tubing_head_pressure (float): tubing head pressure (THP)
    min_surface_oil_rate (float): min surface oil rate (QOSMIN)
    min_surface_gas_rate (float): min surface gas rate (QGSMIN)
    min_surface_water_rate (float): min surface water rate (QWSMIN)
    min_surface_liquid_rate (float): min surface liquid rate (QLIQSMIN)
    min_reservoir_oil_rate (float): min reservoir oil rate (QOMIN)
    min_reservoir_gas_rate (float): min reservoir gas rate (QGMIN)
    min_reservoir_water_rate (float): min reservoir water rate (QWMIN)
    min_reservoir_liquid_rate (float): min reservoir liquid rate (QLIQMIN)
    min_reservoir_total_fluids_rate (float): min reservoir total fluids rate (QALLMIN)
    min_reservoir_hc_rate (float): min reservoir hc rate (QHCMIN)
    min_reverse_surface_oil_rate (float): min reservoir oil rate (QOSMIN-)
    min_reverse_surface_gas_rate (float): min reservoir gas rate (QGSMIN-)
    min_reverse_surface_water_rate (float): min reservoir water rate (QWSMIN-)
    min_reverse_surface_liquid_rate (float): min reservoir liquid rate (QLIQSMIN-)
    min_reverse_reservoir_oil_rate (float): min reverse reservoir oil rate (QOMIN-)
    min_reverse_reservoir_gas_rate (float): min reverse reservoir gas rate (QGMIN-)
    min_reverse_reservoir_water_rate (float): min reverse reservoir water rate (QWMIN-)
    min_reverse_reservoir_liquid_rate (float): min reverse reservoir liquid rate (QLIQMIN-)
    min_reverse_reservoir_total_fluids_rate (float): min reverse reservoir total fluids rate (QALLMIN-)
    min_reverse_reservoir_hc_rate (float): min reverse reservoir hc rate (QHCMIN-)
    max_watercut (float): max watercut (WCUTMAX)
    max_watercut_plug (float): max watercut plug (WCUTPLUG)
    max_watercut_plugplus (float): max watercut plugplus (WCUTPLUGPLUS)
    max_watercut_perf (float): max watercut perf (WCUTPERF)
    max_watercut_perfplus (float): max watercut perfplus (WCUTPERFPLUS)
    max_wor (float): max wor (WORMAX)
    max_wor_plug (float): max wor plug (WORPLUG)
    max_wor_plug_plus (float): max wor plug plus (WORPLUGPLUS)
    max_wor_perf (float): max wor perf (WORPERF)
    max_wor_perfplus (float): max wor perfplus (WORPERFPLUS)
    max_gor (float): max gor (GORMAX)
    max_gor_plug (float): max gor plug (GORPLUG)
    max_gor_plug_plus (float): max gor plug plus (GORPLUGPLUS)
    max_gor_perf (float): max gor perf (GORPERF)
    max_gor_perfplus (float): max gor perfplus (GORPERFPLUS)
    max_lgr (float): max lgr (LGRMAX)
    max_lgr_plug (float): max lgr plug (LGRPLUG)
    max_lgr_plug_plus (float): max lgr plug plus (LGRPLUGPLUS)
    max_lgr_perf (float): max lgr perf (LGRPERF)
    max_lgr_perfplus (float): max lgr perfplus (LGRPERFPLUS)
    max_cum_gas_prod (float): max cum gas prod (CGLIM)
    max_cum_water_prod (float): max cum water prod (CWLIM)
    max_cum_oil_prod (float): max cum oil prod (COLIM).

    artificial_lift_number (int): artificial lift number within the hydraulic table (ALQ)
    max_choke_setting (float): maximum choke/ICD/valve setting (SETTING)
    min_gas_lift_efficiency (float): minimum gas lift efficiency below which the connection will be shut in(GLEFMIN)
    gl_additive_correction (float): additive correction term to value of gas/liquid ratio from optimal gl \
            tables (GLRADD)
    active_node (bool): active/inactive node/well (ACTIVATE)
    pump_power (float): power for the pump (POWER)
    pump_speed (float): maximum speed of the pump/esp/compressor (SPEED)
    choke_limit (str): ON/OFF for whether the esp should exceed the choke limit (CHOKELIMIT)
    manifold_position (int): position in the manifold for the well (POSITION)

    """

    well_name: Optional[str] = None
    max_surface_oil_rate: Optional[float] = None
    max_surface_gas_rate: Optional[float] = None
    max_surface_water_rate: Optional[float] = None
    max_surface_liquid_rate: Optional[float] = None
    max_hc_molar_rate: Optional[float] = None
    max_reverse_surface_oil_rate: Optional[float] = None
    max_reverse_surface_gas_rate: Optional[float] = None
    max_reverse_surface_water_rate: Optional[float] = None
    max_reverse_surface_liquid_rate: Optional[float] = None
    max_reservoir_oil_rate: Optional[float] = None
    max_reservoir_gas_rate: Optional[float] = None
    max_reservoir_water_rate: Optional[float] = None
    max_reservoir_liquid_rate: Optional[float] = None
    max_reservoir_hc_rate: Optional[float] = None
    max_reverse_reservoir_oil_rate: Optional[float] = None
    max_reverse_reservoir_gas_rate: Optional[float] = None
    max_reverse_reservoir_water_rate: Optional[float] = None
    max_reverse_reservoir_liquid_rate: Optional[float] = None
    max_reverse_reservoir_total_fluids_rate: Optional[float] = None
    max_reverse_reservoir_hc_rate: Optional[float] = None
    max_avg_comp_dp: Optional[float] = None
    max_comp_dp: Optional[float] = None

    min_pressure: Optional[float] = None
    max_pressure: Optional[float] = None
    max_wag_water_pressure: Optional[float] = None
    max_wag_gas_pressure: Optional[float] = None
    min_reverse_surface_oil_rate: Optional[float] = None
    min_reverse_surface_gas_rate: Optional[float] = None
    min_reverse_surface_water_rate: Optional[float] = None
    min_reverse_surface_liquid_rate: Optional[float] = None
    min_surface_oil_rate: Optional[float] = None
    min_surface_gas_rate: Optional[float] = None
    min_surface_water_rate: Optional[float] = None
    min_surface_liquid_rate: Optional[float] = None
    min_reservoir_oil_rate: Optional[float] = None
    min_reservoir_gas_rate: Optional[float] = None
    min_reservoir_water_rate: Optional[float] = None
    min_reservoir_liquid_rate: Optional[float] = None
    min_reservoir_total_fluids_rate: Optional[float] = None
    min_reservoir_hc_rate: Optional[float] = None
    min_reverse_reservoir_oil_rate: Optional[float] = None
    min_reverse_reservoir_gas_rate: Optional[float] = None
    min_reverse_reservoir_water_rate: Optional[float] = None
    min_reverse_reservoir_liquid_rate: Optional[float] = None
    min_reverse_reservoir_total_fluids_rate: Optional[float] = None
    min_reverse_reservoir_hc_rate: Optional[float] = None
    max_watercut: Optional[float] = None
    max_watercut_plug: Optional[float] = None
    max_watercut_plugplus: Optional[float] = None
    max_watercut_perf: Optional[float] = None
    max_watercut_perfplus: Optional[float] = None
    max_wor: Optional[float] = None
    max_wor_plug: Optional[float] = None
    max_wor_plug_plus: Optional[float] = None
    max_wor_perf: Optional[float] = None
    max_wor_perfplus: Optional[float] = None
    max_gor: Optional[float] = None
    max_gor_plug: Optional[float] = None
    max_gor_plug_plus: Optional[float] = None
    max_gor_perf: Optional[float] = None
    max_gor_perfplus: Optional[float] = None
    gor_limit: Optional[float] = None
    gor_limit_exponent: Optional[float] = None
    gor_limit_frequency: Optional[float] = None
    max_lgr: Optional[float] = None
    max_lgr_plug: Optional[float] = None
    max_lgr_plug_plus: Optional[float] = None
    max_lgr_perf: Optional[float] = None
    max_lgr_perfplus: Optional[float] = None
    max_cum_gas_prod: Optional[float] = None
    max_cum_water_prod: Optional[float] = None
    max_cum_oil_prod: Optional[float] = None

    max_qmult_total_reservoir_rate: Optional[float] = None
    convert_qmult_to_reservoir_barrels: Optional[bool] = None
    qmult_oil_rate: Optional[float] = None
    qmult_water_rate: Optional[float] = None
    qmult_gas_rate: Optional[float] = None
    use_qmult_qoil_surface_rate: Optional[bool] = None
    use_qmult_qwater_surface_rate: Optional[bool] = None
    use_qmult_qgas_surface_rate: Optional[bool] = None
    use_qmult_qoilqwat_surface_rate: Optional[bool] = None

    artificial_lift_number: Optional[int] = None
    max_choke_setting: Optional[float] = None
    min_gas_lift_efficiency: Optional[float] = None
    gl_additive_correction: Optional[float] = None
    active_node: Optional[bool] = None
    pump_power: Optional[float] = None
    pump_speed: Optional[float] = None
    choke_limit: Optional[str] = None
    manifold_position: Optional[int] = None

    clear_all: Optional[bool] = None
    clear_q: Optional[bool] = None
    clear_limit: Optional[bool] = None
    clear_alq: Optional[bool] = None
    clear_p: Optional[bool] = None

    def __init__(self, properties_dict: dict[str, None | int | str | float | UnitSystem]) -> None:
        """Initialises the NexusConstraint class.

        Args:
            properties_dict (dict): dict of the properties to set on the object.
        """
        super(Constraint, self).__init__({})
        for key, prop in properties_dict.items():
            self.__setattr__(key, prop)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
        nexus_mapping: dict[str, tuple[str, type]] = {
            'WELL': ('well_name', str),
            'NAME': ('name', str),
            # Special keywords - QMULT
            'QALLRMAX_MULT': ('convert_qmult_to_reservoir_barrels', bool),
            'QOSMAX_MULT': ('use_qmult_qoil_surface_rate', bool),
            'QWSMAX_MULT': ('use_qmult_qwater_surface_rate', bool),
            'QGSMAX_MULT': ('use_qmult_qgas_surface_rate', bool),
            'QLIQSMAX_MULT': ('use_qmult_qoilqwat_surface_rate', bool),
            # Special Clear keywords
            'CLEAR': ('clear_all', bool),
            'CLEARQ': ('clear_q', bool),
            'CLEARP': ('clear_p', bool),
            'CLEARLIMIT': ('clear_limit', bool),
            'CLEARALQ': ('clear_alq', bool),
            }
        nexus_mapping.update(NexusConstraint.get_limit_constraints_map())
        nexus_mapping.update(NexusConstraint.get_pressure_constraints_map())
        nexus_mapping.update(NexusConstraint.get_rate_constraints_map())
        nexus_mapping.update(NexusConstraint.get_alq_constraints_map())
        return nexus_mapping

    @staticmethod
    def get_rate_constraints_map() -> dict[str, tuple[str, type]]:

        nexus_mapping: dict[str, tuple[str, type]] = {
            'QALLRMAX': ('max_qmult_total_reservoir_rate', float),

            'QOSMAX': ('max_surface_oil_rate', float),
            'QGSMAX': ('max_surface_gas_rate', float),
            'QWSMAX': ('max_surface_water_rate', float),
            'QLIQSMAX': ('max_surface_liquid_rate', float),
            'QMHCMAX': ('max_hc_molar_rate', float),
            'QOSMAX-': ('max_reverse_surface_oil_rate', float),
            'QGSMAX-': ('max_reverse_surface_gas_rate', float),
            'QWSMAX-': ('max_reverse_surface_water_rate', float),
            'QLIQSMAX-': ('max_reverse_surface_liquid_rate', float),
            'QOMAX': ('max_reservoir_oil_rate', float),
            'QGMAX': ('max_reservoir_gas_rate', float),
            'QWMAX': ('max_reservoir_water_rate', float),
            'QLIQMAX': ('max_reservoir_liquid_rate', float),
            'QALLMAX': ('max_reservoir_total_fluids_rate', float),
            'QHCMAX': ('max_reservoir_hc_rate', float),
            'QOMAX-': ('max_reverse_reservoir_oil_rate', float),
            'QGMAX-': ('max_reverse_reservoir_gas_rate', float),
            'QWMAX-': ('max_reverse_reservoir_water_rate', float),
            'QLIQMAX-': ('max_reverse_reservoir_liquid_rate', float),
            'QALLMAX-': ('max_reverse_reservoir_total_fluids_rate', float),
            'QHCMAX-': ('max_reverse_reservoir_hc_rate', float),
            'QOSMIN': ('min_surface_oil_rate', float),
            'QGSMIN': ('min_surface_gas_rate', float),
            'QWSMIN': ('min_surface_water_rate', float),
            'QLIQSMIN': ('min_surface_liquid_rate', float),
            'QOMIN': ('min_reservoir_oil_rate', float),
            'QGMIN': ('min_reservoir_gas_rate', float),
            'QWMIN': ('min_reservoir_water_rate', float),
            'QLIQMIN': ('min_reservoir_liquid_rate', float),
            'QALLMIN': ('min_reservoir_total_fluids_rate', float),
            'QHCMIN': ('min_reservoir_hc_rate', float),
            'QOSMIN-': ('min_reverse_surface_oil_rate', float),
            'QGSMIN-': ('min_reverse_surface_gas_rate', float),
            'QWSMIN-': ('min_reverse_surface_water_rate', float),
            'QLIQSMIN-': ('min_reverse_surface_liquid_rate', float),
            'QOMIN-': ('min_reverse_reservoir_oil_rate', float),
            'QGMIN-': ('min_reverse_reservoir_gas_rate', float),
            'QWMIN-': ('min_reverse_reservoir_water_rate', float),
            'QLIQMIN-': ('min_reverse_reservoir_liquid_rate', float),
            'QALLMIN-': ('min_reverse_reservoir_total_fluids_rate', float),
            'QHCMIN-': ('min_reverse_reservoir_hc_rate', float),

            'QOIL': ('qmult_oil_rate', float),
            'QWATER': ('qmult_water_rate', float),
            'QGAS': ('qmult_gas_rate', float),
            'DPBHAVG': ('max_avg_comp_dp', float),
            'DPBHMX': ('max_comp_dp', float),
            }
        return nexus_mapping

    @staticmethod
    def get_pressure_constraints_map() -> dict[str, tuple[str, type]]:
        nexus_mapping: dict[str, tuple[str, type]] = {
            'PMIN': ('min_pressure', float),
            'PMAX': ('max_pressure', float),
            'PWMAX': ('max_wag_water_pressure', float),
            'PGMAX': ('max_wag_gas_pressure', float),
            'BHP': ('bottom_hole_pressure', float),
            'THP': ('tubing_head_pressure', float),
            }
        return nexus_mapping

    @staticmethod
    def get_limit_constraints_map() -> dict[str, tuple[str, type]]:
        nexus_mapping: dict[str, tuple[str, type]] = {
            'WCUTMAX': ('max_watercut', float),
            'WCUTPLUG': ('max_watercut_plug', float),
            'WCUTPLUGPLUS': ('max_watercut_plugplus', float),
            'WCUTPERF': ('max_watercut_perf', float),
            'WCUTPERFPLUS': ('max_watercut_perfplus', float),
            'WORMAX': ('max_wor', float),
            'WORPLUG': ('max_wor_plug', float),
            'WORPLUGPLUS': ('max_wor_plug_plus', float),
            'WORPERF': ('max_wor_perf', float),
            'WORPERFPLUS': ('max_wor_perfplus', float),
            'GORLIM': ('gor_limit', float),
            'EXPONENT': ('gor_limit_exponent', float),
            'FREQUENCY': ('gor_limit_frequency', float),
            'GORMAX': ('max_gor', float),
            'GORPLUG': ('max_gor_plug', float),
            'GORPLUGPLUS': ('max_gor_plug_plus', float),
            'GORPERF': ('max_gor_perf', float),
            'GORPERFPLUS': ('max_gor_perfplus', float),
            'LGRMAX': ('max_lgr', float),
            'LGRPLUG': ('max_lgr_plug', float),
            'LGRPLUGPLUS': ('max_lgr_plug_plus', float),
            'LGRPERF': ('max_lgr_perf', float),
            'LGRPERFPLUS': ('max_lgr_perfplus', float),
            'CGLIM': ('max_cum_gas_prod', float),
            'CWLIM': ('max_cum_water_prod', float),
            'COLIM': ('max_cum_oil_prod', float),
            }
        return nexus_mapping

    @staticmethod
    def get_alq_constraints_map() -> dict[str, tuple[str, type]]:
        """Gets the nexus mapping for artificial lift constraints."""
        nexus_mapping: dict[str, tuple[str, type]] = {
            'ALQ': ('artificial_lift_number', int),
            'SETTING': ('max_choke_setting', float),
            'GLEFMIN': ('min_gas_lift_efficiency', float),
            'GLRADD': ('gl_additive_correction', float),
            'ACTIVATE': ('active_node', bool),
            'POWER': ('pump_power', float),
            'SPEED': ('pump_speed', float),
            'CHOKELIMIT': ('choke_limit', str),
            'POSITION': ('manifold_position', int),
            }
        return nexus_mapping

    def update(self, new_data: dict[str, None | int | str | float | UnitSystem], nones_overwrite: bool = False):
        """Updates attributes in the object based on the dictionary provided."""
        for k, v in new_data.items():
            if v is not None or nones_overwrite:
                setattr(self, k, v)

    def to_table_line(self, headers: list[str]) -> str:
        """String representation of the constraint for entry to an inline constraint table.

        Args:
            headers (list[str]): Unused for nexusconstraint, provide an empty list
        """
        qmult_control_key_words = ['QALLRMAX_MULT', 'QOSMAX_MULT', 'QWSMAX_MULT', 'QGSMAX_MULT', 'QLIQSMAX_MULT']
        skip_attributes = ['date', 'unit_system', 'NAME', 'ACTIVATE', 'QOIL', 'QWATER', 'QGAS', 'WELL', 'control_mode']
        clear_attributes = ['CLEAR', 'CLEARQ', 'CLEARP', 'CLEARLIMIT', 'CLEARALQ']

        if headers:
            warnings.warn('Headers is currently not used in the constraint to line call')

        if self.name is not None:
            constraint_string = self.name
        elif self.well_name is not None:
            constraint_string = self.well_name
        else:
            raise ValueError('Must have a well or node name for returning a constraint to a string')

        for attribute, value in self.to_dict(keys_in_keyword_style=True).items():
            if value and attribute in qmult_control_key_words:
                constraint_string += (' ' + attribute.replace('_MULT', '') + ' MULT')
            elif value is None or attribute in skip_attributes:
                continue
            elif value and attribute in clear_attributes:
                constraint_string += ' ' + attribute
            else:
                constraint_string += (' ' + attribute + ' ' + str(value))

        if self.active_node:
            constraint_string += ' ACTIVATE'
        elif self.active_node is not None:
            # equivalent to active node being False
            constraint_string += ' DEACTIVATE'

        constraint_string += '\n'
        return constraint_string

    def write_qmult_table(self) -> list[str]:
        """Writes out a QMULT table from a constraint that uses the following attributes.
        'QOIL': ('qmult_oil_rate', float).
        'QWATER': ('qmult_water_rate', float).
        'QGAS': ('qmult_gas_rate', float).

        Returns:
            list[str] with a representation of the QMULT table with a new line as a new entry in the list.
        """
        table_to_return = ['QMULT\n', 'WELL QOIL QGAS QWATER\n']
        qmult_values = self.write_qmult_values()
        table_to_return.append(qmult_values)
        table_to_return.append('ENDQMULT\n')

        return table_to_return

    def write_qmult_values(self) -> str:
        """Writes out the values for a QMULT table, callable on its own or using the write_qmult_table method."""
        qmult_values_keywords = ['qmult_oil_rate', 'qmult_gas_rate', 'qmult_water_rate']
        if self.name is not None:
            string_to_return = self.name
        elif self.well_name is not None:
            string_to_return = self.well_name
        else:
            raise ValueError('Must have a well or node name for returning a qmult table')

        for keyword in qmult_values_keywords:
            value = getattr(self, keyword, None)
            if value is None:
                string_to_return += ' NA'
            else:
                string_to_return += f' {str(value)}'
        string_to_return += '\n'
        return string_to_return
