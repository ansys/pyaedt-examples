# # IPC2581 export
#
# This example shows how to use the electronics database (EDB) to export an IPC2581 file.
#
# Keywords: **HFSS 3D Layout**, **IPC2581**.

# ## Preparation
# Import the required packages

import os
import tempfile
import time

from ansys.aedt.core import Edb
from ansys.aedt.core.downloads import download_file

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open Electronics UI when the application is launched.


# Download the example PCB data.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
aedb = download_file(source="edb/ANSYS-HSD_V1.aedb", destination=temp_folder.name)

# ## Launch EDB

edbapp = Edb(edbpath=aedb, edbversion=AEDT_VERSION)

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

# ## Close EDB

edbapp.close_edb()

# ## Clean up the temporary directory

time.sleep(3)
temp_folder.cleanup()
