# # 2D Extractor: stripline analysis

# This example shows how you can use PyAEDT to create a differential stripline design in
# 2D Extractor and run a simulation.

# ## Perform required imports
#
# Perform required imports.

# +
import os
import tempfile

from ansys.pyaedt.examples.constants import AEDT_VERSION, NUM_CORES
import pyaedt

# -

# ## Create temporary directory
#
# Create temporary directory.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT and 2D Extractor
#
# Launch AEDT 2024.1 in graphical mode and launch 2D Extractor. This example
# uses SI units.

q2d = pyaedt.Q2d(
    projectname=pyaedt.generate_unique_project_name(),
    designname="differential_stripline",
    specified_version=AEDT_VERSION,
    non_graphical=False,
    new_desktop_session=True,
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

base_line_obj = q2d.modeler.create_polyline(
    [[0, layer_2_lh, 0], [sig_w, layer_2_lh, 0]], name="signal_p"
)
top_line_obj = q2d.modeler.create_polyline([[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]])
q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
q2d.modeler.connect([base_line_obj, top_line_obj])
q2d.modeler.move([base_line_obj], ["{}+{}".format(co_gnd_w, clearance), 0, 0])

# ## Create negative signal
#
# Create a negative signal.

base_line_obj = q2d.modeler.create_polyline(
    position_list=[[0, layer_2_lh, 0], [sig_w, layer_2_lh, 0]], name="signal_n"
)
top_line_obj = q2d.modeler.create_polyline(
    position_list=[[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]]
)
q2d.modeler.move(objid=[top_line_obj], vector=[delta_w_half, 0, 0])
q2d.modeler.connect([base_line_obj, top_line_obj])
q2d.modeler.move(
    objid=[base_line_obj], vector=["{}+{}+{}+{}".format(co_gnd_w, clearance, sig_w, sig_gap), 0, 0]
)

# ## Create coplanar ground
#
# Create a coplanar ground.

# +
base_line_obj = q2d.modeler.create_polyline(
    position_list=[[0, layer_2_lh, 0], [co_gnd_w, layer_2_lh, 0]], name="co_gnd_left"
)
top_line_obj = q2d.modeler.create_polyline(
    position_list=[[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]]
)
q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
q2d.modeler.connect([base_line_obj, top_line_obj])

base_line_obj = q2d.modeler.create_polyline(
    position_list=[[0, layer_2_lh, 0], [co_gnd_w, layer_2_lh, 0]], name="co_gnd_right"
)
top_line_obj = q2d.modeler.create_polyline(
    position_list=[[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]]
)
q2d.modeler.move(objid=[top_line_obj], vector=[delta_w_half, 0, 0])
q2d.modeler.connect([base_line_obj, top_line_obj])
q2d.modeler.move(
    objid=[base_line_obj],
    vector=["{}+{}*2+{}*2+{}".format(co_gnd_w, clearance, sig_w, sig_gap), 0, 0],
)
# -

# ## Create reference ground plane
#
# Create a reference ground plane.

q2d.modeler.create_rectangle(
    position=[0, layer_1_lh, 0], dimension_list=[model_w, cond_h], name="ref_gnd_u"
)
q2d.modeler.create_rectangle(
    position=[0, layer_3_lh, 0], dimension_list=[model_w, cond_h], name="ref_gnd_l"
)

# ## Create dielectric
#
# Create a dielectric.

q2d.modeler.create_rectangle(
    position=[0, layer_1_uh, 0], dimension_list=[model_w, core_h], name="Core", matname="FR4_epoxy"
)
q2d.modeler.create_rectangle(
    position=[0, layer_2_uh, 0], dimension_list=[model_w, pp_h], name="Prepreg", matname="FR4_epoxy"
)
q2d.modeler.create_rectangle(
    position=[0, layer_2_lh, 0],
    dimension_list=[model_w, cond_h],
    name="Filling",
    matname="FR4_epoxy",
)

# ## Assign conductors
#
# Assign conductors to the signal.

# +
obj = q2d.modeler.get_object_from_name("signal_p")
q2d.assign_single_conductor(
    name=obj.name,
    target_objects=[obj],
    conductor_type="SignalLine",
    solve_option="SolveOnBoundary",
    unit="mm",
)

obj = q2d.modeler.get_object_from_name("signal_n")
q2d.assign_single_conductor(
    name=obj.name,
    target_objects=[obj],
    conductor_type="SignalLine",
    solve_option="SolveOnBoundary",
    unit="mm",
)
# -

# ## Create reference ground
#
# Create a reference ground.

obj = [
    q2d.modeler.get_object_from_name(i)
    for i in ["co_gnd_left", "co_gnd_right", "ref_gnd_u", "ref_gnd_l"]
]
q2d.assign_single_conductor(
    name="gnd",
    target_objects=obj,
    conductor_type="ReferenceGround",
    solve_option="SolveOnBoundary",
    unit="mm",
)

# ## Assign Huray model on signals
#
# Assign the Huray model on the signals.

# +
obj = q2d.modeler.get_object_from_name("signal_p")
q2d.assign_huray_finitecond_to_edges(obj.edges, radius="0.5um", ratio=3, name="b_" + obj.name)

obj = q2d.modeler.get_object_from_name("signal_n")
q2d.assign_huray_finitecond_to_edges(obj.edges, radius="0.5um", ratio=3, name="b_" + obj.name)
# -

# ## Define differential pair
#
# Define the differential pair.

matrix = q2d.insert_reduced_matrix(
    operation_name=q2d.MATRIXOPERATIONS.DiffPair,
    source_names=["signal_p", "signal_n"],
    rm_name="diff_pair",
)

# ## Create setup, analyze, and plot
#
# Create a setup, analyze, and plot solution data.

# Create a setup.

setup = q2d.create_setup(setupname="new_setup")

# Add a sweep.

sweep = setup.add_sweep(sweepname="sweep1", sweeptype="Discrete")
sweep.props["RangeType"] = "LinearStep"
sweep.props["RangeStart"] = "1GHz"
sweep.props["RangeStep"] = "100MHz"
sweep.props["RangeEnd"] = "5GHz"
sweep.props["SaveFields"] = False
sweep.props["SaveRadFields"] = False
sweep.props["Type"] = "Interpolating"
sweep.update()

# Analyze the nominal design and plot characteristic impedance.

q2d.analyze()
plot_sources = matrix.get_sources_for_plot(category="Z0")

# Get simulation results as a ``SolutionData`` object and plot as a jpg

data = q2d.post.get_solution_data(expressions=plot_sources, context=matrix.name)
data.plot(snapshot_path=os.path.join(temp_dir.name, "plot.jpg"))

# Add a parametric sweep and analyze.

parametric = q2d.parametrics.add(
    sweep_var="sig_bot_w", start_point=75, end_point=100, step=5, variation_type="LinearStep"
)
parametric.add_variation(
    sweep_var="sig_gap",
    start_point="100um",
    end_point="200um",
    step=5,
    variation_type="LinearCount",
)
q2d.analyze_setup(name=parametric.name, num_cores=NUM_CORES)

# ## Save project and release AEDT
#
# Save the project, release AEDT and remove both the project and temporary directory.

q2d.save_project()
q2d.release_desktop()
temp_dir.cleanup()
