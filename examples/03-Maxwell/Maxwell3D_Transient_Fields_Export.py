# # Maxwell 3D: fields export in transient

# Keywords: time steps, field calculator

# ## Perform required imports
#
# Perform required imports.

import tempfile
import pyaedt

# ## Define constants

AEDT_VERSION = "2024.2"
NG_MODE = False

# ## Create temporary directory and download files
#
# Create a temporary directory where we store downloaded data or
# dumped data.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Import project
#
# Import of the project in the temporary directory

project_path = pyaedt.downloads.download_file(
    source="maxwell_transient_fields",
    name="M3D_Transient_StrandedWindings.aedtz",
    destination=temp_folder.name
)

# ## Initialize and launch Maxwell 2D
#
# Initialize and launch Maxwell 2D, providing the version, path to the project, the design
# name and type.

m3d = pyaedt.Maxwell3d(
    project=project_path,
    version=AEDT_VERSION,
    non_graphical=NG_MODE
)

# ## Create field expressions
#
# Create a field expression to evaluate J field normal to a surface
# Calculate the average value of the J field

fields = m3d.ofieldsreporter
fields.CalcStack("clear")
fields.EnterQty("J")
fields.EnterSurf("Coil_A2")
fields.CalcOp("Normal")
fields.CalcOp("Dot")
fields.AddNamedExpression("Jn", "Fields")

fields.CopyNamedExprToStack("Jn")
fields.EnterSurf("Coil_A2_ObjectFromFace1")
fields.CalcOp("Mean")
fields.AddNamedExpression("J_avg_A2", "Fields")

# ## Release AEDT and clean up temporary directory
#
# Release AEDT and remove both the project and temporary directory.

m3d.release_desktop()
temp_folder.cleanup()

