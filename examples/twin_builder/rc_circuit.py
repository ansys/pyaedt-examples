# # Twin Builder: RC circuit design anaysis
#
# This example shows how you can use PyAEDT to create a Twin Builder design
# and run a Twin Builder time-domain simulation.


# ## Set up project
#
# Perform required imports.

import tempfile

import pyaedt

# Define constants.

AEDT_VERSION = "2024.1"
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary folder
#
# Simulation data will be saved in the temporary folder.
# If you run this example as a Jupyter Notebook,
# the results and project data can be retrieved before executing the
# final cell of the notebook.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Set up the simulation project
#
# Launch Twin Builder using an implicit declaration and add a new design with
# a default setup.

tb = pyaedt.TwinBuilder(
    project=os.path.join(temp_dir.name, "RC_ckt.aedt"),
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)
tb.modeler.schematic_units = "mil"

# ### Place components
#
# Create components for an RC circuit driven by a pulse voltage source.
# Create components, such as a voltage source, resistor, and capacitor.

source = tb.modeler.schematic.create_voltage_source("E1", "EPULSE", 10, 10, [0, 0])
resistor = tb.modeler.schematic.create_resistor("R1", 10000, [1000, 1000], 90)
capacitor = tb.modeler.schematic.create_capacitor("C1", 1e-6, [2000, 0])

# Create a ground, which is needed for an analog analysis.

gnd = tb.modeler.components.create_gnd([0, -1000])

# Connect components with pins.

source.pins[1].connect_to_component(resistor.pins[0])
resistor.pins[1].connect_to_component(capacitor.pins[0])
capacitor.pins[1].connect_to_component(source.pins[0])
source.pins[0].connect_to_component(gnd.pins[0])

# ## Solve
#
# Parametrize the default transient setup by setting the end time.

tb.set_end_time("300ms")

# Solve the transient setup.

tb.analyze_setup("TR")


# ## Postpprocessing
#
# Get report data and plot it using Matplotlib. The following code gets and plots
# the values for the voltage on the pulse voltage source and the values for the
# voltage on the capacitor in the RC circuit.

E_Value = "E1.V"
C_Value = "C1.V"
x = tb.post.get_solution_data([E_Value, C_Value], "TR", "Time")
x.plot([E_Value, C_Value], x_label="Time", y_label="Capacitor Voltage vs Input Pulse")
tb.save_project()
tb.release_desktop()

# ## Close Twin Builder
#
# After the simulation completes, you can close Twin Builder or release it.
# All methods provide for saving the project before closing.

# ## Cleanup
#
# All project files are saved in the folder ``temp_dir.name``.
# If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell removes all
# temporary files, including the project folder.

temp_dir.cleanup()
