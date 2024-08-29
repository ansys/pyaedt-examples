# # Busbar analysis

# This example shows how you can use PyAEDT to create a busbar design in
# Q3D Extractor and run a simulation.
#
# Keywords: **Q3D**, **Busbar**.

# ## Perform required imports
#
# Perform required imports.

import os
import tempfile
import time

import ansys.aedt.core

# Set constant values

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False

# ## Create temporary directory
#
# Create temporary directory.
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

# Create the solution setup and define the frequency range for the solution.

setup1 = q3d.create_setup(props={"AdaptiveFreq": "100MHz"})
sweep = setup1.add_sweep()
sweep.props["RangeStart"] = "1MHz"
sweep.props["RangeEnd"] = "100MHz"
sweep.props["RangeStep"] = "5MHz"
sweep.update()

# ### Setup for postprocessing
#
# Specify the traces that will be displayed after solving the model.

data_plot_self = q3d.matrices[0].get_sources_for_plot(
    get_self_terms=True, get_mutual_terms=False
)
data_plot_mutual = q3d.get_traces_for_plot(
    get_self_terms=False, get_mutual_terms=True, category="C"
)

# Define a plot and a data table in Electronics Desktop for visualizing results.

q3d.post.create_report(expressions=data_plot_self)
q3d.post.create_report(
    expressions=data_plot_mutual, context="Original", plot_type="Data Table"
)

# ## Analyze
#
# Solve the setup.

q3d.analyze(cores=NUM_CORES)
q3d.save_project()

# Retrieve solution data for processing in Python.

data = q3d.post.get_solution_data(expressions=data_plot_self, context="Original")
data.data_magnitude()
data.plot()

# ## Release AEDT

q3d.save_project()
q3d.release_desktop()
# Wait 3 seconds to allow Electronics Desktop to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Cleanup
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
