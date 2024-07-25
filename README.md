# PyAEDT Examples

This repository holds examples for PyAEDT.

## Guidelines for contribution

The following guidelines help ensure that the examples are consistent, easy to read and maintain:

- Use lower case with underscore for variables, functions and methods.
- Variable instances should use lower case with underscore.
  For example:
  ```
     m2d = pyaedt.Maxwell2d()
     m3d = pyaedt.Maxwell3d()
     hfss = pyaedt.Hfss() 
  ```
- Explicitly use the named arguments when calling methods or functions. For example:
  ```
     m3d.modeler.create_box(position=[7, 4, 22], 
                            dimensions_list=[10, 5, 30], 
                            name="Magnet", 
                            matname="copper")
  ```
- Keep the syntax in your example simple and easy to read. For example, the logic required for your example may already exist in ``pyaedt`` or other installed packages.
- Install [pre-commit](https://pre-commit.com/) to help identify simple issues before submitting your code for review.
  ```
     pre-commit run --all-files
  ```
- Use the ``tempfile`` module to create and clean up the folder where your example will read and write files:
  ```
     import tempfile
  ```
  Create a temporary folder at the beginning of the example:
  ```
     temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
  ```
  Remove the temporary folder at the end of the example:
  ```
     temp_dir.cleanup()
  ```
- The examples should be formatted, so they are compatible with jupytext using the [light format](https://jupytext.readthedocs.io/en/latest/formats-scripts.html#the-light-format) and can
be rendered and run in [Jupyter Lab](https://docs.jupyter.org/en/latest/) as Notebook files. Jupyter can be used to ensure correct rendering of markdown, images, and equations.
  ```
     pip install .[doc]
     jupyter lab
  ```
  Notebook files can be opened, edited and run from within Jupyter using _right click > Open With > Jupytext Notebook_.

## Example Template

You can refer to other examples or use the following 
[template](./examples/Template/Example_Template.py)
to create a new example. This code will be rendered
as a Jupyter Notebook if you open it using the jupytext plugin.

``` python
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

# ## Perform required imports
#
# Perform required imports.

import os
import tempfile
import pyaedt
import time

# Set constant values

AEDT_VERSION = "2024.1"
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory

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

```
