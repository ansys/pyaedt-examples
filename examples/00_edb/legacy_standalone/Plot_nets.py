# # EDB: plot nets with Matplotlib
#
# This example shows how to use the ``Edb`` class to view nets, layers and
# via geometry directly in Python. The methods demonstrated in this example
# rely on
# [matplotlib](https://matplotlib.org/cheatsheets/_images/cheatsheets-1.png).

# ## Perform required imports
#
# Perform required imports, which includes importing a section.

# +
import tempfile

import pyedb
from pyedb.misc.downloads import download_file
# -

# ## Download the EDB and copy it into the temporary folder.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
targetfolder = download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_dir.name)

# ## Create an instance of the Electronics Database using the `pyedb.Edb` class.
#
# > Note that units are SI.

# +
# Select EDB version (change it manually if needed, e.g. "2025.1")
edb_version = "2025.1"
print(f"EDB version: {edb_version}")

edb = pyedb.Edb(edbpath=targetfolder, edbversion=edb_version)
# -

# Display the nets on a layer. You can display the net geometry directly in Python using
# ``matplotlib`` from the ``pyedb.Edb`` class.

edb.nets.plot("AVCC_1V3")

# You can view multiple nets by passing a list containing the net
# names to the ``plot()`` method.

edb.nets.plot(["GND", "GND_DP", "AVCC_1V3"], color_by_net=True)

# You can display all copper on a single layer by passing ``None``
# as the first argument. The second argument is a list
# of layers to plot. In this case, only one
# layer is to be displayed.

edb.nets.plot(None, ["1_Top"], color_by_net=True, plot_components_on_top=True)

# Display a side view of the layers and padstack geometry using the
# ``Edb.stackup.plot()`` method.

edb.stackup.plot(scale_elevation=False, plot_definitions=["c100hn140", "c35"])

# ## Creating coaxial port on component U1 and all ddr4_dqs nets
# Selecting all nets from ddr4_dqs and component U1 and create coaxial ports
# On corresponding pins.

comp_u1 = edb.components.instances["U1"]
signal_nets = [net for net in comp_u1.nets if "ddr4_dqs" in net.lower()]
edb.hfss.create_coax_port_on_component("U1", net_list=signal_nets)
edb.components.set_solder_ball(component="U1", sball_diam="0.3mm", sball_height="0.3mm")

# ## Renaming all ports
# Renaming all port with _renamed string as suffix example.

for port_name, port in edb.ports.items():
    port.name = f"{port_name}_renamed"


# Close the EDB.

edb.close_edb()

# Remove all files and the temporary directory.

temp_dir.cleanup()
