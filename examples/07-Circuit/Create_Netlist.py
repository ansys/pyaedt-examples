# # Circuit Netlist to Schematic
#
# This example shows how to create components
# in the circuit schematic editor from a netlist file.
#
# Note that HSPICE files are fully supported and many other formats enjoy broad coverage.

# ## Imports
#
# Perform required imports and set paths.

# +
import os
import tempfile

from ansys.pyaedt.examples.constants import AEDT_VERSION
import pyaedt

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
netlist = pyaedt.downloads.download_netlist(destination=temp_dir.name)
# -

# ## Launch AEDT
#
# Launch AEDT in graphical mode. 
# > _Note that this example uses SI units._

# ## Set non-graphical mode
#
# Set non-graphical mode.
# You can set ``non_graphical`` either to ``True`` or ``False``.
# The Boolean parameter ``new_thread`` defines whether to create a new instance
# of AEDT or try to connect to an existing instance of it.

desktopVersion = AEDT_VERSION
non_graphical = False
new_thread = True

# ## Launch AEDT with Circuit
#
# Launch AEDT with Circuit. The `pyaedt.Desktop` class initializes AEDT
# and starts it on the specified version in the specified graphical mode.

desktop = pyaedt.launch_desktop(desktopVersion, non_graphical, new_thread)
aedtapp = pyaedt.Circuit(projectname=os.path.join(temp_dir.name, "NetlistExample"))

# ## Define a Parameter
#
# Specify the voltage as a parameter.

aedtapp["Voltage"] = "5"

# ## Create schematic from netlist file
#
# Create a schematic from a netlist file. The ``create_schematic_from_netlist``
# method reads the netlist file and parses it. All components are parsed
# but only these categories are mapped: R, L, C, Q, U, J, V, and I.

aedtapp.create_schematic_from_netlist(netlist)

# ## Finish
#
# After adding any other desired functionalities, close the project and release
# AEDT.

desktop.release_desktop()

temp_dir.cleanup()  # Clean up temporary directory and project data.
