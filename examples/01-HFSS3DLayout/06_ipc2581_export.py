# # HFSS 3D Layout: IPC2581 export
#
# This example shows how to use the electronics database (EDB) to export an IPC2581 file.

# ## Preparation
# Import the required packages

import os
import tempfile
import time

from pyaedt import Edb
from pyaedt.downloads import download_file

# Specify the version of Electronics Destkop to use for this example.

EDB_VERSION = "2024.1"

# Download the example PCB data.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
aedb = download_file(source="edb/ANSYS-HSD_V1.aedb", destination=temp_folder.name)

# ## Launch EDB

edbapp = Edb(edbpath=aedb, edbversion=EDB_VERSION)

# ## Create a cutout
# The following assignments will define the region of the PCB to be cut out for analysis.

edbapp.cutout(
    signal_list=["PCIe_Gen4_TX1_N", "PCIe_Gen4_TX1_P"],
    reference_list=["GND"],
    extent_type="ConvexHull",
    expansion_size=0.002,
    use_round_corner=False,
    number_of_threads=4,
    remove_single_pin_components=True,
    use_pyaedt_extent_computing=True,
    extent_defeature=0,
)
edbapp.nets.plot(None, None, color_by_net=True)

# ## Export layout as a IPC2581 file.

edbapp.export_to_ipc2581(
    ipc_path=os.path.join(temp_folder.name, "ANSYS-HSD_V1.xml"), units="inch"
)

# ## Close EDB and clean up the temporary directory
#
# All project files are saved in the folder ``temp_file.dir``.
# If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell removes
# all temporary files, including the project folder.

edbapp.close_edb()
time.sleep(
    3
)  # Allow Electronics desktop to shut down before deleting the project files.
temp_folder.cleanup()
