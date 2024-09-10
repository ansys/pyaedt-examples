# # RC circuit design analysis
#
# This example shows how you can use PyAEDT to create a Twin Builder design
# and run a Twin Builder time-domain simulation.
#
# Keywords: **Twin Builder**, **RC**.

# ## Perform required imports
#
# Perform required imports.

import os
import tempfile
import time

import ansys.aedt.core

# ## Define constants

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory
#
# Create temporary directory.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch Twin Builder
#
# Launch Twin Builder using an implicit declaration and add a new design with
# a default setup.

project_name = os.path.join(temp_folder.name, "rc_circuit.aedt")
tb = ansys.aedt.core.TwinBuilder(
    project=project_name,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)
tb.modeler.schematic_units = "mil"

# ## Create components for RC circuit
#
# Create components for an RC circuit driven by a pulse voltage source.
# Create components, such as a voltage source, resistor, and capacitor.

source = tb.modeler.schematic.create_voltage_source("E1", "EPULSE", 10, 10, [0, 0])
resistor = tb.modeler.schematic.create_resistor("R1", 10000, [1000, 1000], 90)
capacitor = tb.modeler.schematic.create_capacitor("C1", 1e-6, [2000, 0])

# ## Create ground
#
# Create a ground, which is needed for an analog analysis.

gnd = tb.modeler.components.create_gnd([0, -1000])

# ## Connect components
#
# Connects components with pins.

source.pins[1].connect_to_component(resistor.pins[0])
resistor.pins[1].connect_to_component(capacitor.pins[0])
capacitor.pins[1].connect_to_component(source.pins[0])
source.pins[0].connect_to_component(gnd.pins[0])

# ## Parametrize transient setup
#
# Parametrize the default transient setup by setting the end time.

tb.set_end_time("300ms")

# ## Solve transient setup
#
# Solve the transient setup.

tb.analyze_setup("TR")


# ## Get report data and plot using Matplotlib
#
# Get report data and plot it using Matplotlib. The following code gets and plots
# the values for the voltage on the pulse voltage source and the values for the
# voltage on the capacitor in the RC circuit.

E_Value = "E1.V"
C_Value = "C1.V"

x = tb.post.get_solution_data([E_Value, C_Value], "TR", "Time")
x.plot([E_Value, C_Value], x_label="Time", y_label="Capacitor Voltage vs Input Pulse")

# ## Release AEDT
#
# Release AEDT and close the example.

tb.save_project()
tb.release_desktop()
# Wait 3 seconds to allow Electronics Desktop to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Cleanup
#
# All project files are saved in the folder ``temp_folder.name``. If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
