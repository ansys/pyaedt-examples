# # Q3D Extractor: busbar analysis

# This example shows how you can use PyAEDT to create a busbar design in
# Q3D Extractor and run a simulation.

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

# ## Launch AEDT and Q3D Extractor
#
# Launch AEDT 2024 R1 in graphical mode and launch Q3D Extractor. This example uses SI units.

q3d = pyaedt.Q3d(
    project=os.path.join(temp_dir.name, "busbar"),
    version=AEDT_VERSION,
    non_graphical=False,
    new_desktop=True,
)

# ## Create primitives
#
# Create polylines for three busbars and a box for the substrate.

# +
b1 = q3d.modeler.create_polyline(
    position_list=[[0, 0, 0], [-100, 0, 0]],
    name="Bar1",
    matname="copper",
    xsection_type="Rectangle",
    xsection_width="5mm",
    xsection_height="1mm",
)
q3d.modeler["Bar1"].color = (255, 0, 0)

q3d.modeler.create_polyline(
    points=[[0, -15, 0], [-150, -15, 0]],
    name="Bar2",
    matname="aluminum",
    xsection_type="Rectangle",
    xsection_width="5mm",
    xsection_height="1mm",
)
q3d.modeler["Bar2"].color = (0, 255, 0)

q3d.modeler.create_polyline(
    points=[[0, -30, 0], [-175, -30, 0], [-175, -10, 0]],
    name="Bar3",
    matname="copper",
    xsection_type="Rectangle",
    xsection_width="5mm",
    xsection_height="1mm",
)
q3d.modeler["Bar3"].color = (0, 0, 255)

q3d.modeler.create_box(
    origin=[50, 30, -0.5], sizes=[-250, -100, -3], name="substrate", matname="FR4_epoxy"
)
q3d.modeler["substrate"].color = (128, 128, 128)
q3d.modeler["substrate"].transparency = 0.8

q3d.plot(show=False, export_path=os.path.join(temp_dir.name, "Q3D.jpg"), plot_air_objects=False)
# -

# ## Set up boundaries
#
# Identify nets and assign sources and sinks to all nets.
# There is a source and sink for each busbar.

# +
q3d.auto_identify_nets()

q3d.source(assignment="Bar1", axisdir=q3d.AxisDir.XPos, name="Source1")
q3d.sink(assignment="Bar1", axisdir=q3d.AxisDir.XNeg, name="Sink1")

q3d.source(assignment="Bar2", axisdir=q3d.AxisDir.XPos, name="Source2")
q3d.sink(assignment="Bar2", axisdir=q3d.AxisDir.XNeg, name="Sink2")
q3d.source(assignment="Bar3", axisdir=q3d.AxisDir.XPos, name="Source3")
bar3_sink = q3d.sink(assignment="Bar3", axisdir=q3d.AxisDir.YPos, name="Sink3")
# -

# ## Print information
#
# Use the different methods available to print net and terminal information.

print(q3d.nets)
print(q3d.net_sinks("Bar1"))
print(q3d.net_sinks("Bar2"))
print(q3d.net_sinks("Bar3"))
print(q3d.net_sources("Bar1"))
print(q3d.net_sources("Bar2"))
print(q3d.net_sources("Bar3"))

# ## Create setup
#
# Create a setup for Q3D Extractor and add a sweep that defines the adaptive
# frequency value.

setup1 = q3d.create_setup(props={"AdaptiveFreq": "100MHz"})
sweep = setup1.add_sweep()
sweep.props["RangeStart"] = "1MHz"
sweep.props["RangeEnd"] = "100MHz"
sweep.props["RangeStep"] = "5MHz"
sweep.update()

# ## Get curves to plot
#
# Get the curves to plot. The following code simplifies the way to get curves.

data_plot_self = q3d.matrices[0].get_sources_for_plot(get_self_terms=True, get_mutual_terms=False)
data_plot_mutual = q3d.get_traces_for_plot(
    get_self_terms=False, get_mutual_terms=True, category="C"
)

# ## Create rectangular plot
#
# Create a rectangular plot and a data table.

q3d.post.create_report(expressions=data_plot_self)
q3d.post.create_report(expressions=data_plot_mutual, context="Original", plot_type="Data Table")

# ## Solve setup
#
# Solve the setup.

q3d.analyze(num_cores=NUM_CORES)
q3d.save_project()

# ## Get report data
#
# Get the report data into a data structure that allows you to manipulate it.

data = q3d.post.get_solution_data(expressions=data_plot_self, context="Original")
data.data_magnitude()
data.plot()

# ## Close AEDT
#
# After the simulation completes, you can close AEDT or release it using the
# ``release_desktop`` method. All methods provide for saving projects before closing.

q3d.release_desktop(close_projects=True, close_desktop=True)
temp_dir.cleanup()
