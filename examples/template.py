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
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in this example removes the temporary folder and
# > all contents. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch application
#
# The syntax for different applications in AEDT differ
# only in the name of the class that instantiates the 
# application. For example ``Maxwell3d``, ``Hfss`` or ``Icepak``.

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

# ## Set up model
#
# Description of preprocessing task.
# Add as many sections as needed for preprocessing tasks.
#
# Subsequent steps in the model creation process should be labled with a
# H3 title.
# ### This is a H3 title
#
# Markdown syntax:
# ``` markdown
# ### This is a H3 title
# ```


# ## Run the analysis
#
# The analysis is generally run with a single call that launches the solve
# process:
# ``` python
# app.analyze_setup()
# ```

# ## Postprocessing
#
# Description of postprocessing task.
# Add subsections with H3 titles as needed to 
# describe postprocessing steps such as
# visualizing or analyzing simulation results.


# ### Save project

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
