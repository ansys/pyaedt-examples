# Copyright (C) 2024 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# # Short, Descriptive Title
#
# (do not specify the solver type in the title, i.e.: Maxwell2D, Maxwell3D etc)
#
# Most examples can be described as a series of steps that comprise a workflow.
# 1. Import packages and instantiate the application.
# 2. Do something useful and interesting like creating the model, assign materials and boundary conditions, etc.
# 3. Run one or more analyses.
# 4. View the results.
#
# Keywords: **Template**, **Jupyter**

# ## Prerequisites
#
# ### Perform imports

# +
import tempfile
import time

import ansys.aedt.core  # Interface to Ansys Electronics Desktop
# -

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2026.1"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.


# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ### Launch application
#
# AEDT applications are accessed through Python classes.
# Each application has it's own class, for example:
# - ``Maxwell3d``
# - ``Hfss``
# - ``Maxwell2d``
# - ``Icepak``
# - ``Emit``
# - ``QExtractor``
#
# > **Note:** Some examples access multiple applications. When the first
# > application is
# > started, an AEDT _Project_ is created.
# > When a 2nd application instance for a different AEDT
# > application is created, the corresponding design
# > type will be inserted into the project.

project_name = os.path.join(temp_folder.name, "my_project.aedt")
m3d = ansys.aedt.core.Maxwell3d(
    project=project_name,
    design="my_design",
    solution_type="my_solver",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Model Preparation
#
# Description of steps used to create and prepare the model for simulation.
# Add as many sections as needed for preprocessing tasks. Use level 3 headers
# for subsequent headers in this section.

# ### Create 3D model
#
# > Insert code to build the model from scratch or import a model.
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

# ## Postprocess
#
# After generating results demonstrate how to visualize and evaluate results
# in this section.
# Level 3 headers can be used to identify various post-processing
# steps.
#
# ### Evaluate loss
# > For example, in this section you may use code to demonstrate how to evaluate loss.
#
# ### Visualize fields
# > PyAEDT provides access to field solution data via the


# ## Finish
#
# ### Save the project

m3d.save_project()
m3d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
