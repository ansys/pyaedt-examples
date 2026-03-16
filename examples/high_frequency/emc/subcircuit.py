# # Schematic subcircuit management
#
# This example shows how to add a subcircuit to a circuit design.
# It changes the focus within the hierarchy between
# the child subcircuit and the parent design.
#
# Keywords: **Circuit**, **EMC**, **schematic**.

# ## Prerequisites
#
# ### Perform imports

# +
import os
import tempfile
import time

import ansys.aedt.core
# -

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ### Launch Circuit
#
# Launch AEDT in graphical mode. Instantite an instance of the ``Circuit`` class.

circuit = ansys.aedt.core.Circuit(
    project=os.path.join(temp_folder.name, "SubcircuitExampl.aedt"),
    design="SimpleExample",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)
circuit.modeler.schematic_units = "mil"

# ## Add subcircuit
#
# Add a new subcircuit to the previously created circuit design, creating a
# child circuit. Push this child circuit down into the child subcircuit.

subcircuit = circuit.modeler.schematic.create_subcircuit(location=[0.0, 0.0])
subcircuit_name = subcircuit.composed_name
circuit.push_down(subcircuit)

# ## Parametrize subcircuit
#
# Parametrize the subcircuit and add a resistor, inductor, and a capacitor with
# parameter values. Components are connected in series,
# and the focus is changed to the parent schematic using
# the ``pop_up()`` method.

circuit.variable_manager.set_variable(name="R_val", expression="35ohm")
circuit.variable_manager.set_variable(name="L_val", expression="1e-7H")
circuit.variable_manager.set_variable(name="C_val", expression="5e-10F")
p1 = circuit.modeler.schematic.create_interface_port(name="In")
r1 = circuit.modeler.schematic.create_resistor(value="R_val")
l1 = circuit.modeler.schematic.create_inductor(value="L_val")
c1 = circuit.modeler.schematic.create_capacitor(value="C_val")
p2 = circuit.modeler.schematic.create_interface_port(name="Out")
circuit.modeler.schematic.connect_components_in_series(
    assignment=[p1, r1, l1, c1, p2], use_wire=True
)
circuit.pop_up()

# ## Finish
#
# ### Save the project

circuit.save_project()
circuit.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
