# # SBR+: Import Geometry from Maps
#
# This example shows how you can use PyAEDT to create an HFSS SBR+ project from an
# OpenStreeMaps.
#
# Keywords: **HFSS SBR+**, **City**.

# ## Perform required imports
#
# Perform required imports and set up the local path to the PyAEDT
# directory path.

import os
import tempfile
import pyaedt

# Set constant values

AEDT_VERSION = "2024.1"
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory

temp_dir = tempfile.TemporaryDirectory(suffix="_ansys")

# ## Launch HFSS and open project
#
# Launch HFSS and open the project.

project_name = os.path.join(temp_dir.name, "city.aedt")
app = pyaedt.Hfss(
    project=project_name,
    design="Ansys",
    solution_type="SBR+",
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
)

# ## Define Location to import
#
# Define latitude and longitude to import.

ansys_home = [40.273726, -80.168269]

# ## Generate map and import
#
# Assign boundaries.

app.modeler.import_from_openstreet_map(
    ansys_home, terrain_radius=250, road_step=3, plot_before_importing=False, import_in_aedt=True
)

# ## Plot model
#
# Plot the model.

plot_obj = app.plot(show=False, plot_air_objects=True)
plot_obj.background_color = [153, 203, 255]
plot_obj.zoom = 1.5
plot_obj.show_grid = False
plot_obj.show_axes = False
plot_obj.bounding_box = False
plot_obj.plot(os.path.join(app.working_directory, "Source.jpg"))

# ## Release AEDT
#
# Release AEDT and close the example.

app.release_desktop()

# ## Cleanup
#
# All project files are saved in the folder ``temp_dir.name``. If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_dir.cleanup()
