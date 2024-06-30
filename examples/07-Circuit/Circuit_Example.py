# # Circuit Schematic Creation and Analysis
#
# This example shows how to build a circuit schematic
# and run a transient circuit simulation.

# <img src="_static/circuit.png" width="600">
#
# ## Perform required imports
#
# Perform required imports.

# +
import os
import tempfile
import time

import pyaedt

# -

# Set constant values

AEDT_VERSION = "2024.1"

# ## Launch AEDT
#
# Launch AEDT in graphical mode. This example uses SI units.

# ## Set non-graphical mode
#
# Set non-graphical mode.
# You can set ``non_graphical`` either to ``True`` or ``False``.
# The Boolean parameter ``new_thread`` defines whether to create a new instance
# of AEDT or try to connect to an existing instance of it.

# ## Launch AEDT and Circuit
#
# Launch AEDT and Circuit. The [pyaedt.Desktop](
# https://aedt.docs.pyansys.com/version/stable/API/_autosummary/pyaedt.desktop.Desktop.html#pyaedt.desktop.Desktop)
# class initializes AEDT and starts the specified version in the specified mode.

# +
desktop_version = AEDT_VERSION
non_graphical = False
new_thread = True
temp_dir = tempfile.TemporaryDirectory(suffix=".ansys", ignore_cleanup_errors=True)

circuit = pyaedt.Circuit(
    project=os.path.join(temp_dir.name, "CircuitExample"),
    design="Simple",
    version=desktop_version,
    non_graphical=non_graphical,
    new_desktop=new_thread,
)

circuit.modeler.schematic.schematic_units = "mil"
# -

# ## Create circuit setup
#
# Create and customize an linear network analysis (LNA) setup.

setup1 = circuit.create_setup("MyLNA")
setup1.props["SweepDefinition"]["Data"] = "LINC 0GHz 4GHz 10001"

# ## Place Components
#
# Place components such as an inductor, resistor, and capacitor. The ``location`` argument
# provides the ``[x, y]`` coordinates to place the component.

inductor = circuit.modeler.schematic.create_inductor(name="L1", value=1e-9, location=[0, 0])
resistor = circuit.modeler.schematic.create_resistor(name="R1", value=50, location=[500, 0])
capacitor = circuit.modeler.schematic.create_capacitor(name="C1", value=1e-12, location=[1000, 0])

#  ## Get all pins
#
# The component pins are instances of the class
# ``pyaedt.modeler.circuits.objct3dcircuit.CircuitPins`` and
# provide access to the
# pin location, net connectivity and the method ``connect_to_component()`` which
# can be used to connect components in the schematic
# as will be demonstrated in
# this example.

# ## Place a Port and Ground
#
# Place a port and a ground in the schematic.

port = circuit.modeler.components.create_interface_port(name="myport", location=[-300, 50])
gnd = circuit.modeler.components.create_gnd(location=[1200, -100])

# ## Connect components
#
# Connect components with wires in the schematic. The ``connect_to_component()``
# method is used to create connections between pins.

port.pins[0].connect_to_component(assignment=inductor.pins[0], use_wire=True)
inductor.pins[1].connect_to_component(assignment=resistor.pins[1], use_wire=True)
resistor.pins[0].connect_to_component(assignment=capacitor.pins[0], use_wire=True)
capacitor.pins[1].connect_to_component(assignment=gnd.pins[0], use_wire=True)

# ## Create transient setup
#
# Create a transient setup.

setup2 = circuit.create_setup(name="MyTransient", setup_type=circuit.SETUPS.NexximTransient)
setup2.props["TransientData"] = ["0.01ns", "200ns"]
setup3 = circuit.create_setup(name="MyDC", setup_type=circuit.SETUPS.NexximDC)

# ## Solve transient setup
#
# Solve the transient setup.

circuit.analyze_setup("MyLNA")
circuit.export_fullwave_spice()

# ## Create report
#
# Display the scattering parameters.

solutions = circuit.post.get_solution_data(
    expressions=circuit.get_traces_for_plot(category="S"),
)
solutions.enable_pandas_output = True
real, imag = solutions.full_matrix_real_imag
print(real)

# ## Plot data
#
# Create a plot based on solution data.

fig = solutions.plot()

# ## Close AEDT
#
# After the simulation completes, you can close AEDT or release it using the
# `pyaedt.Desktop.force_close_desktop` method.
# All methods provide for saving the project before closing.

circuit.save_project()
print("Project Saved in {}".format(circuit.project_path))

circuit.release_desktop()
time.sleep(3)

temp_dir.cleanup()  # Remove project folder and temporary files.
