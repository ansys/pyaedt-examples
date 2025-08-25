# # GDS Import
#
# Integrated circuit layout data is defined in GDS data which specifies the layout
# geometry. Additionally, layer mapping and layer material information is defined in a
# technology file.
#
# This example demonstrates how to import GDS files and translate GDS data
# into an EDB file along with some simplified technology data
# for subsequent use in HFSS 3D Layout.
#
# Keywords: **GDS**, **RFIC**

# ## Prerequisites
#
# ### Perform imports

import os
import tempfile
from pyedb.dotnet.edb import Edb
from pyedb.misc.downloads import download_file
from ansys.aedt.core.hfss3dlayout import  Hfss3dLayout

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.2"
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ### Import a GDS file.
#
# Download the test case folder and copy it to the working directory. The 
# method ``download_file()`` retrieves example data from the 
# [Ansys GitHub "example_data" repository](https://github.com/ansys/example-data/tree/main/pyaedt).
#
# The following files are used in this example:
#
# - ``Model.xml`` defines physical information such
#   as material properties, stackup layer names, and boundary conditions.
# - ``Model.gds`` contains the GDS data for the layout.
# - ``Model.map`` maps properties to stackup layers.

# +
control_fn = "Model.xml"
gds_fn = "Model.gds"
layer_map = "Model.map"

local_path = download_file("gds", destination=temp_folder.name)
control_file = os.path.join(local_path, control_fn)
map_file = os.path.join(local_path, layer_map)
gds_in = os.path.join(local_path, gds_fn)
# -

# ### Open the EDB
#
# Each GDS file requires a control file (XML) or a technology file (IRCX, VLC.TECH, or ITF)
# that maps the GDS geometry to a physical layer in the stackup.
# The MAP file is also regularly used to map the stackup layers, and finally in some cases a layer filter (XML) is deployed, when
# only a part of the stackup is needed.
#
# Open the EDB by creating an instance of the ``Edb`` class.

edb = Edb(gds_in, edbversion=AEDT_VERSION, control_file=control_file, map_file=map_file)

# ### View the layer stackup

edb.stackup.plot()

# ### Save and close the EDB
#
# The GDS file has been converted to an EDB and is ready for subsequent processing either in the
# 3D Layout UI of Electronics Desktop or using 
# PyEDB. 
# The following commands save and close the EDB. 

edb_path = os.path.join(temp_folder.name, "gds_design.aedb")
edb.save_as(edb_path)
edb.close()

# ## View the layout
# ### Open the EDB in Electronics Desktop
#
# The following command opens the EDB in Electronics Desktop. If you're running this example locally, you should see something like this:
#
# <img src="_static/layout.png" width="800">

h3d = Hfss3dLayout(project=edb_path, version=AEDT_VERSION, new_desktop=NG_MODE)

# ### Close the HFSS 3D Layout 
# The following command releases Ansys Electronics Desktop and closes the project.

h3d.release_desktop()

# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
