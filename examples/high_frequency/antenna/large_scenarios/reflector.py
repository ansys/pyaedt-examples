# # Reflector
#
# This example shows how to use PyAEDT to create an HFSS SBR+ project from an
# HFSS antenna and run a simulation.
#
# Keywords: **HFSS**,  **SBR+**, **reflector**.

# ## Perform imports and define constants
#
# Perform required imports and set up the local path to the path for the PyAEDT
# directory.

# +
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_sbr

# -

# Define constants.

AEDT_VERSION = "2025.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download project

project_full_name = download_sbr(local_path=temp_folder.name)

# ## Define designs
#
# Define two designs, one source and one target, with each design connected to
# a different object.

# +
target = ansys.aedt.core.Hfss(
    project=project_full_name,
    design="Cassegrain_",
    solution_type="SBR+",
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
)

source = ansys.aedt.core.Hfss(
    project=target.project_name,
    design="feeder",
    version=AEDT_VERSION,
)
# -

# ## Define linked antenna
#
# Define a linked antenna. This is HFSS far field applied to HFSS SBR+.

target.create_sbr_linked_antenna(source, target_cs="feederPosition", field_type="farfield")

# ## Assign boundaries
#
# Assign boundaries.

target.assign_perfecte_to_sheets(["Reflector", "Subreflector"])
target.mesh.assign_curvilinear_elements(["Reflector", "Subreflector"])

# ## Create setup and solve
#
# Create a setup and solve it.

setup1 = target.create_setup()
setup1.props["RadiationSetup"] = "ATK_3D"
setup1.props["ComputeFarFields"] = True
setup1.props["RayDensityPerWavelength"] = 2
setup1.props["MaxNumberOfBounces"] = 3
setup1["RangeType"] = "SinglePoints"
setup1["RangeStart"] = "10GHz"
target.analyze(cores=NUM_CORES)

# ## Postprocess
#
# Plot results in AEDT.

variations = target.available_variations.get_independent_nominal_values()
variations["Freq"] = ["10GHz"]
variations["Theta"] = ["All"]
variations["Phi"] = ["All"]
target.post.create_report(
    "db(GainTotal)",
    target.nominal_adaptive,
    variations=variations,
    primary_sweep_variable="Theta",
    context="ATK_3D",
    report_category="Far Fields",
)

# Plot results using Matplotlib.

solution = target.post.get_solution_data(
    "GainTotal",
    target.nominal_adaptive,
    variations=variations,
    primary_sweep_variable="Theta",
    context="ATK_3D",
    report_category="Far Fields",
)
solution.plot()

# ## Release AEDT
#
# Release AEDT and close the example.

target.save_project()
target.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``. If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
