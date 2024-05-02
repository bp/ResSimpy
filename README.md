# ResSimpy: Python API for working with Reservoir Simulator models

[![License](https://img.shields.io/pypi/l/ressimpy)](https://github.com/bp/ResSimpy/blob/master/LICENSE.MD)
[![Documentation Status](https://readthedocs.org/projects/ressimpy/badge/?version=latest)](https://ResSimpy.readthedocs.io/en/latest/?badge=latest)
[![Python CI](https://github.com/bp/ResSimpy/actions/workflows/ci-tests.yml/badge.svg)](https://github.com/bp/ResSimpy/actions/workflows/ci-tests.yml)
![Python version](https://img.shields.io/pypi/pyversions/ResSimpy)
[![PyPI](https://img.shields.io/pypi/v/ResSimpy)](https://badge.fury.io/py/ResSimpy)
![Status](https://img.shields.io/pypi/status/ResSimpy)
[![codecov](https://codecov.io/gh/bp/ResSimpy/branch/master/graph/badge.svg)](https://codecov.io/gh/bp/ResSimpy)

## Introduction
**ResSimpy** is a Python API for automating reservoir simulation workflows, allowing the user to read, manipulate and 
write reservoir simulation input decks. Whilst it was created by staff at BP, we welcome contributions from anybody 
interested, whether it is by raising pull requests, or simply suggesting features / raising bugs in the [GitHub issues](https://github.com/bp/ResSimpy/issues).

### Documentation

See the complete package documentation on
[readthedocs](https://ResSimpy.readthedocs.io/).

## Installation

ResSimpy can be installed with pip:

```bash
pip install ressimpy
```

## Contributing

Please see [Contributing Guide](docs/CONTRIBUTING.rst) for instructions on how to set up a dev environment and contribute
code to the project.

## Getting Started
The following Python code examples demonstrate how to perform some simple operations on a model using ResSimpy:

### Step 1: Import the library
```python
from ResSimpy import NexusSimulator as Simulator
```

###  Step 2: Initialise the model
```python
nexus_fcs_file = '/path/to/fcsfile.fcs'
model = Simulator(origin=nexus_fcs_file) # Create the 'Simulator' model object
```

#### Once these steps are completed, you are able to perform any supported operations on the model. The following code snippets are examples of a few such operations:

### Writing Out Files
```python
# Update the files in the model that have been modified.
# IMPORTANT: no changes made to the model, such as adding completions or removing constraints will be applied to the model files until this function is called.
model.update_simulator_files()

# Create a copy of the entire model
model.write_out_new_simulator(new_file_path='/new/path/to/fcsfile.fcs', new_include_file_location='/new/path/to/includes_directory/')
```

### Wells - Get wells overview
```python
wells_info = model.wells.get_wells_overview() # Returns a list of wells with their information. Can be print()ed
print(wells_info)
```

### Wells - Get information about an individual Well 
```python
well = model.wells.get(well_name='well_1') # Retrieves the named well as a NexusWell object

# You can then access the various properties for that well (such as perforations, shutins, completion events etc) using (for example)
perforations = well.perforations

# You can pretty print the information about a well using
print(well.printable_well_info)

# Get the wells information in dataframe format
wells_df = model.wells.get_df()
print(wells_df)
```

### Completions 
```python
# Adding a completion
new_completion = {'date': '01/02/2025', 'i': 4, 'j': 5, 'k': 6, 'well_radius': 7.50} # Create a dictionary containing the properties of the completion you wish to add
model.wells.add_completion(well_name='well_1', completion_properties=new_completion) # Add the new completion

# Removing a completion
completion_to_modify = {'date': '01/02/2025', 'i': 4, 'j': 5, 'k': 6, 'well_radius': 7.5} # Create a dictionary containing the properties of the existing completion
model.wells.remove_completion(well_name='well_1', completion_properties=completion_to_modify) # Remove the completion

# Modifying a completion
modified_properties = {'date': '10/03/2025'} # Create a dict with the properties you want to change and their new values
model.wells.modify_completion(well_name='well_1', properties_to_modify=modified_properties, completion_to_change=completion_to_modify) # Modify the completion
```

### Structured Grid -  Get a list of the array functions applied to the grid 
```python
func_list = model.grid.get_array_functions_list()
func_summary_df = model.grid.get_array_functions_df() # get a dataframe instead

[print(x) for x in func_list[0:9]] # Example showing how to print out the first 10 functions
```

### Networks - Get constraints
```python
constraints = model.network.constraints.get_all()
constraints_for_well = constraints['well_1'] # Get the constraints for the well well_1

# You can then access various properties related to the constraints, such as oil, water and gas rates using
oil_rate = constraints_for_well[0].max_surface_oil_rate
print(f"\nmax surface oil rate: {oil_rate}")

# Get a dataframe with all constraints in it.
constraint_df = model.network.constraints.get_df()
print(constraint_df)
```

### Networks -  Get dataframes of well connections, wellbores, network connections and nodes
```python
df_well_cons = model.network.connections.get_df()
df_well_bores = model.network.wellbores.get_df()
df_connections = model.network.connections.get_df()
df_nodes = model.network.nodes.get_df()
```

## Support
For most bugs or feature requests, we recommend using [GitHub issues](https://github.com/bp/ResSimpy/issues).
If, however, you have a query related to something else, or if your query relates to something confidential, please feel
free to email the team at ResSimpy@bp.com.