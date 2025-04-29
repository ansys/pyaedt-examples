# # Wiring of a rectifier with a capacitor filter
#
# This example shows how to use PyAEDT to create a Twin Builder design
# and run a Twin Builder time-domain simulation.
#
# <img src="_static/rectifier.png" width="500">
#
# Keywords: **Twin Builder**, **rectifier**, **filter**.

# ## Perform imports and define constants
#
# Perform required imports.

# +
import os
import tempfile
import time

import ansys.aedt.core
import matplotlib.pyplot as plt
# -

# Define constants.

AEDT_VERSION = "2025.1"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch Twin Builder
#
# Launch Twin Builder using an implicit declaration and add a new design with
# the default setup.

project_name = os.path.join(temp_folder.name, "TB_Rectifier_Demo.aedt")
tb = ansys.aedt.core.TwinBuilder(
    project=project_name,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Create components
#
# Place components for a bridge rectifier and a capacitor filter in the schematic editor.
#
# Specify the grid spacing to use for placement
# of components in the schematic editor. Components are placed using the named
# argument ``location`` as a list of ``[x, y]`` values in millimeters.

G = 0.00254

# Create an AC sinosoidal voltage source.

source = tb.modeler.schematic.create_voltage_source(
    "V_AC", "ESINE", 100, 50, location=[-1 * G, 0]
)

# Place the four diodes of the bridge rectifier. The named argument ``angle`` is the rotation angle
# of the component in radians.

diode1 = tb.modeler.schematic.create_diode(
    name="D1", location=[10 * G, 6 * G], angle=270
)
diode2 = tb.modeler.schematic.create_diode(
    name="D2", location=[20 * G, 6 * G], angle=270
)
diode3 = tb.modeler.schematic.create_diode(
    name="D3", location=[10 * G, -4 * G], angle=270
)
diode4 = tb.modeler.schematic.create_diode(
    name="D4", location=[20 * G, -4 * G], angle=270
)

# Place a capacitor filter.

capacitor = tb.modeler.schematic.create_capacitor(
    name="C_FILTER", value=1e-6, location=[29 * G, -10 * G]
)

# Place a load resistor.

resistor = tb.modeler.schematic.create_resistor(
    name="RL", value=100000, location=[39 * G, -10 * G]
)

# Place the ground component.

gnd = tb.modeler.components.create_gnd(location=[5 * G, -16 * G])

# ## Connect components
#
# Connect components with wires, and connect the diode pins to create the bridge.

tb.modeler.schematic.create_wire(
    points=[diode1.pins[0].location, diode3.pins[0].location]
)
tb.modeler.schematic.create_wire(
    points=[diode2.pins[1].location, diode4.pins[1].location]
)
tb.modeler.schematic.create_wire(
    points=[diode1.pins[1].location, diode2.pins[0].location]
)
tb.modeler.schematic.create_wire(
    points=[diode3.pins[1].location, diode4.pins[0].location]
)

# Connect the voltage source to the bridge.

tb.modeler.schematic.create_wire(
    points=[source.pins[1].location, [0, 10 * G], [15 * G, 10 * G], [15 * G, 5 * G]]
)
tb.modeler.schematic.create_wire(
    points=[source.pins[0].location, [0, -10 * G], [15 * G, -10 * G], [15 * G, -5 * G]]
)

# Connect the filter capacitor and load resistor.

tb.modeler.schematic.create_wire(
    points=[resistor.pins[0].location, [40 * G, 0], [22 * G, 0]]
)
tb.modeler.schematic.create_wire(points=[capacitor.pins[0].location, [30 * G, 0]])

# Add the ground connection.

tb.modeler.schematic.create_wire(
    points=[resistor.pins[1].location, [40 * G, -15 * G], gnd.pins[0].location]
)
tb.modeler.schematic.create_wire(points=[capacitor.pins[1].location, [30 * G, -15 * G]])
tb.modeler.schematic.create_wire(points=[gnd.pins[0].location, [5 * G, 0], [8 * G, 0]])

# Zoom to fit the schematic
tb.modeler.zoom_to_fit()

# The circuit schematic should now be visible in the Twin Builder
# schematic editor and look like
# the image shown at the beginning of the example.
#
# ## Run the simulation
#
# Update the total time to be simulated and run the analysis.

tb.set_end_time("100ms")
tb.analyze_setup("TR")

# ## Get report data and plot using Matplotlib
#
# Get report data and plot it using Matplotlib. The following code gets and plots
# the values for the voltage on the pulse voltage source and the values for the
# voltage on the capacitor in the RC circuit.

src_name = source.InstanceName + ".V"
x = tb.post.get_solution_data(src_name, "TR", "Time")
plt.plot(x.intrinsics["Time"], x.data_real(src_name))
plt.grid()
plt.xlabel("Time")
plt.ylabel("AC Voltage")
plt.show()

r_voltage = resistor.InstanceName + ".V"
x = tb.post.get_solution_data(r_voltage, "TR", "Time")
plt.plot(x.intrinsics["Time"], x.data_real(r_voltage))
plt.grid()
plt.xlabel("Time")
plt.ylabel("AC to DC Conversion using Rectifier")
plt.show()

# ## Release AEDT
#
# Release AEDT and close the example.

tb.save_project()
tb.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``. If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
