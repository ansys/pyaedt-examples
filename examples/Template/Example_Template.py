# # PyAEDT Example Template
#
# This code can be used to create a new example
# for PyAEDT. Examples should demonstrate the use of
# PyAEDT to automate simple workflow steps.
#
# You may want to add keywords to your example. Comments
# in the notebook are rendered using Markdown.
#
# Keywords: **HFSS**, **flex cable**, **CPWG**.

# ## Set up project
#
# Perform required imports.

import os
import tempfile
import pyaedt
import time

# Set constant values

AEDT_VERSION = "2024.1"
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary folder
#
# Simulation data will be saved in the temporary folder. 
# If you run this example as a Jupyter Notebook,
# the results and project data can be retrieved before executing the
# final cell of the notebook.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch Application
#
# The syntax for different applications in AEDT differ
# only in the name of the class. In this template we use
# ``Hfss()``. Modify
# this text as needed for your example.

project_name = os.path.join(temp_dir.name, "example.aedt")
hfss = pyaedt.Hfss(
    project=project_name,
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
)

# ## Add code
#
# This is where you write the code for your example. Use Markdown
# to create header cells and add a description of what is done in each cell. 
# You can also
# add in-line comments if you feel a given command
# needs further clarification.

my_var = 4  # assign 4 to a variable.
print(my_var)

# ## Release AEDT
#
# At the end of the example, release the application. Use the following cells
# so the user of the example knows how to save the project data for 
# later use if needed.

hfss.save_project()
hfss.release_desktop()
time.sleep(3)  # Allow Elctronics Desktop to shut down before cleaning the temporary project folder.

# ## Cleanup
#
# All project files are saved in the folder ``temp_dir.name``. If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_dir.cleanup()
