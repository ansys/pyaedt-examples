# # Short, Descriptive Title (do not specify the application name here, i.e.: Maxwell2D, Maxwell3D etc)
#
# Description:
#
# Most examples can be described as a series of steps that comprise a workflow.
# 1. Import packages and instantiate the application.
# 2. Do something useful and interesting.
# 3. View the results.
#
# Keywords: **Template**, **Jupyter**

# ## Perform imports and define constants
#
# Perform required imports.

import os
import tempfile
import time

import ansys.aedt.core

# Define constants.

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT and application
#
# Create an instance of the application (such as ``Maxwell3d`` or``Hfss``)
# with a class (such as ``m3d`` or``hfss``) by providing
# the project and design names, the solver, and the version.

project_name = os.path.join(temp_folder.name, "my_project.aedt")
m3d = ansys.aedt.core.Maxwell3d(
    project=project_name,
    design="my_design",
    solution_type="my_solver",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)
m3d.modeler.model_units = "mm"

# ## Preprocess
#
# Description of preprocessing task.
# Add as many sections as needed for preprocessing tasks.


# ## Postprocess
#
# Description of postprocessing task.
# Add as many sections as needed for postprocessing tasks.


# ## Release AEDT

m3d.save_project()
m3d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
