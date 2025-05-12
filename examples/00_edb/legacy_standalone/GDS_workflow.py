# # EDB: Importing other types of files
#
# This example demonstrates how to import different types of files and translate their information to an EDB file.

# Perform imports.

# +
import os
import tempfile
from pyedb.dotnet.edb import Edb
from pyedb.misc.downloads import download_file
from ansys.aedt.core.hfss3dlayout import  Hfss3dLayout
# -

# ## Case 1: Import a .gds file.
#
# Download the test case folder and copy it to a temporary folder.
# The following files are used in this example:
#
# - _sky130_fictious_dtc_exmple_contol_no_map.xml_
#   defines physical information such
#   as material properties, stackup layers, and boundary conditions.
# - _dummy_layermap.map_
#   maps properties to stackup layers.

# +
temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
control_fn = "XML_Automation.xml"
gds_fn = "Model.gds"
layer_map = "Model.map"

local_path = download_file("gds_file", destination=temp_dir.name)
my_control_file = os.path.join(local_path, control_fn)
my_map_file = os.path.join(local_path, layer_map)
gds_in = os.path.join(local_path, gds_fn)
# -

# ## Open EDB
#
# Import the gds and open the edb. Each gds is followed either by a control file (*.xml) or a technology file (*.ircx, *.vlc.tech, or *.itf).
# Then a map file (*.map) is also regularly used to map the stackup layers, and finally in some cases a layer filter (*.xml) is deployed, when
# only a part of the stackup is needed.

# +
# Select EDB version (change it manually if needed, e.g. "2025.1")
version = "2025.1"
print(f"EDB version: {version}")

edb = Edb(gds_in, edbversion=version, control_file=my_control_file,map_file = my_map_file)

# ## Save and Close EDB
#
# Close the project.

edb1_path = os.path.join(temp_dir.name, "gds_design.aedb")

edb.save_as(edb1_path)

edb.close_edb()

# ## Close EDB

# ## Case 2: Import a .brd file (or any other compatible format: *.dxf, *.zip, *.sml (IPC2581), *.mcm, *.sip and *.tgz).
# Download the test case folder and copy it to the temporary folder.
# The following files are used in this example:
# - Galileo.brd
#   board file that contains all the information of the design that is translated in EDB.

local_path = download_file("brd", destination=temp_dir.name)
brd_file = "BeagleBone Black_PCB_RevC_No Logo_210401.brd"
my_brd_file = os.path.join(local_path, brd_file)


# ## Open EDB
#
# Directly import the .brd file as an Edb object (the same version as before is used).

edb = Edb(my_brd_file, edbversion=version)

# ## Save and Close EDB
#
# Close the project.

edb2_path = os.path.join(temp_dir.name, "brd_design.aedb")

edb.save_as(edb2_path)

edb.close_edb()

# ## Open both EDB files with HFSS 3D Layout, and observe the designs.

h3d_gds = Hfss3dLayout(project=edb1_path,version=version,new_desktop=True)

h3d_brd = Hfss3dLayout(project=edb2_path,version=version,new_desktop=True)

# ## Successfully close the HFSS 3D Layout designs and release the dekstop.

h3d_gds.release_desktop()

h3d_brd.release_desktop()

# Clean up the temporary folder.

temp_dir.cleanup()
