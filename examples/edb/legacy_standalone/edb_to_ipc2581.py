# # EDB: IPC2581 export
#
# This example shows how you can use PyAEDT to export an IPC2581 file.
#
# Perform required imports, which includes importing a section.

# +
import os
import tempfile
import time

import pyedb
from pyedb.generic.general_methods import generate_unique_name
from pyedb.misc.downloads import download_file

# -

# ## Download the AEDB file and copy it in the temporary folder.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
targetfile = download_file("pyaedt/edb/ANSYS-HSD_V1.aedb", destination=temp_dir.name)
ipc2581_file_name = os.path.join(temp_dir.name, "Ansys_Hsd.xml")
print(targetfile)

# ## Launch EDB
#
# Launch the `pyedb.Edb` class, using EDB 2023.
# > Note that length dimensions passed to EDB are in SI units.

# +
# Select EDB version (change it manually if needed, e.g. "2025.1")
AEDT_VERSION = "2026.1"

edb = pyedb.Edb(edbpath=targetfile, version=edb_version)
# -

# ## Parametrize the width of a trace.

edb.modeler.parametrize_trace_width("A0_N", parameter_name=generate_unique_name("Par"), variable_value="0.4321mm")

# ## Create a cutout and plot it.

signal_list = []
for net in edb.nets.netlist:
    if "PCIe" in net:
        signal_list.append(net)
power_list = ["GND"]
edb.cutout(
    signal_nets=signal_list,
    reference_nets=power_list,
    extent_type="ConvexHull",
    expansion_size=0.002,
    use_round_corner=False,
    number_of_threads=4,
    remove_single_pin_components=True,
    use_pyaedt_extent_computing=True,
    extent_defeature=0,
)
edb.nets.plot(None, None, color_by_net=True)

# ## Export the EDB to an IPC2581 file.

edb.export_to_ipc2581(ipc_path=ipc2581_file_name)
print("IPC2581 File has been saved to {}".format(ipc2581_file_name))

# ## Close EDB

edb.close()

# Wait 3 seconds before cleaning the temporary directory.
time.sleep(3)

# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_dir.cleanup()
