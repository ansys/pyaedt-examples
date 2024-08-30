# # Enabling Control Program

# This example shows how you can use PyAEDT to enable control program in a Maxwell 2D project.
# It shows how to create the geometry, load material properties from an Excel file and
# set up the mesh settings. Moreover, it focuses on post-processing operations, in particular how to
# plot field line traces, relevant for an electrostatic analysis.
#
# Keywords: **Maxwell 2D**, **control program**.

# ## Perform required imports
#
# Perform required imports.

import tempfile
import time

from ansys.aedt.core import Maxwell2d, downloads

# ## Define constants

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory
#
# The temporary directory is used to run the example and save simulation data.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download the project file
#
# The files required to run this example will be downloaded to the temporary working folder.

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
#
# Set the active design.

m2d.set_active_design("1 time step control")

# ## Retrieve the setup
#
# Get the simulation setup for this design so that the "control program" can be enabled.

setup = m2d.setups[0]

# ## Enable control program
#
# Enable control program by giving the path to the file.

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
# Wait 3 seconds to allow Electronics Desktop to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Cleanup
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
