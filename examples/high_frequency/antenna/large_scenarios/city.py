# # Environment import from [open street map](https://www.openstreetmap.org/)
#
# This example shows how to use PyAEDT to create an HFSS SBR+ project from
# OpenStreetMap.
#
# Keywords: **HFSS**,  **SBR+**, **city**, **OpenStreetMap**

# ## Prerequisites
#
# ### Perform imports

# +
import os
import tempfile
import time

import ansys.aedt.core
# -

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.1"
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ### Launch HFSS and open project
#
# Launch HFSS and open the project. The solution type
# [SBR+](https://www.ansys.com/blog/new-hfss-sbr-technology-in-ansys-2021-r2) instantiates a design type that supports the SBR+ solver.

project_name = os.path.join(temp_folder.name, "city.aedt")
app = ansys.aedt.core.Hfss(
    project=project_name,
    design="Ansys",
    solution_type="SBR+",
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
)

# ## Model Preparation
#
# ### Define the global location
#
# Define the latitude and longitude of the 
# [location](https://www.openstreetmap.org/#map=12/40.2740/-80.1680) 
# to import from OpenStreetMap.

ansys_home = [40.273726, -80.168269]

# ### Generate map and import
#
# Import the model and define the domain size. The radius that defines the domain is specified in meters.

app.modeler.import_from_openstreet_map(
    ansys_home,
    terrain_radius=250,
    road_step=3,
    plot_before_importing=True,
    import_in_aedt=True,
)

# ### Visualize the model
#
# Plot the model.

plot_obj = app.plot(show=False, plot_air_objects=True)
plot_obj.background_color = [153, 203, 255]
plot_obj.zoom = 1.5
plot_obj.show_grid = False
plot_obj.show_axes = False
plot_obj.bounding_box = False
plot_obj.plot(os.path.join(temp_folder.name, "Source.jpg"))

# ## Finish
#
# ### Save the project
# Release AEDT and close the example.

app.save_project()
app.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
