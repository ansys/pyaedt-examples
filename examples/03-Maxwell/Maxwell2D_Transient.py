# # Maxwell 2D: transient winding analysis
#
# This example shows how you can use PyAEDT to create a project in Maxwell 2D
# and run a transient simulation. It runs only on Windows using CPython.
#
# The following libraries are required for the advanced postprocessing features
# used in this example:
#
# - [Matplotlib](https://pypi.org/project/matplotlib/)
# - [Numpy](https://pypi.org/project/numpy/)
# - [PyVista](https://pypi.org/project/pyvista/)
#
# Install these libraries with:
#
# ```console
#   pip install numpy pyvista matplotlib
# ```

# ## Perform required imports
#
# Perform required imports.

import os
import tempfile
import time

import pyaedt

# ## Define constants

AEDT_VERSION = "2024.1"
NG_MODE = False

# ## Create temporary directory and download files
#
# Create a temporary directory where we store downloaded data or
# dumped data.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Insert Maxwell 2D design
#
# Insert a Maxwell 2D design.

m2d = pyaedt.Maxwell2d(
    solution_type="TransientXY",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
    project=pyaedt.generate_unique_project_name(),
)

# ## Create rectangle and duplicate it
#
# Create a rectangle and duplicate it.

rect1 = m2d.modeler.create_rectangle(
    origin=[0, 0, 0], sizes=[10, 20], name="winding", matname="copper"
)
duplicate = rect1.duplicate_along_line(vector=[14, 0, 0])
rect2 = m2d.modeler[duplicate[0]]

# ## Create air region
#
# Create an air region.

region = m2d.modeler.create_region([100, 100, 100, 100])

# ## Assign windings and balloon
#
# Assigns windings to the sheets and a balloon to the air region.

m2d.assign_winding(assignment=[rect1.name, rect2.name], name="PHA")
m2d.assign_balloon(assignment=region.edges)

# ## Plot model
#
# Plot the model.

m2d.plot(
    show=False,
    output_file=os.path.join(temp_folder.name, "Image.jpg"),
    plot_air_objects=True,
)

# ## Create setup
#
# Create the transient setup.

setup = m2d.create_setup()
setup.props["StopTime"] = "0.02s"
setup.props["TimeStep"] = "0.0002s"
setup.props["SaveFieldsType"] = "Every N Steps"
setup.props["N Steps"] = "1"
setup.props["Steps From"] = "0s"
setup.props["Steps To"] = "0.002s"

# ## Create rectangular plot
#
# Create a rectangular plot.

m2d.post.create_report(
    expressions="InputCurrent(PHA)",
    domain="Time",
    primary_sweep_variable="Time",
    plot_name="Winding Plot 1",
)

# ## Solve model
#
# Solve the model.

m2d.analyze(use_auto_settings=False)

# ## Create output and plot using PyVista
#
# Create the output and plot it using PyVista.

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
gif.animate()
# -

# ## Generate plot outside of AEDT
#
# Generate the same plot outside AEDT.

solutions = m2d.post.get_solution_data(
    expressions="InputCurrent(PHA)", primary_sweep_variable="Time"
)
solutions.plot()

# ## Release AEDT and clean up temporary directory
#
# Release AEDT and remove both the project and temporary directory.

m2d.release_desktop()

time.sleep(3)
temp_folder.cleanup()
