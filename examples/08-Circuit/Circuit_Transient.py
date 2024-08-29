# # Circuit Transient Analysis and Eye Diagram
#
# This example demonstrates how to create a circuit design,
# run a Nexxim time-domain simulation, and create an eye diagram.
#
# Keywords: **Circuit**, **Transient**, **Eye diagram**.

# ## Perform required imports
#
# Perform required imports.

# +
import os
import tempfile
import time

import ansys.aedt.core
import numpy as np
from matplotlib import pyplot as plt

# -

# ## Define constants

AEDT_VERSION = "2024.2"
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory and download files
#
# Create a temporary directory where we store downloaded data or
# dumped data.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT with Circuit
#
# Launch AEDT in graphical mode with the Circuit schematic editor.

circuit = ansys.aedt.core.Circuit(
    project=os.path.join(temp_folder.name, "CktTransient"),
    design="Circuit Examples",
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
)

# ## IBIS Buffer
#
# Read an IBIS file and place a buffer in the schematic editor.

ibis = circuit.get_ibis_model_from_file(
    os.path.join(circuit.desktop_install_dir, "buflib", "IBIS", "u26a_800.ibs")
)
ibs = ibis.buffers["DQ_u26a_800"].insert(0, 0)

# ## Ideal Transmission Line
#
# Place an ideal transmission line in the schematic and parametrize it.

tr1 = circuit.modeler.components.components_catalog["Ideal Distributed:TRLK_NX"].place(
    "tr1"
)
tr1.parameters["P"] = "50mm"

# ## Component Placement
#
# Create a resistor and ground in the schematic.

res = circuit.modeler.components.create_resistor(name="R1", value="1Meg")
gnd1 = circuit.modeler.components.create_gnd()

# ## Connect Componennts
#
# Connect the components in the schematic.

tr1.pins[0].connect_to_component(ibs.pins[0])
tr1.pins[1].connect_to_component(res.pins[0])
res.pins[1].connect_to_component(gnd1.pins[0])

# ## Voltage Probe
#
# Place a probe and rename it to ``Vout``.

pr1 = circuit.modeler.components.components_catalog["Probes:VPROBE"].place("vout")
pr1.parameters["Name"] = "Vout"
pr1.pins[0].connect_to_component(res.pins[0])
pr2 = circuit.modeler.components.components_catalog["Probes:VPROBE"].place("Vin")
pr2.parameters["Name"] = "Vin"
pr2.pins[0].connect_to_component(ibs.pins[0])

# ## Analyze
#
# Create a transient analysis setup and analyze it.

trans_setup = circuit.create_setup(name="TransientRun", setup_type="NexximTransient")
trans_setup.props["TransientData"] = ["0.01ns", "200ns"]
circuit.analyze_setup("TransientRun")

# ## Results
#
# Create a report using the ``get_solution_data()`` method. This
# method allows you to view and post-process results using Python packages.
# The ``solutions.plot()`` method uses
# [Matplotlib](https://matplotlib.org/).

report = circuit.post.create_report("V(Vout)", domain="Time")
if not NG_MODE:
    report.add_cartesian_y_marker(0)
solutions = circuit.post.get_solution_data(domain="Time")
solutions.plot("V(Vout)")

# ## Visualize Results
#
# Create a report inside AEDT using the ``new_report`` object. This object is
# fully customizable and usable with most of the reports available in AEDT.
# The standard report is the main one used in Circuit and Twin Builder.

new_report = circuit.post.reports_by_category.standard("V(Vout)")
new_report.domain = "Time"
new_report.create()
if not NG_MODE:
    new_report.add_limit_line_from_points([60, 80], [1, 1], "ns", "V")
    vout = new_report.traces[0]
    vout.set_trace_properties(
        style=vout.LINESTYLE.Dot,
        width=2,
        trace_type=vout.TRACETYPE.Continuous,
        color=(0, 0, 255),
    )
    vout.set_symbol_properties(
        style=vout.SYMBOLSTYLE.Circle, fill=True, color=(255, 255, 0)
    )
    ll = new_report.limit_lines[0]
    ll.set_line_properties(
        style=ll.LINESTYLE.Solid,
        width=4,
        hatch_above=True,
        violation_emphasis=True,
        hatch_pixels=2,
        color=(0, 0, 255),
    )
new_report.time_start = "20ns"
new_report.time_stop = "100ns"
new_report.create()
sol = new_report.get_solution_data()
sol.plot()

# ## Eye Diagram in AEDT
#
# Create an eye diagram inside AEDT using the ``new_eye`` object.

new_eye = circuit.post.reports_by_category.eye_diagram("V(Vout)")
new_eye.unit_interval = "1e-9s"
new_eye.time_stop = "100ns"
new_eye.create()

# ## Eye Diagram in Matplotlib
#
# Create the same eye diagram outside AEDT using Matplotlib and the
# ``get_solution_data()`` method.

# +
unit_interval = 1
offset = 0.25
tstop = 200
tstart = 0
t_steps = []
i = tstart + offset
while i < tstop:
    i += 2 * unit_interval
    t_steps.append(i)

t = [
    [i for i in solutions.intrinsics["Time"] if k - 2 * unit_interval < i <= k]
    for k in t_steps
]
ys = [
    [
        i / 1000
        for i, j in zip(solutions.data_real(), solutions.intrinsics["Time"])
        if k - 2 * unit_interval < j <= k
    ]
    for k in t_steps
]
fig, ax = plt.subplots(sharex=True)
cells = np.array([])
cellsv = np.array([])
for a, b in zip(t, ys):
    an = np.array(a)
    an = an - an.mean()
    bn = np.array(b)
    cells = np.append(cells, an)
    cellsv = np.append(cellsv, bn)
plt.plot(cells.T, cellsv.T, zorder=0)
plt.show()
# -

# ## Release AEDT
#
# Release AEDT and close the example.

circuit.save_project()
circuit.release_desktop()
# Wait 3 seconds to allow Electronics Desktop to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Cleanup
#
# All project files are saved in the folder ``temp_folder.name``. If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
