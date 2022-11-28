from typing import Optional

import resqpy.model as rq
import resqpy.well as rqw
import resqpy.crs as rqc
import resqpy.olio.write_data as wd
import resqpy.weights_and_measures as wam
import os
from inspect import getsourcefile
from ResSimpy.Nexus.NexusSimulator import NexusSimulator
import ResSimpy.Nexus.nexus_file_operations as nexus_file_operations


class ResqmlToNexusDeck:

    def __init__(self, epc_path: str, output_folder: str, is_gas_model: bool = False,
                 water_oil_contact: Optional[float] = None, gas_water_contact: Optional[float] = None,
                 american_run_units: bool = True, pimatch_process=True, root_name='Flynn'):
        self.epc_path = epc_path
        self.output_folder = os.path.join(output_folder, 'nexus_data')
        self.__water_oil_contact = water_oil_contact
        self.__american_run_units = american_run_units
        self.pimatch_process = pimatch_process
        self.root_name = root_name
        self.__is_gas_model = is_gas_model
        self.__gas_water_contact = gas_water_contact

        self.ntg_array = None
        self.poro_array = None
        self.permx_array = None
        self.permy_array = None
        self.permz_array = None
        self.sw_array = None

        self.reference_depth_feet = None
        self.reference_pressure_psi = None

        self.simulation = None

        self.__load_epc_model()

    def __load_epc_model(self):
        """Performs a series of validation checks on the supplied epc file and loads in the model if all is OK."""
        model = rq.Model(epc_file=self.epc_path)

        # Check there is only one grid on the model
        grid_list = model.parts(obj_type="IjkGridRepresentation")
        if len(grid_list) != 1:
            raise ValueError(
                f"RESQML to Nexus workflow can only handle 1 grid in epc files. There are {len(grid_list)} grids in "
                f"this EPC file.")

        # Load in the grid
        grid = model.grid()
        self.grid = grid

        # Check the grid units
        if grid.xy_units() != grid.z_units():
            raise ValueError(
                f"Grid units inconsistent between the xy axis which is in {grid.xy_units()} and the z axis which is in "
                f"{grid.z_units()}")

        # Check the Coordinate reference system
        self.crs = rqc.Crs(model, uuid=grid.crs_uuid)

        z1, z2 = grid.xyz_box(lazy=False)[:, 2]
        if self.crs.z_inc_down:
            z_deepest = z2
        else:
            z_deepest = -z1

        # Convert contact measurement to feet as template is in feet
        z_deepest = wam.convert_lengths(z_deepest, grid.z_units(), 'ft')

        input_units = 'ft' if self.__american_run_units is True else 'm'

        if self.__water_oil_contact is None and self.__is_gas_model is False:
            self.__water_oil_contact = z_deepest
        elif self.__water_oil_contact is not None and self.__is_gas_model is False:
            # Convert user entered water oil contact to feet
            self.__water_oil_contact = wam.convert_lengths(self.__water_oil_contact, input_units, 'ft')

        if self.__gas_water_contact is None and self.__is_gas_model is True:
            self.__gas_water_contact = z_deepest
        elif self.__gas_water_contact is not None and self.__is_gas_model is True:
            # Convert user entered gas water contact to feet
            self.__gas_water_contact = wam.convert_lengths(self.__gas_water_contact, input_units, 'ft')

        if self.reference_depth_feet is None:
            self.reference_depth_feet = z_deepest

        if self.reference_pressure_psi is None:
            self.reference_pressure_psi = 0.5 * self.reference_depth_feet  # Water Pressure Gradient

    def create_nexus_deck(self):
        self.__create_basic_model()
        self.__create_grid_input_files()
        self.__create_nexus_grid_file()
        self.__update_model_values()

        # Reload grid file after creating it
        self.simulation.load_structured_grid_file()

        return self.simulation

    def get_model_template_location(self):
        if self.__is_gas_model:
            return os.path.split(getsourcefile(lambda: 0))[0] + '/Gas_Template_Model/main.fcs'
        else:
            return os.path.split(getsourcefile(lambda: 0))[0] + '/Oil_Template_Model/main.fcs'

    def __update_model_values(self):
        rock_file_path = os.path.join(self.output_folder, 'rock.dat')
        self.simulation.update_file_value(file_path=rock_file_path, token="PREF", new_value=self.reference_pressure_psi)

        init_equil_file_path = os.path.join(self.output_folder, 'init_equil.dat')
        self.simulation.update_file_value(file_path=init_equil_file_path, token="PINIT",
                                          new_value=self.reference_pressure_psi)

        if self.__is_gas_model:
            self.simulation.update_file_value(file_path=init_equil_file_path, token="GWC",
                                              new_value=self.__gas_water_contact)
            self.simulation.update_file_value(file_path=init_equil_file_path, token="DINIT",
                                              new_value=self.__gas_water_contact)
        else:
            self.simulation.update_file_value(file_path=init_equil_file_path, token="WOC",
                                              new_value=self.__water_oil_contact)
            self.simulation.update_file_value(file_path=init_equil_file_path, token="DINIT",
                                              new_value=self.__water_oil_contact)

        pvt_file_path = os.path.join(self.output_folder, 'pvt_water.dat')
        self.simulation.update_file_value(file_path=pvt_file_path, token="PREF", new_value=self.reference_pressure_psi)

    def __create_basic_model(self):
        base_folder = os.path.split(self.output_folder)[0]
        generic_model_location = self.get_model_template_location()
        self.simulation = NexusSimulator(origin=generic_model_location, destination=base_folder,
                                         nexus_data_name="nexus_data", manual_fcs_tidy_call=True,
                                         root_name=self.root_name, write_times=False)

    def __load_property_arrays(self):
        """ Load in the arrays from the models if they exist """
        grid = self.grid

        try:
            grid_properties = grid.property_collection.basic_static_property_parts_dict(share_perm_parts=True)

            self.ntg_array = grid.property_collection.cached_part_array_ref(grid_properties['NTG'])
            self.poro_array = grid.property_collection.cached_part_array_ref(grid_properties['PORO'])
            self.permx_array = grid.property_collection.cached_part_array_ref(grid_properties['PERMI'])
            self.permy_array = grid.property_collection.cached_part_array_ref(grid_properties['PERMJ'])
            self.permz_array = grid.property_collection.cached_part_array_ref(grid_properties['PERMK'])

            self.sw_array = grid.property_collection.single_array_ref(property_kind='saturation', citation_title='SW')
        except AssertionError as e:
            raise e
        except Exception as e:
            raise e

    def __create_grid_input_files(self):
        """Creates the input files for the structured grid file"""
        grid = self.grid

        self.__load_property_arrays()

        # Correct the grid geometry format before writing the CORP file
        grid.set_geometry_is_defined(treat_as_nan=None, complete_partial_pillars=False, nullify_partial_pillars=True,
                                     complete_all=True)

        # Create the CORP file
        grid.write_nexus_corp(os.path.join(self.output_folder, 'main_grid.corp'), write_nx_ny_nz=True,
                              write_corp_keyword=True, write_rh_keyword_if_needed=True,
                              global_xy_units=self.crs.xy_units, global_z_units=self.crs.xy_units,
                              write_units_keyword=True, local_coords=False, global_z_increasing_downward=True)

        # Output all the loaded arrays
        if self.ntg_array is not None:
            wd.write_array_to_ascii_file(os.path.join(self.output_folder, 'ntg.inc'), grid.extent_kji, self.ntg_array,
                                         nan_substitute_value=0.0)
        if self.poro_array is not None:
            wd.write_array_to_ascii_file(os.path.join(self.output_folder, 'poro.inc'), grid.extent_kji, self.poro_array,
                                         nan_substitute_value=0.0)
        if self.permx_array is not None:
            wd.write_array_to_ascii_file(os.path.join(self.output_folder, 'permx.inc'), grid.extent_kji,
                                         self.permx_array, nan_substitute_value=0.0)
        elif self.pimatch_process is True:
            raise ValueError("No Permeability array for the X axis found in PIMatch mode.")

        if self.permy_array is not None:
            wd.write_array_to_ascii_file(os.path.join(self.output_folder, 'permy.inc'), grid.extent_kji,
                                         self.permy_array, nan_substitute_value=0.0)
        if self.permz_array is not None:
            wd.write_array_to_ascii_file(os.path.join(self.output_folder, 'permz.inc'), grid.extent_kji,
                                         self.permz_array, nan_substitute_value=0.0)
        if self.sw_array is not None:
            wd.write_array_to_ascii_file(os.path.join(self.output_folder, 'sw.inc'), grid.extent_kji, self.sw_array,
                                         nan_substitute_value=0.0)

    def __create_nexus_grid_file(self):
        """
        Given a set of grid array options, output from resqpy_to_nexus_grid_inputs function,
        write out corp and grid property array includes into Nexus structured grid file.
        Returns:
            None - writes out data to Nexus structured grid file
        """

        output_folder = self.output_folder.replace('temp/', '', 1)

        # NTG property
        if self.ntg_array is not None:
            ntg_prop = 'NETGRS VALUE \nINCLUDE {}\n\n'.format(os.path.join(output_folder, 'ntg.inc'))
        else:
            ntg_prop = 'NETGRS CON \n 1.0 \n\n'

        # Permx property
        if self.permx_array is not None:
            kx_prop = 'KX VALUE \nINCLUDE {}\n\n'.format(os.path.join(output_folder, 'permx.inc'))
        else:
            kx_prop = 'KX CON \n 100 \n\n'

        # Permy property
        if self.permy_array is not None:
            ky_prop = 'KY VALUE \nINCLUDE {}\n\n'.format(os.path.join(output_folder, 'permy.inc'))
        else:
            ky_prop = 'KY MULT \n 1.0 KX \n\n'  # assumes areally isotropic

        # Permz property
        if self.permz_array is not None:
            kz_prop = 'KZ VALUE \nINCLUDE {}\n\n'.format(os.path.join(output_folder, 'permz.inc'))
        else:
            kz_prop = 'KZ MULT \n 0.1 KX \n\n'  # assumes kv/kh = 0.1

        # Porosity property
        if self.poro_array is not None:
            poro_prop = 'POROSITY VALUE \nINCLUDE {}\n\n'.format(os.path.join(output_folder, 'poro.inc'))
        else:
            poro_prop = 'POROSITY CON \n 0.2 \n\n'

        # Substitute in the template values and create the template file
        template_location = os.path.split(getsourcefile(lambda: 0))[0] + '/structured_grid_template.txt'

        substitutions = {'corp_file': os.path.join(output_folder, 'main_grid.corp'),
                         'ntg_prop': ntg_prop,
                         'kx_prop': kx_prop,
                         'ky_prop': ky_prop,
                         'kz_prop': kz_prop,
                         'poro_prop': poro_prop,
                         'NX': self.grid.ni,
                         'NY': self.grid.nj,
                         'NZ': self.grid.nk}

        output_file_name = os.path.join(self.output_folder, 'main_grid.dat')

        nexus_file_operations.create_templated_file(template_location=template_location, substitutions=substitutions,
                                                    output_file_name=output_file_name)

    @staticmethod
    def get_trajectories(model_address: str):
        model = rq.Model(model_address)
        well_uuids = model.uuids(obj_type='WellboreTrajectoryRepresentation')

        # Remove duplicates
        well_uuids = list(dict.fromkeys(well_uuids))

        wells = []

        for well_id in well_uuids:
            wells.append((rqw.well_name(well_id, model), str(well_id)))

        return wells

    @staticmethod
    def get_trajectory_units(model_address: str, well_id: str):
        model = rq.Model(model_address)
        root = model.root_for_uuid(well_id)
        trajectory = rqw.Trajectory(model, root)

        unit = trajectory.md_uom

        # Handle unusual unit formats that are really just  ft
        if unit.__contains__('ft'):
            unit = 'ft'

        return unit
