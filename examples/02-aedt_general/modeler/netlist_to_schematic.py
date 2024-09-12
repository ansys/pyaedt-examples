# # Circuit Netlist to Schematic
#
# This example shows how to create components
# in the circuit schematic editor from a netlist file.
#
# Note that HSPICE files are fully supported and that broad coverage is provided for many other formats.
#
# Keywords: **Circuit**, **netlist**.

# ## Perform imports and define constants
#
# Perform required imports and set paths.

# +
import os
import tempfile
import time

import ansys.aedt.core

# -

# ## Define constants.

AEDT_VERSION = "2024.2"
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT with Circuit
#
# Launch AEDT with Circuit. The `ansys.aedt.core.Desktop` class initializes AEDT
# and starts it on the specified version in the specified graphical mode.

netlist = ansys.aedt.core.downloads.download_netlist(destination=temp_folder.name)
circuit = ansys.aedt.core.Circuit(
    project=os.path.join(temp_folder.name, "NetlistExample"),
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Define a parameter
#
# Specify the voltage as a parameter.

circuit["Voltage"] = "5"

# ## Create schematic from netlist file
#
# Create a schematic from a netlist file. The ``create_schematic_from_netlist()``
# method reads the netlist file and parses it. All components are parsed,
# but only these categories are mapped: R, L, C, Q, U, J, V, and I.

circuit.create_schematic_from_netlist(netlist)

# ## Release AEDT
#
# Release AEDT and close the example.

circuit.save_project()
circuit.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``. If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
