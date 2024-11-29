# # Busbar analysis

# This example shows how to use PyAEDT to create a busbar design in
# Q3D Extractor and run a simulation.
#
# Keywords: **Q3D**, **EMC*, **busbar**.

# ## Perform imports and define constants
#
# Perform required imports.

import os
import tempfile
import time

import ansys.aedt.core

# Define constants.

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT and Q3D Extractor
#
# Launch AEDT 2024 R2 in graphical mode and launch Q3D Extractor. This example uses SI units.

q3d = ansys.aedt.core.Q3d(
    project=os.path.join(temp_folder.name, "busbar.aedt"),
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Create and set up the Q3D model
#
# Create polylines for three busbars and a box for the substrate.

# +
b1 = q3d.modeler.create_polyline(
    points=[[0, 0, 0], [-100, 0, 0]],
    name="Bar1",
    material="copper",
    xsection_type="Rectangle",
    xsection_width="5mm",
    xsection_height="1mm",
)
q3d.modeler["Bar1"].color = (255, 0, 0)

q3d.modeler.create_polyline(
    points=[[0, -15, 0], [-150, -15, 0]],
    name="Bar2",
    material="aluminum",
    xsection_type="Rectangle",
    xsection_width="5mm",
    xsection_height="1mm",
)
q3d.modeler["Bar2"].color = (0, 255, 0)

q3d.modeler.create_polyline(
    points=[[0, -30, 0], [-175, -30, 0], [-175, -10, 0]],
    name="Bar3",
    material="copper",
    xsection_type="Rectangle",
    xsection_width="5mm",
    xsection_height="1mm",
)
q3d.modeler["Bar3"].color = (0, 0, 255)

q3d.modeler.create_box(
    origin=[50, 30, -0.5],
    sizes=[-250, -100, -3],
    name="substrate",
    material="FR4_epoxy",
)
q3d.modeler["substrate"].color = (128, 128, 128)
q3d.modeler["substrate"].transparency = 0.8

q3d.plot(
    show=False,
    output_file=os.path.join(temp_folder.name, "Q3D.jpg"),
    plot_air_objects=False,
)
# -

# Identify nets and assign sources and sinks to all nets.
# There is a source and sink for each busbar.

# +
q3d.auto_identify_nets()

q3d.source(assignment="Bar1", direction=q3d.AxisDir.XPos, name="Source1")
q3d.sink(assignment="Bar1", direction=q3d.AxisDir.XNeg, name="Sink1")

q3d.source(assignment="Bar2", direction=q3d.AxisDir.XPos, name="Source2")
q3d.sink(assignment="Bar2", direction=q3d.AxisDir.XNeg, name="Sink2")
q3d.source(assignment="Bar3", direction=q3d.AxisDir.XPos, name="Source3")
bar3_sink = q3d.sink(assignment="Bar3", direction=q3d.AxisDir.YPos, name="Sink3")
# -

# Print information about nets and terminal assignments.

print(q3d.nets)
print(q3d.net_sinks("Bar1"))
print(q3d.net_sinks("Bar2"))
print(q3d.net_sinks("Bar3"))
print(q3d.net_sources("Bar1"))
print(q3d.net_sources("Bar2"))
print(q3d.net_sources("Bar3"))


# ## Create Matrix Reduction Operations
#
# Series of Bar1 and Bar2

mr_series = q3d.insert_reduced_matrix(
    operation_name="JoinSeries",
    assignment=["Sink1", "Source2"],
    reduced_matrix="MR_1_Series",
    new_net_name="Series1",
)

# Add Parallel with Bar3

mr_series.add_operation(
    operation_type="JoinParallel",
    source_names=["Source1", "Source3"],
    new_net_name="SeriesPar",
    new_source_name="src_par",
    new_sink_name="snk_par",
)

# Series of Bar1 and Bar2

mr_series2 = q3d.insert_reduced_matrix(
    operation_name="JoinSeries",
    assignment=["Sink1", "Source2"],
    reduced_matrix="MR_2_Series",
    new_net_name="Series2",
)

# Add Series with Bar3

mr_series2.add_operation(
    operation_type="JoinSeries",
    source_names=["Sink3", "Source1"],
    new_net_name="MR_2_Series1",
)

# ## Add a solution Setup and an interpolating frequency sweep
#

freq_sweep_name = "my_sweep"
setup1 = q3d.create_setup(props={"AdaptiveFreq": "1000MHz"})
sweep = setup1.create_linear_step_sweep(
    freqstart=0,
    freqstop=10,
    step_size=0.05,
    sweepname=freq_sweep_name,
    sweep_type="Interpolating",
)

# ## Analyze
#
# Solve the setup.

q3d.analyze(cores=NUM_CORES)
q3d.save_project()

# ## Postprocessing: specify the traces to display and create the Reports.
#
# Capacitances - Original Matrix.

data_plot_self = q3d.matrices[0].get_sources_for_plot(
    get_self_terms=True, get_mutual_terms=False
)
data_plot_mutual = q3d.get_traces_for_plot(
    get_self_terms=False, get_mutual_terms=True, category="C"
)

# ACL - Reduced Matrix MR_1_Series

data_red_m1_plot_self = q3d.matrices[1].get_sources_for_plot(
    get_self_terms=True, get_mutual_terms=False, category="ACL"
)

# ACL - Reduced Matrix MR_2_Series

data_red_m2_plot_self = q3d.matrices[2].get_sources_for_plot(
    get_self_terms=True, get_mutual_terms=False, category="ACL"
)

# Define plots and a data table in AEDT for visualizing results.

rep_original_self_c = q3d.post.create_report(
    expressions=data_plot_self, plot_name="Original, Self Capacitances"
)
rep_original_mutual_c = q3d.post.create_report(
    expressions=data_plot_mutual,
    context="Original",
    plot_type="Data Table",
    plot_name="Original, Mutual Capacitances",
)
rep_red_m1_self_acl = q3d.post.create_report(
    expressions=data_red_m1_plot_self,
    context="MR_1_Series",
    plot_name="MR_1_Series, Self Inductances",
)
reduced_matrix_2_self_report = q3d.post.create_report(
    expressions=data_red_m2_plot_self,
    context="MR_2_Series",
    plot_name="MR_2_Series, Self Inductances",
)
rep_red_m2_self_acl.edit_x_axis_scaling(linear_scaling=False)

# Retrieve solution data for processing in Python.

data = q3d.post.get_solution_data(expressions=data_plot_self, context="Original")
data.data_magnitude()
data.plot()

# ## Release AEDT

q3d.save_project()
q3d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
