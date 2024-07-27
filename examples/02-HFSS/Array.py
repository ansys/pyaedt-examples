# # HFSS: component antenna array

# This example shows how you can use PyAEDT to create an example using a 3D component file. It sets
# up
# the analysis, solves it, and uses postprocessing functions to create plots using Matplotlib and
# PyVista without opening the HFSS user interface. This example runs only on Windows using CPython.
#
# Keywords: **HFSS**, **antenna array**, **far field**.


# ## Preparation
# Import the required packages

import os
import tempfile
import time

import pyaedt
from pyaedt.modules.solutions import FfdSolutionData

# Define constants.

AEDT_VERSION = "2024.1"
NUM_CORES = 4
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download 3D component
# Download the 3D component that is needed to run the example.

example_path = pyaedt.downloads.download_3dcomponent(destination=temp_dir.name)

# ## Launch HFSS and open project
#
# Launch HFSS and open the project.

# +
project_name = os.path.join(temp_dir.name, "array.aedt")
hfss = pyaedt.Hfss(
    project=project_name,
    version=AEDT_VERSION,
    design="Array_Simple",
    non_graphical=NG_MODE,
    new_desktop=True,
)

print("Project name " + project_name)
# -

# ## Read array definition from JSON file
#
# Read JSON file.

dict_in = pyaedt.general_methods.read_json(
    os.path.join(example_path, "array_simple.json")
)

# ## 3D Component definition
#
# Define 3DComponent cell.

dict_in["Circ_Patch_5GHz1"] = os.path.join(example_path, "Circ_Patch_5GHz.a3dcomp")

# ## Add 3D Component Array
#
# Created 3D Component array from the previous dictionary.
# If a 3D component is not available in the design, it is loaded
# into the dictionary from the path that you specify. The following
# code edits the dictionary to point to the location of the A3DCOMP file.

array = hfss.add_3d_component_array_from_json(dict_in)

# ## Modify cells
#
# Make center element passive and rotate corner elements.

array.cells[1][1].is_active = False
array.cells[0][0].rotation = 90
array.cells[0][2].rotation = 90
array.cells[2][0].rotation = 90
array.cells[2][2].rotation = 90

# ## Set up simulation
#
# Set up a simulation and analyze it.

setup = hfss.create_setup()
setup.props["Frequency"] = "5GHz"
setup.props["MaximumPasses"] = 3
hfss.analyze(num_cores=NUM_CORES)


# ## Get far field data
#
# Get far field data. After the simulation completes, the far
# field data is generated port by port and stored in a data class.

ffdata = hfss.get_antenna_ffd_solution_data(
    sphere_name="Infinite Sphere1", setup_name=hfss.nominal_adaptive, frequencies=[5e9]
)

# ## Generate contour plot
#
# Generate a contour plot. You can define the Theta scan and Phi scan.

ffdata.plot_farfield_contour(
    farfield_quantity="RealizedGain", title="Contour at {}Hz".format(ffdata.frequency)
)

# ## Release AEDT
#
# Release AEDT.
# Far field post-processing can be performed without AEDT because the data is stored.

eep_file = ffdata.eep_files
frequencies = ffdata.frequencies
working_directory = hfss.working_directory
hfss.save_project()
hfss.release_desktop()
time.sleep(
    3
)  # Allow Electronics Desktop to shut down before cleaning the temporary project folder.

# ## Load far field data
#
# Load far field data stored.

ffdata = FfdSolutionData(frequencies=frequencies[0], eep_files=eep_file[0])

# ## Generate contour plot
#
# Generate a contour plot. You can define the Theta scan
# and Phi scan.

ffdata.plot_farfield_contour(
    farfield_quantity="RealizedGain", title="Contour at {}Hz".format(ffdata.frequency)
)

# ## Generate 2D cutout plots
#
# Generate 2D cutout plots. You can define the Theta scan
# and Phi scan.

ffdata.plot_2d_cut(
    primary_sweep="theta",
    secondary_sweep_value=[-180, -75, 75],
    farfield_quantity="RealizedGain",
    title="Azimuth at {}Hz".format(ffdata.frequency),
    quantity_format="dB10",
)

ffdata.plot_2d_cut(
    primary_sweep="phi",
    secondary_sweep_value=30,
    farfield_quantity="RealizedGain",
    title="Elevation",
    quantity_format="dB10",
)

# ## Generate 3D polar plots in Matplotlib
#
# Generate 3D polar plots in Matplotlib. You can define
# the Theta scan and Phi scan.

ffdata.polar_plot_3d(farfield_quantity="RealizedGain")

# ## Cleanup
#
# All project files are saved in the folder ``temp_dir.name``.
# If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_dir.cleanup()
