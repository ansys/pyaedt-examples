# # EDB: Importing GDS file
#
# This example demonstrates how to import GDS files and translate their information to an EDB file.

# Perform imports.

# +
import os
import tempfile
from pyedb.dotnet.edb import Edb
from pyedb.misc.downloads import download_file
from ansys.aedt.core.hfss3dlayout import  Hfss3dLayout
# -

# ## Case 1: Import a GDS file.
#
# Download the test case folder and copy it to a temporary folder.
# The following files are used in this example:
#
# - XML_Automation.xml
#   defines physical information such
#   as material properties, stackup layers, and boundary conditions.
# - Model.map
#   maps properties to stackup layers.

# +
temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
control_fn = "Model.xml"
gds_fn = "Model.gds"
layer_map = "Model.map"

local_path = download_file("gds", destination=temp_dir.name)
my_control_file = os.path.join(local_path, control_fn)
my_map_file = os.path.join(local_path, layer_map)
gds_in = os.path.join(local_path, gds_fn)
# -

# ## Open EDB
#
# Import the gds and open the edb. Each gds is followed either by a control file (XML) or a technology file (IRCX, VLC.TECH, or ITF).
# Then a MAP file is also regularly used to map the stackup layers, and finally in some cases a layer filter (XML) is deployed, when
# only a part of the stackup is needed.

# +
# Select EDB version (change it manually if needed, e.g. "2025.1")
version = "2025.1"
print(f"EDB version: {version}")

edb = Edb(gds_in, edbversion=version, control_file=my_control_file, map_file=my_map_file)

# ## Plot stackup


edb.stackup.plot()

# ## Save and Close EDB
#
# Save the project.

edb1_path = os.path.join(temp_dir.name, "gds_design.aedb")

edb.save_as(edb1_path)

# Close the project.

edb.close_edb()

# ## Open both EDB files with HFSS 3D Layout, and observe the design / confirm the robustness from GDS to EDB.

h3d_gds = Hfss3dLayout(project=edb1_path, version=version, new_desktop=True)

# ## Close the HFSS 3D Layout design and release the dekstop.

h3d_gds.release_desktop()

# Clean up the temporary folder.

temp_dir.cleanup()
