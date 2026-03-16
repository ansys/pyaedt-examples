# # Component antenna array

# This example shows how to create an antenna array using 3D components for the unit
# cell definition. You will see how to set
# up the analysis, generate the EM solution, and plot the far-field
# using Matplotlib and
# PyVista. This example runs only on Windows using CPython.
#
# The 3x3 patch antenna array is shown below
#
# <img src="_static\array\array_in_hfss.png" width="600">
#
# The array is automatically built by defining the number of cells in each direction.
# The unit cell vectors are shown as red and blue arrows in the image above.

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
from ansys.aedt.core.examples.downloads import download_file
from ansys.aedt.core.generic import file_utils
from pathlib import Path
# -

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.2"
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
# Download the data used to define the antenna array. Data is retrieved from
# the [example-data repository](https://github.com/ansys/example-data/tree/main/pyaedt)
# on GitHub. The data 

path_to_3dcomp = download_file(source="array_3d_component", local_path=temp_folder.name)

# ## Model Preparation
# ### Launch HFSS
#
# The following cell creates a new ``Hfss`` object. Electronics desktop is launched and
# a new HFSS design is inserted into the project.

# +
project = Path(temp_folder.name) / "array.aedt"
hfss = Hfss(
    project=project,
    version=AEDT_VERSION,
    design="Array_Simple",
    non_graphical=NG_MODE,
    new_desktop=False,  # Set to `False` to connect to an existing AEDT session.
)

print("Project name " + project.name)
# -

# ### Read array definition
#
# Read array definition from the JSON file. The
# return type is a dictionary.

array_definition = file_utils.read_json(Path(path_to_3dcomp) / "array_simple_2by6.json")

# ### Add the 3D component definition
#
# The JSON file links the unit cell to the 3D component
# named ``"Circ_Patch_5GHz1"``.
# This can be seen by examining ``array_definition["cells"]``. The following
# code prints the row and column indices of the array elements along with the name
# of the 3D component for each element.
#
# > **Note:** The ``array_definition["cells"]`` is of type ``dict`` and the key
# > is a string built from the _(row, column)_ indices of the array element. For example:
# > the key for the element in the first row and 2nd column is ``"(1,2)"``.

print("Element\t\tName")
print("--------\t-------------")
for cell in array_definition["cells"]:
    cell_name = array_definition["cells"][cell]["name"]
    print(f"{cell}\t\t'{cell_name}'.")

# Each unit cell is defined by a 3D Component. The 3D component may be added
# to the HFSS design using the method
# [Hfss.modeler.insert_3d_component()](https://aedt.docs.pyansys.com/version/stable/API/_autosummary/ansys.aedt.core.modeler.modeler_3d.Modeler3D.insert_3d_component.html)
# or it can be added as a key to the ``array_definition`` as shown below.

array_definition["Circ_Patch_5GHz1"] = Path(path_to_3dcomp) / "Circ_Patch_5GHz.a3dcomp"

# Note that the 3D component name is identical to the value for each element
# in the ``"cells"`` dictionary. For example,
# ``array_definition["cells"][0][0]["name"]

# ### Create the 3D component array in HFSS
#
# The array is now generated in HFSS from the information in
# ``array_definition``.
# If a 3D component is not available in the design, it is loaded
# into the dictionary from the path that you specify. The following
# code edits the dictionary to point to the location of the ``A3DCOMP`` file.

array = hfss.create_3d_component_array(array_definition, name="circ_patch_array")

# ### Modify cells
#
# Make the center element passive and rotate the corner elements.

#  array.cells[1][1].is_active = False  # Demonstrate turning element on/off.
for nrow in range(2):
    for ncolumn in range(6):
        array.cells[nrow][ncolumn] = 90  # Rotate 90 degrees

# The changes to the array elements can be confirmed in the HFSS user
# interface. The center element is passive, and the corner elements are rotated
# 90 degrees.
#
# <img src="_static\array\array_elements.svg" width="600">
#

# ### Set up simulation and run analysis
#
# Set up a simulation and analyze it.

setup = hfss.create_setup()
setup.props["Frequency"] = "5GHz"
setup.props["MaximumPasses"] = 2
setup.analyze(cores=NUM_CORES)

# ## Postprocess
#
# ### Retrieve far-field data
#
# After the simulation completes, the far-field data can be retrieved as
# an instance of the
# ``FfdSolutionData`` class by calling the 
# ``get_antenna_data()`` method as shown below.
#
# The default resolution for $\theta$ and $\phi$ is 5 degrees. 
# If you want to change the scan range
# or resolution, create a far-field setup in HFSS and pass the setup name as an argument to 
# ``get_antenna_data()``.

far_field_setup = hfss.insert_infinite_sphere(
                    x_start=0,     # phi
                    x_stop=180, 
                    x_step=5, 
                    y_start=-180,  # theta
                    y_stop=180, y_step=1, 
                    name="FFSetup"
                )

ffdata = hfss.get_antenna_data(setup=hfss.nominal_adaptive, sphere=far_field_setup.name)

# ### Generate contour plot
#
# The 3d far-field plot can be created using the ``plot_contour()`` method. Setting
# ``max_theta=90`` restricts the plot to only the upper hemisphere. The pointing angel can 
# be modified using the ``phi`` and ``theta`` named arguments.

ffdata.farfield_data.plot_contour(
    quantity="RealizedGain", phi=0, theta=25,
    title=f"Contour at {ffdata.farfield_data.frequency * 1E-9:0.1f} GHz",
    max_theta=90
)

# ### Save the project and data
#
# Far-field data can be accessed from disk after the solution has been generated
# using ``ffdata.metadata_file``. Subsequent post-processing can 
# continue without using HFSS.

# +
metadata_file = ffdata.metadata_file
working_directory = hfss.working_directory

hfss.save_project()
hfss.desktop_class.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)
# -

# ### Load far field data
#
# An instance of the ``FfdSolutionData`` class
# can be instantiated from the metadata file. Embedded element
# patters are linked through the metadata file.

ffdata = FfdSolutionData(input_file=metadata_file)

# ## Generate contour plot
#
# Generate a contour plot. In this plot the ``theta_max`` is not set. The radial axis is $\theta$
# so the field intensity at the outer edge of the plot corresponds to backward radiation ($\theta=180 \degree$).

ffdata.plot_contour(
    quantity="RealizedGain", title=f"Contour at {ffdata.frequency * 1e-9:.1f} GHz",
    theta=30, phi=0
)

# ### Generate 2D cutout plots
#
# Generate 2D cutout plots. You can define the Theta scan
# and Phi scan.

# +
ffdata.plot_cut(
    quantity="RealizedGain",
    primary_sweep="theta",
    secondary_sweep_value=[ 180, 75],
    title=f"Azimuth at {ffdata.frequency * 1E-9:.1f} GHz",
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
# The following command creates a widget using PyVista that allows you to change the steering angle interactively. You will have to download the Jupyter Notebook for this example and make sure you have installed all dependencies. Enjoy exploring the ``FfdSolutionData`` class by downloading this example and running your own Jupyter Notebook.

ffdata.plot_3d(
    quantity="RealizedGain",
    output_file=os.path.join(working_directory, "Image.jpg"),
    show=False,
)

# ## Finish
#
# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
