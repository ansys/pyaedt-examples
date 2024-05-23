# # HFSS: Probe-fed patch antenna
#
# This example shows how to use the ``Stackup3D`` class
# to create and analyze a patch antenna in HFSS.
#
# Note that the HFSS 3D Layout interface may offer advantages for
# laminate structures such as the patch antenna.
#
# Keywords: **HFSS**, **Patch**, **antenna**.

# ## Perform required imports
#
# Perform required imports.

import tempfile

from ansys.pyaedt.examples.constants import AEDT_VERSION, NUM_CORES
import pyaedt
from pyaedt.modeler.advanced_cad.stackup_3d import Stackup3D

# ## Set non-graphical mode
#
# Set non-graphical mode.
# You can set ``non_graphical`` either to ``True`` or ``False``.

non_graphical = False

# ## Create temporary directory

temp_dir = tempfile.TemporaryDirectory(suffix="_ansys")

# ## Launch HFSS
#
# Launch HFSS and change length units.

project_name = pyaedt.generate_unique_project_name(rootname=temp_dir.name, project_name="patch")
hfss = pyaedt.Hfss(
    projectname=project_name,
    solution_type="Terminal",
    designname="patch",
    non_graphical=non_graphical,
    new_desktop_session=True,
    specified_version=AEDT_VERSION,
)

length_units = "mm"
freq_units = "GHz"

hfss.modeler.model_units = length_units

# ## Create patch
#
# Create the patch.

# +
stackup = Stackup3D(hfss)
ground = stackup.add_ground_layer("ground", material="copper", thickness=0.035, fill_material="air")
dielectric = stackup.add_dielectric_layer(
    "dielectric", thickness="0.5" + length_units, material="Duroid (tm)"
)
signal = stackup.add_signal_layer("signal", material="copper", thickness=0.035, fill_material="air")
patch = signal.add_patch(patch_length=9.57, patch_width=9.25, patch_name="Patch", frequency=1e10)

stackup.resize_around_element(patch)
pad_length = [3, 3, 3, 3, 3, 3]  # Air bounding box buffer in mm.
region = hfss.modeler.create_region(pad_length, is_percentage=False)
hfss.assign_radiation_boundary_to_objects(region)

patch.create_probe_port(ground, rel_x_offset=0.485)
# -

# ## Set up simulation
# Set up a simulation and analyze it.

# +
setup = hfss.create_setup(setupname="Setup1", setuptype="HFSSDriven", Frequency="10GHz")

setup.create_frequency_sweep(
    unit="GHz", sweepname="Sweep1", freqstart=8, freqstop=12, sweep_type="Interpolating"
)

hfss.save_project()
hfss.analyze(num_cores=NUM_CORES)
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

hfss.release_desktop()

# ## Clean temporary directory

temp_dir.cleanup()
