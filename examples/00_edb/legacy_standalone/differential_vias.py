# # Parametric differential vias
#
# This example demonstrates how a differential via pair can be created using the EDB Python
# interface.
#
# The final differential via pair is shown below.
#
# <img src="_static/diff_via.png" width="500">
#
# Keywords: **Differential Via**


# ## Prerequisites
#
# ### Perform imports

import os
import tempfile
import pyedb

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.1"
NG_MODE = False  # Open AEDT UI when it is launched.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ### Start the EDB

# +
aedb_path = os.path.join(temp_folder.name, "diff_via.aedb")
print(f"AEDB file path: {aedb_path}")

edb = pyedb.Edb(edbpath=aedb_path, edbversion=AEDT_VERSION)
# -

# ## Model Creation
#
# ### Add stackup layers
#
# A stackup can be created layer by layer or imported from a 
# [configuration file](https://examples.aedt.docs.pyansys.com/version/dev/examples/00_edb/use_configuration/import_stackup.html).

edb.stackup.add_layer("GND")
edb.stackup.add_layer("Diel", "GND", layer_type="dielectric", thickness="0.1mm", material="FR4_epoxy")
edb.stackup.add_layer("TOP", "Diel", thickness="0.05mm")

# ### Create signal nets and ground planes
# Create a signal net and ground planes.

points = [[0.0, 0], [100e-3, 0.0]]
edb.modeler.create_trace(points, "TOP", width=1e-3)
points = [[0.0, 1e-3], [0.0, 10e-3], [100e-3, 10e-3], [100e-3, 1e-3], [0.0, 1e-3]]
edb.modeler.create_polygon(points, "GND")
points = [[0.0, -1e-3], [0.0, -10e-3], [100e-3, -10e-3], [100e-3, -1e-3], [0.0, -1e-3]]
edb.modeler.create_polygon(points, "GND")


# ## Place vias

edb.padstacks.create("MyVia")
edb.padstacks.place([5e-3, 5e-3], "MyVia")
edb.padstacks.place([15e-3, 5e-3], "MyVia")
edb.padstacks.place([35e-3, 5e-3], "MyVia")
edb.padstacks.place([45e-3, 5e-3], "MyVia")
edb.padstacks.place([5e-3, -5e-3], "MyVia")
edb.padstacks.place([15e-3, -5e-3], "MyVia")
edb.padstacks.place([35e-3, -5e-3], "MyVia")
edb.padstacks.place([45e-3, -5e-3], "MyVia")


# ### View the nets

edb.nets.plot(None, color_by_net=True)

# ### View the stackup

edb.stackup.plot(plot_definitions="MyVia")

# ## Finish
#
# ### Save the project
# Save and close EDB.

if edb:
    edb.save_edb()
    edb.close_edb()
print("EDB saved correctly to {}. You can import in AEDT.".format(aedb_path))

# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
