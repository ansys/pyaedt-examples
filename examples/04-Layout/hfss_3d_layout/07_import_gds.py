# # Import GDS
#
# This example demonstrates how to import a gds layout for subsequent simulation with HFSS.
# - Create control file
#   - Add HFSS analysis setups
#   - Create via group
#   - Add ports
#   - Add components
# - Import layout as EDB
#     -  Plot stackup
#
# Keywords: **HFSS 3D Layout**, **GDS**.

# ## Preparation
# Import the required packages

# +
import os
import tempfile

from ansys.aedt.core.downloads import download_file
from pyedb import Edb
from pyedb.dotnet.edb_core.edb_data.control_file import ControlFile

# -

# Set constant values

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory
#
# Create temporary directory.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

control_fn = download_file(
    source="gds",
    name="sky130_fictitious_dtc_example_control_no_map.xml",
    destination=temp_folder.name,
)
gds_fn = download_file(
    source="gds", name="sky130_fictitious_dtc_example.gds", destination=temp_folder.name
)
layer_map = download_file(
    source="gds", name="dummy_layermap.map", destination=temp_folder.name
)

# -

# ## Control file
#
# A Control file is an xml file which purpose if to provide additional information during
# import phase. It can include, materials, stackup, setup, boundaries and settings.
# In this example we will import an existing xml, integrate it with a layer mapping file of gds
# and then adding setup and boundaries.

c = ControlFile(xml_input=control_fn, layer_map=layer_map)

# ## Set up simulation
#
# This code sets up a simulation with HFSS and adds a frequency sweep.

setup = c.setups.add_setup("Setup1", "1GHz")
setup.add_sweep("Sweep1", "0.01GHz", "5GHz", "0.1GHz")

# ## Provide additional stackup settings
#
# After import, you can change the stackup settings and add or remove layers or materials.

c.stackup.units = "um"
c.stackup.dielectrics_base_elevation = -100
c.stackup.metal_layer_snapping_tolerance = "10nm"
for via in c.stackup.vias:
    via.create_via_group = True
    via.snap_via_group = True

# ## Define boundary settings
#
# Boundaries can include ports, components and boundary extent.

c.boundaries.units = "um"
c.boundaries.add_port(
    "P1", x1=223.7, y1=222.6, layer1="Metal6", x2=223.7, y2=100, layer2="Metal6"
)
c.boundaries.add_extent()
comp = c.components.add_component("B1", "BGA", "IC", "Flip chip", "Cylinder")
comp.solder_diameter = "65um"
comp.add_pin("1", "81.28", "84.6", "met2")
comp.add_pin("2", "211.28", "84.6", "met2")
comp.add_pin("3", "211.28", "214.6", "met2")
comp.add_pin("4", "81.28", "214.6", "met2")
c.import_options.import_dummy_nets = True

# ## Write XML file
#
# After all settings are ready, you can write an XML file.

c.write_xml(os.path.join(temp_folder.name, "output.xml"))

# ## Open EDB
#
# Import the gds and open the edb.

# +

edbapp = Edb(
    gds_fn,
    edbversion=AEDT_VERSION,
    technology_file=os.path.join(temp_folder.name, "output.xml"),
)
# -

# ## Plot stackup
#
# Plot the stackup.

edbapp.stackup.plot(first_layer="met1")

# ## Close EDB
#
# Close the project.

edbapp.close_edb()

# Clean up the temporary folder.

temp_folder.cleanup()
