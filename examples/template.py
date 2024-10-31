# # Short, Descriptive Title 
#
# (do not specify the solver type in the title, i.e.: Maxwell2D, Maxwell3D etc)
#
# ## Description:
#
# Most examples can be described as a series of steps that comprise a workflow.
# 1. Import packages and instantiate the application.
# 2. Do something useful and interesting like creating the geometric model, assing materials and boundary conditions, etc.
# 3. Run one or more analyses.
# 4. View the results.
#
# Keywords: **Template**, **Jupyter**

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

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.


# ## Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch application
#
# The syntax for different applications in AEDT differs
# only in the name of the class. This example demonstrates the use of the
# ``Maxwell3d`` class.
#
# > **Note:** Some examples use multiple solver types. When the first solver is
# > instantiated, an AEDT _Project_ is created. In this case, it is the instance of
# > ``Maxwell3d``. When another instance of is created, for example an instance of
# > the ``Icepak`` class, an Icepak design will be inserted into the project.

project_name = os.path.join(temp_folder.name, "my_project.aedt")
m3d = ansys.aedt.core.Maxwell3d(
    project=project_name,
    design="my_design",
    solution_type="my_solver",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ### Units
#
# The default units are "mm". Model units can be queried or changed using the
# property ``m3d.modeler.model_units``.

m3d.modeler.model_units = "mm"
print(f'Model units are "{m3d.modeler.model_units}"')

# ## Model Preparation
#
# Description of steps used to create and prepare the model for simulation.
# Add as many sections as needed for preprocessing tasks. Use level 3 headers
# for subsequent headers in this section.
#
# ### Create 3D model
#
# > Insert code to generate a 3D model or import a model.
#
# ### Assign boundary conditions
#
# > Insert code to assign boundaries here.
#
# ### Define solution setup
#
# > Insert code to specify solver settings here.
#
# ### Run analysis
#
# > Run the simulation.

m3d.analyze_setup("Setup1")

#
# ## Postprocess
#
# Description of postprocessing task.
# Add as many sections as needed for postprocessing tasks. Again use
# level 3 headers: `### Level 3 header`.


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
