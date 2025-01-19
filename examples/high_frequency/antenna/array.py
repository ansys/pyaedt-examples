# # Component antenna array

# This example shows how to create an antenna array using 3D components for the unit
# cell definition. You will see how to set
# up the analysis, generates the EM solution, and post-process the solution data
# using Matplotlib and
# PyVista. This example runs only on Windows using CPython.
#
# Keywords: **HFSS**, **antenna array**, **3D components**, **far field**.

# ## Prerequisites
#
# ### Perform imports

# +
import os
import tempfile
import time

from ansys.aedt.core import Hfss
from ansys.aedt.core.visualization.advanced.farfield_visualization import \
    FfdSolutionData
from ansys.aedt.core.downloads import download_3dcomponent
from ansys.aedt.core import general_methods
# -

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.
#

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ### Download 3D component
# Download the 3D component that will be used to define
# the unit cell in the antenna array.

path_to_3dcomp = download_3dcomponent(destination=temp_folder.name)

# ### Launch HFSS
#
# The following cell creates a new ``Hfss`` object. Electronics desktop is launched and
# a new HFSS design is inserted into the project.

# +
project_name = os.path.join(temp_folder.name, "array.aedt")
hfss = Hfss(
    project=project_name,
    version=AEDT_VERSION,
    design="Array_Simple",
    non_graphical=NG_MODE,
    new_desktop=False,  # Set to `False` to connect to an existing AEDT session.
)

print("Project name " + project_name)
# -

# ### Read array definition
#
# Read array definition from the JSON file.

array_definition = general_methods.read_json(
    os.path.join(path_to_3dcomp, "array_simple.json")
)

# ### Add the 3D component definition
#
# The JSON file links the unit cell to the 3D component
# named "Circ_Patch_5GHz1".
# This can be seen by examining ``array_definition["cells"]``. The following
# code prints the row and column indices of the array elements along with the name
# of the 3D component for each element.
#
# > **Note:** The ``array_definition["cells"]`` is of type ``dict`` and the key
# > values use the row, column indices in a string. For example: ``"(1,2)"`` for
# > the cell in the first row and the 2nd column.

print("Element\t\tName")
print("--------\t-------------")
for cell in array_definition["cells"]:
    cell_name = array_definition["cells"][cell]["name"]
    print(f"{cell}\t\t'{cell_name}'.")

# Each unit cell is defined by a 3D Component. The 3D component may be added
# to the HFSS design using the method
# [``Hfss.modeler.insert_3d_component()``]
# (https://aedt.docs.pyansys.com/version/stable/API/_autosummary/ansys.aedt.core.modeler.modeler_3d.Modeler3D.insert_3d_component.html)
# or it can be added as a key to the ``array_definition`` as shown below.

array_definition["Circ_Patch_5GHz1"] = os.path.join(path_to_3dcomp, "Circ_Patch_5GHz.a3dcomp")

# Note that the 3D component name is identical to the value for each element
# in the ``"cells"`` dictionary. For example,
# ``array_definition["cells"][0][0]["name"]

# ### Create the 3D component array in HFSS
#
# The array is now generated in HFSS from the information in
# ``array_definition``.
# If a 3D component is not available in the design, it is loaded
# into the dictionary from the path that you specify. The following
# code edits the dictionary to point to the location of the ``*.a3dcomp`` file.

array = hfss.add_3d_component_array_from_json(array_definition, name="circ_patch_array")

# ### Modify cells
#
# Make the center element passive and rotate the corner elements.

array.cells[1][1].is_active = False
array.cells[0][0].rotation = 90
array.cells[0][2].rotation = 90
array.cells[2][0].rotation = 90
array.cells[2][2].rotation = 90

# ### Set up simulation and run analysis
#
# Set up a simulation and analyze it.

setup = hfss.create_setup()
setup.props["Frequency"] = "5GHz"
setup.props["MaximumPasses"] = 3
hfss.analyze(cores=NUM_CORES)


# ## Postprocess
#
# ### Retrieve far-field data
#
# Get far-field data. After the simulation completes, the far
# field data is generated port by port and stored in a data class.

ffdata = hfss.get_antenna_data(setup=hfss.nominal_adaptive, sphere="Infinite Sphere1")

# ### Generate contour plot
#
# Generate a contour plot. You can define the Theta scan and Phi scan.

ffdata.farfield_data.plot_contour(
    quantity="RealizedGain",
    title=f"Contour at {ffdata.farfield_data.frequency * 1E-9:0.1f} GHz"
)

# ### Save the project and data
#
# Farfield data can be accessed from disk after the solution has been generated
# using the ``metadata_file`` property of ``ffdata``.

# +
metadata_file = ffdata.metadata_file
working_directory = hfss.working_directory

hfss.save_project()
hfss.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)
# -

# ### Load far field data
#
# The ``FfdSolutionData`` method can be instantiated from the metadata file. Embedded element
# patters are linked through the metadata file.

ffdata = FfdSolutionData(input_file=metadata_file)

# ## Generate contour plot
#
# Generate a contour plot. You can define the Theta scan
# and Phi scan.

ffdata.plot_contour(
    quantity="RealizedGain", title=f"Contour at {ffdata.frequency*1e-9:.1f}GHz"
)

# ### Generate 2D cutout plots
#
# Generate 2D cutout plots. You can define the Theta scan
# and Phi scan.

# +
ffdata.plot_cut(
    quantity="RealizedGain",
    primary_sweep="theta",
    secondary_sweep_value=[-180, -75, 75],
    title=f"Azimuth at {ffdata.frequency*1E-9:.1f}GHz",
    quantity_format="dB10",
)

ffdata.plot_cut(
    quantity="RealizedGain",
    primary_sweep="phi",
    secondary_sweep_value=30,
    title="Elevation",
    quantity_format="dB10",
)
# -

# ### Generate 3D plot
#
# Generate 3D plots. You can define the Theta scan and Phi scan.

ffdata.plot_3d(
    quantity="RealizedGain",
    output_file=os.path.join(working_directory, "Image.jpg"),
    show=False,
)

# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
