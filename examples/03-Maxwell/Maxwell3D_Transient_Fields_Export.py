# # Maxwell 3D: fields export in transient

# This example uses PyAEDT to export J field values for selected time steps in Maxwell 3D transient solver.
# Keywords: time steps, field export

# ## Perform required imports
#
# Perform required imports.

from pyaedt import Maxwell3d

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

# ## Initialize and launch Maxwell 2D
#
# Initialize and launch Maxwell 2D, providing the version, path to the project, the design
# name and type.

m3d = Maxwell3d(
    version=AEDT_VERSION,
    non_graphical=NG_MODE
)

# ## Create setup and validate
#
# Create the setup and validate it.

setup = m3d.create_setup(name="Setup1")
setup.props["StopTime"] = "0.02s"
setup.props["TimeStep"] = "0.002s"
setup.props["SaveFieldsType"] = "Every N Steps"
setup.props["N Steps"] = "2"
setup.props["Steps From"] = "0s"
setup.props["Steps To"] = "0.02s"
setup.update()

# ## Analyze and save project
#
# Analyze and save the project.

m3d.analyze_setup(name=setup.name)
m3d.save_project()

# ## Create field expression to evaluate J field
#
# Create a field expression to evaluate J field for a certain object

fields = m3d.ofieldsreporter
fields.CalcStack("clear")
fields.EnterQty("J")
fields.EnterVol("Coil_A2")
fields.CalcOp("Value")


# J is not scalar so you can not add as a named expression!
# J can only be exported: fields.CalculatorWrite()


# ## Release AEDT and clean up temporary directory
#
# Release AEDT and remove both the project and temporary directory.

m3d.release_desktop()
temp_folder.cleanup()

