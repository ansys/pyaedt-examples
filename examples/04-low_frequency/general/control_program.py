# # Control program enablement

# This example shows how to use PyAEDT to enable a control program in a Maxwell 2D project.
# It shows how to create the geometry, load material properties from an Excel file, and
# set up the mesh settings. Moreover, it focuses on postprocessing operations, in particular how to
# plot field line traces, which are relevant for an electrostatic analysis.
#
# Keywords: **Maxwell 2D**, **control program**.

# ## Perform imports and define constants
#
# Perform required imports.

import tempfile
import time

from ansys.aedt.core import Maxwell2d, downloads

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

# ## Download project file
#
# The files required to run this example are downloaded to the temporary working folder.

aedt_file = downloads.download_file(
    source="maxwell_ctrl_prg",
    name="ControlProgramDemo.aedt",
    destination=temp_folder.name,
)
ctrl_prg_file = downloads.download_file(
    source="maxwell_ctrl_prg", name="timestep_only.py", destination=temp_folder.name
)

# ## Launch Maxwell 2D
#
# Create an instance of the ``Maxwell2d`` class named ``m2d``.

m2d = Maxwell2d(
    project=aedt_file,
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
)

# ## Set active design

m2d.set_active_design("1 time step control")

# ## Get setup
#
# Get the simulation setup for this design so that the control program can be enabled.

setup = m2d.setups[0]

# ## Enable control program
#
# Enable the control program by giving the path to the file.

setup.enable_control_program(control_program_path=ctrl_prg_file)

# ## Analyze setup
#
# Run the analysis.

m2d.save_project()
m2d.analyze(setup=setup.name, cores=NUM_CORES, use_auto_settings=False)

# ## Plot results
#
# Display the simulation results.

sols = m2d.post.get_solution_data(
    expressions="FluxLinkage(Winding1)",
    variations={"Time": ["All"]},
    primary_sweep_variable="Time",
)
sols.plot()

# ## Release AEDT

m2d.save_project()
m2d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
