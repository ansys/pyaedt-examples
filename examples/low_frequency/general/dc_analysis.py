# # Electro DC analysis

# This example shows how to use PyAEDT to create a Maxwell DC analysis,
# compute mass center, and move coordinate systems.
#
# Keywords: **Maxwell 3D**, **DC**.

# ## Perform imports and define constants
#
# Perform required imports.

import os
import tempfile
import time

from ansys.aedt.core import Maxwell3d

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

# ## Launch AEDT
#
# Create an instance of the ``Maxwell3d`` class named ``m3d`` by providing
# the project name, the version, and the graphical mode.

project_name = os.path.join(temp_folder.name, "conductor_example.aedt")
m3d = Maxwell3d(
    project=project_name,
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
)

# ## Set up Maxwell solution
#
# Set up the Maxwell solution to DC.

m3d.solution_type = m3d.SOLUTIONS.Maxwell3d.ElectroDCConduction

# ## Create conductor
#
# Create a conductor using copper, a predefined material in the Maxwell material library.

conductor = m3d.modeler.create_box(
    origin=[7, 4, 22], sizes=[10, 5, 30], name="Conductor", material="copper"
)

# ## Create setup and assign voltage

m3d.assign_voltage(assignment=conductor.faces, amplitude=0)
m3d.create_setup()

# ## Solve setup

m3d.analyze(cores=NUM_CORES)

# ## Compute mass center
#
# Compute mass center using the fields calculator.

m3d.post.ofieldsreporter.EnterScalarFunc("X")
m3d.post.ofieldsreporter.EnterVol(conductor.name)
m3d.post.ofieldsreporter.CalcOp("Mean")
m3d.post.ofieldsreporter.AddNamedExpression("CM_X", "Fields")
m3d.post.ofieldsreporter.EnterScalarFunc("Y")
m3d.post.ofieldsreporter.EnterVol(conductor.name)
m3d.post.ofieldsreporter.CalcOp("Mean")
m3d.post.ofieldsreporter.AddNamedExpression("CM_Y", "Fields")
m3d.post.ofieldsreporter.EnterScalarFunc("Z")
m3d.post.ofieldsreporter.EnterVol(conductor.name)
m3d.post.ofieldsreporter.CalcOp("Mean")
m3d.post.ofieldsreporter.AddNamedExpression("CM_Z", "Fields")
m3d.post.ofieldsreporter.CalcStack("clear")

# ## Get mass center
#
# Get mass center using the fields calculator.

xval = m3d.post.get_scalar_field_value(quantity="CM_X")
yval = m3d.post.get_scalar_field_value(quantity="CM_Y")
zval = m3d.post.get_scalar_field_value(quantity="CM_Z")

# ## Create variables
#
# Create variables with mass center values.

m3d[conductor.name + "x"] = str(xval * 1e3) + "mm"
m3d[conductor.name + "y"] = str(yval * 1e3) + "mm"
m3d[conductor.name + "z"] = str(zval * 1e3) + "mm"

# ## Create coordinate system
#
# Create a parametric coordinate system.

cs1 = m3d.modeler.create_coordinate_system(
    origin=[conductor.name + "x", conductor.name + "y", conductor.name + "z"],
    reference_cs="Global",
    name=conductor.name + "CS",
)

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
