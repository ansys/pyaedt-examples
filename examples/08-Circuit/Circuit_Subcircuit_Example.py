# # Schematic subcircuit management
#
# This example shows how to add a subcircuit to a circuit design.
# In this example, the focus is changed within the hierarchy between
# the child subcircuit and the parent design.
#
# Keywords: **Circuit**, **Schematic**.

# ## Imports
#
# Perform the required import.

import os
import tempfile
import time

import ansys.aedt.core

# Set constant values

AEDT_VERSION = "2024.2"
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory

temp_dir = tempfile.TemporaryDirectory(suffix="_ansys")

# ## Launch AEDT with Circuit
#
# Launch AEDT in graphical mode. Instantite an instance of the ``Circuit`` class.

circuit = ansys.aedt.core.Circuit(
    project=os.path.join(temp_dir.name, "SubcircuitExampl.aedt"),
    design="SimpleExample",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
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

# ## Release AEDT
#
# Release AEDT and close the example.

circuit.save_project()
circuit.release_desktop()
# Wait 5 seconds to allow Electronics Desktop to shut down before cleaning the temporary directory.
time.sleep(5)

# ## Cleanup
#
# All project files are saved in the folder ``temp_dir.name``. If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_dir.cleanup()
