# # Circuit: schematic subcircuit management
#
# This example shows how to add a subcircuit to a circuit design.
# In this example, the focus is changed within the hierarchy between
# the child subcircuit and the parent design.

# ## Imports
#
# Perform the required import.

import os
import tempfile
import time

import pyaedt

# Set constant values

AEDT_VERSION = "2024.2"

# ## Set non-graphical mode
#
# Set non-graphical mode.
# You can set ``non_graphical`` either to ``True`` or ``False``.

# ## Launch AEDT with Circuit
#
# Launch AEDT in graphical mode. Instantite an instance of the ``Circuit`` class.

non_graphical = False
temp_dir = tempfile.TemporaryDirectory(suffix=".ansys", ignore_cleanup_errors=True)
circuit = pyaedt.Circuit(
    project=os.path.join(temp_dir.name, "SubcircuitExample"),
    design="SimpleExample",
    version=AEDT_VERSION,
    non_graphical=non_graphical,
    new_desktop=True,
)
circuit.modeler.schematic_units = "mil"

# ## Add Subcircuit
#
# Add a new subcircuit to the previously created circuit design, creating a
# child circuit. Push this child circuit down into the child subcircuit.

subcircuit = circuit.modeler.schematic.create_subcircuit(location=[0.0, 0.0])
subcircuit_name = subcircuit.composed_name
circuit.push_down(subcircuit)

# ## Parametrization
#
# Parametrize the subcircuit and add a resistor, inductor, and a capacitor with
# the parameter values. Components are connected in series
# and the focus is changed to the parent schematic using
# the ``pop_up`` method.

circuit.variable_manager.set_variable(variable_name="R_val", expression="35ohm")
circuit.variable_manager.set_variable(variable_name="L_val", expression="1e-7H")
circuit.variable_manager.set_variable(variable_name="C_val", expression="5e-10F")
p1 = circuit.modeler.schematic.create_interface_port(name="In")
r1 = circuit.modeler.schematic.create_resistor(value="R_val")
l1 = circuit.modeler.schematic.create_inductor(value="L_val")
c1 = circuit.modeler.schematic.create_capacitor(value="C_val")
p2 = circuit.modeler.schematic.create_interface_port(name="Out")
circuit.modeler.schematic.connect_components_in_series(
    components_to_connect=[p1, r1, l1, c1, p2], use_wire=True
)
circuit.pop_up()


# ## Done
#
# Release AEDT and clean up the temporary files. If you run this example locally and
# want to keep the files, the project folder name can be retrieved from ``temp_file.name``.

circuit.save_project()
print("Project Saved in {}".format(circuit.project_path))

circuit.release_desktop()
time.sleep(3)

temp_dir.cleanup()  # Remove project folder and temporary files.
