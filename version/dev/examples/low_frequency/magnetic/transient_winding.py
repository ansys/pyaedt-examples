# # Transient winding analysis
#
# This example shows how to use PyAEDT to create a project in Maxwell 2D
# and run a transient simulation. It runs only on Windows using CPython.
#
# The following libraries are required for the advanced postprocessing features
# used in this example:
#
# - [Matplotlib](https://pypi.org/project/matplotlib/)
# - [Numpy](https://pypi.org/project/numpy/)
# - [PyVista](https://pypi.org/project/pyvista/)
#
# Install these libraries with this command:
#
# ```console
#   pip install numpy pyvista matplotlib
# ```
#
# Keywords: **Maxwell 2D**, **transient**, **winding**.

# ## Perform imports and define constants
#
# Perform required imports.

# +
import os
import tempfile
import time

import ansys.aedt.core

# -

# Define constants.

AEDT_VERSION = "2025.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.


# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Insert Maxwell 2D design

project_name = os.path.join(temp_folder.name, "Transient.aedt")
m2d = ansys.aedt.core.Maxwell2d(
    solution_type="TransientXY",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
    project=project_name,
)

# ## Create rectangle and duplicate it

rect1 = m2d.modeler.create_rectangle(origin=[0, 0, 0], sizes=[10, 20], name="winding", material="copper")
duplicate = rect1.duplicate_along_line(vector=[14, 0, 0])
rect2 = m2d.modeler[duplicate[0]]

# ## Create air region
#
# Create an air region.

region = m2d.modeler.create_region([100, 100, 100, 100])

# ## Assign windings and balloon
#
# Assigns windings to the sheets and a balloon to the air region.

m2d.assign_winding(assignment=[rect1.name, rect2.name], current="1*sin(2*pi*50*Time)", name="PHA")
m2d.assign_balloon(assignment=region.edges)

# ## Create transient setup

setup = m2d.create_setup()
setup.props["StopTime"] = "0.02s"
setup.props["TimeStep"] = "0.0002s"
setup.props["SaveFieldsType"] = "Every N Steps"
setup.props["N Steps"] = "1"
setup.props["Steps From"] = "0s"
setup.props["Steps To"] = "0.002s"

# ## Create rectangular plot

m2d.post.create_report(
    expressions="InputCurrent(PHA)",
    domain="Sweep",
    primary_sweep_variable="Time",
    plot_name="Winding Plot 1",
)

# ## Solve model

m2d.analyze(cores=NUM_CORES, use_auto_settings=False)

# ## Create output and plot using PyVista

# +
cutlist = ["Global:XY"]
face_lists = rect1.faces
face_lists += rect2.faces
timesteps = [str(i * 2e-4) + "s" for i in range(11)]
id_list = [f.id for f in face_lists]

gif = m2d.post.plot_animated_field(
    quantity="Mag_B",
    assignment=id_list,
    plot_type="Surface",
    intrinsics={"Time": "0s"},
    variation_variable="Time",
    variations=timesteps,
    show=False,
    export_gif=False,
)
gif.isometric_view = False
gif.camera_position = [15, 15, 80]
gif.focal_point = [15, 15, 0]
gif.roll_angle = 0
gif.elevation_angle = 0
gif.azimuth_angle = 0

# Set off_screen to False to visualize the animation.
# gif.off_screen = False
gif.animate(show=False)
# -

# ## Generate plot outside of AEDT
#
# Generate the same plot outside AEDT.

solutions = m2d.post.get_solution_data(expressions="InputCurrent(PHA)", primary_sweep_variable="Time", domain="Sweep")
solutions.plot()

# ## Release AEDT

m2d.save_project()
m2d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
