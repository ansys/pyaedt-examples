# # Probe-fed patch antenna
#
# This example shows how to use the ``Stackup3D`` class
# to create and analyze a patch antenna in HFSS.
#
# Note that the HFSS 3D Layout interface may offer advantages for
# laminate structures such as the patch antenna.
#
# Keywords: **HFSS**, **terminal**, **antenna**., **patch**.
#
# ## Perform imports and define constants
#
# Perform required imports.

import os
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.modeler.advanced_cad.stackup_3d import Stackup3D

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

# ## Launch HFSS
#
# Launch HFSS and change the length units.

project_name = os.path.join(temp_folder.name, "patch.aedt")
hfss = ansys.aedt.core.Hfss(
    project=project_name,
    solution_type="Terminal",
    design="patch",
    non_graphical=NG_MODE,
    new_desktop=True,
    version=AEDT_VERSION,
)

length_units = "mm"
freq_units = "GHz"
hfss.modeler.model_units = length_units

# ## Create patch
#
# Create the patch.

# +
stackup = Stackup3D(hfss)
ground = stackup.add_ground_layer(
    "ground", material="copper", thickness=0.035, fill_material="air"
)
dielectric = stackup.add_dielectric_layer(
    "dielectric", thickness="0.5" + length_units, material="Duroid (tm)"
)
signal = stackup.add_signal_layer(
    "signal", material="copper", thickness=0.035, fill_material="air"
)
patch = signal.add_patch(
    patch_length=9.57, patch_width=9.25, patch_name="Patch", frequency=1e10
)

stackup.resize_around_element(patch)
pad_length = [3, 3, 3, 3, 3, 3]  # Air bounding box buffer in mm.
region = hfss.modeler.create_region(pad_length, is_percentage=False)
hfss.assign_radiation_boundary_to_objects(region)

patch.create_probe_port(ground, rel_x_offset=0.485)
# -

# ## Set up simulation
# Set up a simulation and analyze it.

# +
setup = hfss.create_setup(name="Setup1", setup_type="HFSSDriven", Frequency="10GHz")

setup.create_frequency_sweep(
    unit="GHz",
    name="Sweep1",
    start_frequency=8,
    stop_frequency=12,
    sweep_type="Interpolating",
)

hfss.save_project()
hfss.analyze(cores=NUM_CORES)
# -

# ## Plot S11
#

plot_data = hfss.get_traces_for_plot()
report = hfss.post.create_report(plot_data)
solution = report.get_solution_data()
plt = solution.plot(solution.expressions)

# ## Release AEDT
#
# Release AEDT.

hfss.save_project()
hfss.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes
# all temporary files, including the project folder.

temp_folder.cleanup()
