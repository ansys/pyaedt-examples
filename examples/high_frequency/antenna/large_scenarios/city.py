# # Geometry import from maps
#
# This example shows how to use PyAEDT to create an HFSS SBR+ project from
# OpenStreetMap.
#
# Keywords: **HFSS**,  **SBR+**, **city**.

# ## Perform imports and define constants
#
# Perform required imports and set up the local path to the PyAEDT
# directory path.

import os
import tempfile
import time

import ansys.aedt.core

# Define constants.

AEDT_VERSION = "2025.1"
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch HFSS and open project
#
# Launch HFSS and open the project.

project_name = os.path.join(temp_folder.name, "city.aedt")
app = ansys.aedt.core.Hfss(
    project=project_name,
    design="Ansys",
    solution_type="SBR+",
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
)

# ## Define location to import
#
# Define the latitude and longitude of the location to import.

ansys_home = [40.273726, -80.168269]

# ## Generate map and import
#
# Assign boundaries.

app.modeler.import_from_openstreet_map(
    ansys_home,
    terrain_radius=250,
    road_step=3,
    plot_before_importing=True,
    import_in_aedt=True,
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
plot_obj.plot(os.path.join(temp_folder.name, "Source.jpg"))

# ## Release AEDT
#
# Release AEDT and close the example.

app.save_project()
app.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``. If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
