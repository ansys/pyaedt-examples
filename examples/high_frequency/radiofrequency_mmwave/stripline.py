# # Stripline analysis

# This example shows how to use PyAEDT to create a differential stripline design in
# 2D Extractor and run a simulation.
#
# Keywords: **Q2D**, **Stripline**.

# ## Perform imports and define constants
#
# Perform required imports.

# +
import os
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.generic.constants import MatrixOperationsQ2D

# -

# Define constants.

AEDT_VERSION = "2025.2"
NUM_CORES = 4


# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT and 2D Extractor
#
# Launch AEDT 2025.2 in graphical mode and launch 2D Extractor. This example
# uses SI units.

q2d = ansys.aedt.core.Q2d(
    project=os.path.join(temp_folder.name, "stripline"),
    design="differential_stripline",
    version=AEDT_VERSION,
    non_graphical=False,
    new_desktop=True,
)

# ## Define variables
#
# Define variables.

# +
e_factor = "e_factor"
sig_w = "sig_bot_w"
sig_gap = "sig_gap"
co_gnd_w = "gnd_w"
clearance = "clearance"
cond_h = "cond_h"
core_h = "core_h"
pp_h = "pp_h"

for var_name, var_value in {
    "e_factor": "2",
    "sig_bot_w": "150um",
    "sig_gap": "150um",
    "gnd_w": "500um",
    "clearance": "150um",
    "cond_h": "17um",
    "core_h": "150um",
    "pp_h": "150um",
}.items():
    q2d[var_name] = var_value

delta_w_half = "({0}/{1})".format(cond_h, e_factor)
sig_top_w = "({1}-{0}*2)".format(delta_w_half, sig_w)
co_gnd_top_w = "({1}-{0}*2)".format(delta_w_half, co_gnd_w)
model_w = "{}*2+{}*2+{}*2+{}".format(co_gnd_w, clearance, sig_w, sig_gap)
# -

# ## Create primitives
#
# Create primitives and define the layer heights.

layer_1_lh = 0
layer_1_uh = cond_h
layer_2_lh = layer_1_uh + "+" + core_h
layer_2_uh = layer_2_lh + "+" + cond_h
layer_3_lh = layer_2_uh + "+" + pp_h
layer_3_uh = layer_3_lh + "+" + cond_h

# ## Create positive signal
#
# Create a positive signal.

signal_p_1 = q2d.modeler.create_polyline(points=[[0, layer_2_lh, 0], [sig_w, layer_2_lh, 0]], name="signal_p_1")

signal_p_2 = q2d.modeler.create_polyline(points=[[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]], name="signal_p_2")
q2d.modeler.move([signal_p_2], [delta_w_half, 0, 0])
q2d.modeler.connect([signal_p_1, signal_p_2])
q2d.modeler.move(assignment=[signal_p_1], vector=["{}+{}".format(co_gnd_w, clearance), 0, 0])

# ## Create negative signal
#
# Create a negative signal.

signal_n_1 = q2d.modeler.create_polyline(points=[[0, layer_2_lh, 0], [sig_w, layer_2_lh, 0]], name="signal_n_1")

signal_n_2 = q2d.modeler.create_polyline(points=[[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]], name="signal_n_2")

q2d.modeler.move(assignment=[signal_n_2], vector=[delta_w_half, 0, 0])
q2d.modeler.connect([signal_n_1, signal_n_2])
q2d.modeler.move(
    assignment=[signal_n_1],
    vector=["{}+{}+{}+{}".format(co_gnd_w, clearance, sig_w, sig_gap), 0, 0],
)

# ## Create reference ground plane
#
# Create a reference ground plane.

ref_gnd_u = q2d.modeler.create_rectangle(origin=[0, layer_1_lh, 0], sizes=[model_w, cond_h], name="ref_gnd_u")
ref_gnd_l = q2d.modeler.create_rectangle(origin=[0, layer_3_lh, 0], sizes=[model_w, cond_h], name="ref_gnd_l")

# ## Create dielectric
#
# Create a dielectric.

q2d.modeler.create_rectangle(
    origin=[0, layer_1_uh, 0],
    sizes=[model_w, core_h],
    name="Core",
    material="FR4_epoxy",
)
q2d.modeler.create_rectangle(
    origin=[0, layer_2_uh, 0],
    sizes=[model_w, pp_h],
    name="Prepreg",
    material="FR4_epoxy",
)
q2d.modeler.create_rectangle(
    origin=[0, layer_2_lh, 0],
    sizes=[model_w, cond_h],
    name="Filling",
    material="FR4_epoxy",
)

# ## Assign conductors
#
# Assign conductors to the signal.

# +
q2d.assign_single_conductor(
    name=signal_p_1.name,
    assignment=[signal_p_1],
    conductor_type="SignalLine",
    solve_option="SolveOnBoundary",
    units="mm",
)

q2d.assign_single_conductor(
    name=signal_n_1.name,
    assignment=[signal_n_1],
    conductor_type="SignalLine",
    solve_option="SolveOnBoundary",
    units="mm",
)
# -

# ## Create reference ground
#
# Create a reference ground.

q2d.assign_single_conductor(
    name="gnd",
    assignment=[ref_gnd_u, ref_gnd_l],
    conductor_type="ReferenceGround",
    solve_option="SolveOnBoundary",
    units="mm",
)

# ## Assign Huray model on signals
#
# Assign the Huray model on the signals.

# +
q2d.assign_huray_finitecond_to_edges(signal_p_1.edges, radius="0.5um", ratio=3, name="b_" + signal_p_1.name)

q2d.assign_huray_finitecond_to_edges(signal_n_1.edges, radius="0.5um", ratio=3, name="b_" + signal_n_1.name)
# -

# ## Define differential pair
#
# Define the differential pair.

matrix = q2d.insert_reduced_matrix(
    operation_name=MatrixOperationsQ2D.DiffPair,
    assignment=["signal_p_1", "signal_n_1"],
    reduced_matrix="diff_pair",
)

# ## Create setup, analyze, and plot
#
# Create a setup, analyze, and plot solution data.

# Create a setup.

setup = q2d.create_setup(name="new_setup")

# Add a sweep.

sweep = setup.add_sweep(name="sweep1", sweep_type="Discrete")
sweep.props["RangeType"] = "LinearStep"
sweep.props["RangeStart"] = "1GHz"
sweep.props["RangeStep"] = "100MHz"
sweep.props["RangeEnd"] = "5GHz"
sweep.props["SaveFields"] = False
sweep.props["SaveRadFields"] = False
sweep.props["Type"] = "Interpolating"
sweep.update()

# Analyze the nominal design and plot characteristic impedance.

q2d.analyze(cores=NUM_CORES)
plot_sources = matrix.get_sources_for_plot(category="Z0")

# Get simulation results as a ``SolutionData`` object and plot to a JPG file.

data = q2d.post.get_solution_data(expressions=plot_sources, context=matrix.name)
data.plot(snapshot_path=os.path.join(temp_folder.name, "plot.jpg"))

# -

# ## Release AEDT

q2d.save_project()
q2d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
