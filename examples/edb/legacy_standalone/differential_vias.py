# # Coplanar Waveguide with Via Array
#
# This example demonstrates how a coplanar waveguide with via array can be created using the EDB Python
# interface.
#
# <img src="_static/cpw_via_array.png" width="500">
#
# Keywords: **coplanar waveguide, via array**


# ## Prerequisites
#
# ### Perform imports

import os
import tempfile
import pyedb

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.2"
NG_MODE = False  # Open AEDT UI when it is launched.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ### Start the EDB

# +
aedb_path = os.path.join(temp_folder.name, "cpw_via_array.aedb")
print(f"AEDB file path: {aedb_path}")

edb = pyedb.Edb(edbpath=aedb_path, edbversion=AEDT_VERSION)
# -

# ## Model Creation
#
# ### Add stackup layers
#
# A stackup can be created layer by layer or imported from a 
# [configuration file](https://examples.aedt.docs.pyansys.com/version/dev/examples/edb/use_configuration/import_stackup.html).

edb.stackup.add_layer("GND")
edb.stackup.add_layer("Diel", "GND", layer_type="dielectric", thickness="0.5mm", material="FR4_epoxy")
edb.stackup.add_layer("TOP", "Diel", thickness="0.05mm")

# ### Create signal nets and ground planes
# Create a signal net and ground planes.

points = [[0.0, 0], [100e-3, 0.0]]
trace = edb.modeler.create_trace(points, "TOP", width=1e-3, end_cap_style="Flat", start_cap_style="Flat")
points = [[0.0, 1e-3], [0.0, 10e-3], [100e-3, 10e-3], [100e-3, 1e-3], [0.0, 1e-3]]
edb.modeler.create_polygon(points, "TOP")
points = [[0.0, -1e-3], [0.0, -10e-3], [100e-3, -10e-3], [100e-3, -1e-3], [0.0, -1e-3]]
edb.modeler.create_polygon(points, "TOP")
points = [[0.0, -10e-3], [0, 10e-3], [100e-3, 10e-3], [100e-3, -10e-3]]
edb.modeler.create_polygon(points, "GND")

# ## Create wave ports on the main trace's ends.

edb.hfss.create_wave_port(prim_id = trace.id, point_on_edge = ["-10mm","10mm"], port_name="wport1")

edb.hfss.create_wave_port(prim_id = trace.id, point_on_edge = ["100mm","0mm"], port_name="wport2")

# ## Place vias

edb.padstacks.create("MyVia")
edb.padstacks.place([5e-3, 5e-3], "MyVia")
edb.padstacks.place([15e-3, 5e-3], "MyVia")
edb.padstacks.place([25e-3, 5e-3], "MyVia")
edb.padstacks.place([35e-3, 5e-3], "MyVia")
edb.padstacks.place([45e-3, 5e-3], "MyVia")
edb.padstacks.place([55e-3, 5e-3], "MyVia")
edb.padstacks.place([65e-3, 5e-3], "MyVia")
edb.padstacks.place([75e-3, 5e-3], "MyVia")
edb.padstacks.place([85e-3, 5e-3], "MyVia")
edb.padstacks.place([95e-3, 5e-3], "MyVia")
edb.padstacks.place([5e-3, -5e-3], "MyVia")
edb.padstacks.place([15e-3, -5e-3], "MyVia")
edb.padstacks.place([25e-3, -5e-3], "MyVia")
edb.padstacks.place([35e-3, -5e-3], "MyVia")
edb.padstacks.place([45e-3, -5e-3], "MyVia")
edb.padstacks.place([55e-3, -5e-3], "MyVia")
edb.padstacks.place([65e-3, -5e-3], "MyVia")
edb.padstacks.place([75e-3, -5e-3], "MyVia")
edb.padstacks.place([85e-3, -5e-3], "MyVia")
edb.padstacks.place([95e-3, -5e-3], "MyVia")

# ### Create simulation setup

setup = edb.create_hfss_setup(name= "Setup1")
setup.set_solution_single_frequency("1GHz", max_num_passes=1, max_delta_s="0.02")
setup.add_sweep(name="Sweep1")


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
