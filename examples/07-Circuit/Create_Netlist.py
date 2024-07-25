# # Circuit Netlist to Schematic
#
# This example shows how to create components
# in the circuit schematic editor from a netlist file.
#
# Note that HSPICE files are fully supported and many other formats enjoy broad coverage.

# ## Imports
#
# Perform required imports and set paths.

import os
import tempfile
import time

import pyaedt

# ## Setup
#
# Create a temporary working folder and download the project data.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
netlist = pyaedt.downloads.download_netlist(destination=temp_dir.name)

# Set constant values

AEDT_VERSION = "2024.1"
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Launch AEDT
#
# Launch AEDT in graphical mode.
# > _Note that this example uses SI units._

# ## Launch AEDT with Circuit
#
# Launch AEDT with Circuit. The `pyaedt.Desktop` class initializes AEDT
# and starts it on the specified version in the specified graphical mode.

circuit = pyaedt.Circuit(
    project=os.path.join(temp_dir.name, "NetlistExample"),
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Define a Parameter
#
# Specify the voltage as a parameter.

circuit["Voltage"] = "5"

# ## Create schematic from netlist file
#
# Create a schematic from a netlist file. The ``create_schematic_from_netlist``
# method reads the netlist file and parses it. All components are parsed
# but only these categories are mapped: R, L, C, Q, U, J, V, and I.

schematic = circuit.create_schematic_from_netlist(netlist)

# ## Finish
#
# After adding any other desired functionalities, close the project and release
# AEDT.


circuit.save_project()
print("Project Saved in {}".format(circuit.project_path))
circuit.release_desktop()
time.sleep(3)

# ## Cleanup
#
# All project files are saved in the folder ``temp_dir.name``.
# If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell removes
# all temporary files, including the project folder.

temp_dir.cleanup()  # Remove project folder and temporary files.
