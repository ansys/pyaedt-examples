# # Component antenna array

# This example shows how to use PyAEDT to create an example using a 3D component file. It sets
# up the analysis, solves it, and uses postprocessing functions to create plots using Matplotlib and
# PyVista without opening the HFSS user interface. This example runs only on Windows using CPython.
#
# Keywords: **HFSS**, **antenna array**, **3D components**, **far field**.

# ## Perform imports and define constants
#
# Perform required imports.

import os
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.visualization.advanced.farfield_visualization import \
    FfdSolutionData

# Define constants

AEDT_VERSION = "2025.1"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download 3D component
# Download the 3D component that is needed to run the example.

example_path = ansys.aedt.core.downloads.download_3dcomponent(
    destination=temp_folder.name
)

# ## Launch HFSS and open project
#
# Launch HFSS and open the project.

# +
project_name = os.path.join(temp_folder.name, "array.aedt")
hfss = ansys.aedt.core.Hfss(
    project=project_name,
    version=AEDT_VERSION,
    design="Array_Simple",
    non_graphical=NG_MODE,
    new_desktop=True,
)

print("Project name " + project_name)
# -

# ## Read array definition
#
# Read array definition from the JSON file.

dict_in = ansys.aedt.core.general_methods.read_json(
    os.path.join(example_path, "array_simple.json")
)

# ## Define 3D component
#
# Define the 3D component cell.

dict_in["Circ_Patch_5GHz1"] = os.path.join(example_path, "Circ_Patch_5GHz.a3dcomp")

# ## Add 3D component array
#
# A 3D component array is created from the previous dictionary.
# If a 3D component is not available in the design, it is loaded
# into the dictionary from the path that you specify. The following
# code edits the dictionary to point to the location of the A3DCOMP file.

array = hfss.add_3d_component_array_from_json(dict_in)

# ## Modify cells
#
# Make the center element passive and rotate the corner elements.

array.cells[1][1].is_active = False
array.cells[0][0].rotation = 90
array.cells[0][2].rotation = 90
array.cells[2][0].rotation = 90
array.cells[2][2].rotation = 90

# ## Set up simulation and analyze
#
# Set up a simulation and analyze it.

setup = hfss.create_setup()
setup.props["Frequency"] = "5GHz"
setup.props["MaximumPasses"] = 3
hfss.analyze(cores=NUM_CORES)


# ## Get far field data
#
# Get far field data. After the simulation completes, the far
# field data is generated port by port and stored in a data class.

ffdata = hfss.get_antenna_data(setup=hfss.nominal_adaptive, sphere="Infinite Sphere1")

# ## Generate contour plot
#
# Generate a contour plot. You can define the Theta scan and Phi scan.

ffdata.farfield_data.plot_contour(
    quantity="RealizedGain",
    title="Contour at {}Hz".format(ffdata.farfield_data.frequency),
)

# ## Release AEDT
#
# Release AEDT.
# You can perform far field postprocessing without AEDT because the data is stored.

metadata_file = ffdata.metadata_file
working_directory = hfss.working_directory

hfss.save_project()
hfss.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Load far field data
#
# Load the stored far field data.

ffdata = FfdSolutionData(input_file=metadata_file)

# ## Generate contour plot
#
# Generate a contour plot. You can define the Theta scan
# and Phi scan.

ffdata.plot_contour(
    quantity="RealizedGain", title="Contour at {}Hz".format(ffdata.frequency)
)

# ## Generate 2D cutout plots
#
# Generate 2D cutout plots. You can define the Theta scan
# and Phi scan.

ffdata.plot_cut(
    quantity="RealizedGain",
    primary_sweep="theta",
    secondary_sweep_value=[-180, -75, 75],
    title="Azimuth at {}Hz".format(ffdata.frequency),
    quantity_format="dB10",
)

ffdata.plot_cut(
    quantity="RealizedGain",
    primary_sweep="phi",
    secondary_sweep_value=30,
    title="Elevation",
    quantity_format="dB10",
)

# ## Generate 3D plot
#
# Generate 3D plots. You can define the Theta scan and Phi scan.

ffdata.plot_3d(
    quantity="RealizedGain",
    output_file=os.path.join(working_directory, "Image.jpg"),
    show=False,
)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
