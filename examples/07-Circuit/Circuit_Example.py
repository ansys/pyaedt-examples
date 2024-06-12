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

from ansys.pyaedt.examples.constants import AEDT_VERSION
import pyaedt

# -

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
temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")

desktop = pyaedt.launch_desktop(desktop_version, non_graphical, new_thread)
aedt_app = pyaedt.Circuit(
    projectname=os.path.join(temp_dir.name, "CircuitExample"), designname="Simple"
)
aedt_app.modeler.schematic.schematic_units = "mil"
# -

# ## Create circuit setup
#
# Create and customize an linear network analysis (LNA) setup.

setup1 = aedt_app.create_setup("MyLNA")
setup1.props["SweepDefinition"]["Data"] = "LINC 0GHz 4GHz 10001"

# ## Place Components
#
# Place components such as an inductor, resistor, and capacitor. The ``location`` argument
# provides the ``[x, y]`` coordinates to place the component.

inductor = aedt_app.modeler.schematic.create_inductor(name="L1", value=1e-9, location=[0, 0])
resistor = aedt_app.modeler.schematic.create_resistor(name="R1", value=50, location=[500, 0])
capacitor = aedt_app.modeler.schematic.create_capacitor(name="C1", value=1e-12, location=[1000, 0])

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

port = aedt_app.modeler.components.create_interface_port(name="myport", location=[-300, 50])
gnd = aedt_app.modeler.components.create_gnd(location=[1200, -100])

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

setup2 = aedt_app.create_setup(name="MyTransient", setup_type=aedt_app.SETUPS.NexximTransient)
setup2.props["TransientData"] = ["0.01ns", "200ns"]
setup3 = aedt_app.create_setup(name="MyDC", setup_type=aedt_app.SETUPS.NexximDC)

# ## Solve transient setup
#
# Solve the transient setup.

aedt_app.analyze_setup("MyLNA")
aedt_app.export_fullwave_spice()

# ## Create report
#
# Display the scattering parameters.

solutions = aedt_app.post.get_solution_data(
    expressions=aedt_app.get_traces_for_plot(category="S"),
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

desktop.release_desktop()

time.sleep(3)
temp_dir.cleanup()  # Remove project data and temporary working directory.
