# # Import of a PCB and its components via IDF and EDB

# This example shows how to import a PCB and its components using IDF files (LDB and BDF).
# You can also use a combination of EMN and EMP files in a similar way.
#
# Keywords: **Icepak**, **PCB**, **IDF**.

# ## Perform imports and define constants
#
# Perform required imports.

import os
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core import Hfss3dLayout, Icepak

# Define constants.

AEDT_VERSION = "2024.2"
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Open project
#
# Open an empty project in non-graphical mode, using a temporary folder.

# +
temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

ipk = Icepak(
    project=os.path.join(temp_folder.name, "Icepak_ECAD_Import.aedt"),
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
)
# -

# ## Import the IDF files
#
# Import the BDF and LDF files. Sample files are shown here.
#
# <img src="_static\bdf.png" width="400">
#
# <img src="_static\ldf.png" width="400">
#
# You can import the IDF files with several filtering options, including caps, resistors,
# inductors, power, specific power, and size.
# There are also options for PCB creation, including number of layers, copper percentages, and layer sizes.
#
# This example uses the default values for the PCB.
# The imported PCB (from the IDF files) are deleted later and replaced by a PCB that has the trace
# information (from ECAD) for higher accuracy.

# Download ECAD and IDF files.

def_path = ansys.aedt.core.downloads.download_file(
    source="icepak/Icepak_ECAD_Import/A1_uprev.aedb",
    name="edb.def",
    destination=temp_folder.name,
)
board_path = ansys.aedt.core.downloads.download_file(
    source="icepak/Icepak_ECAD_Import/", name="A1.bdf", destination=temp_folder.name
)
library_path = ansys.aedt.core.downloads.download_file(
    source="icepak/Icepak_ECAD_Import/", name="A1.ldf", destination=temp_folder.name
)

# Import IDF file.

ipk.import_idf(board_path=board_path)

# Save the project

ipk.save_project()

# ## Import ECAD
# Add an HFSS 3D Layout design with the layout information of the PCB.

hfss3d_lo = Hfss3dLayout(project=def_path, version=AEDT_VERSION)
hfss3d_lo.save_project()

# Create a PCB component in Icepak linked to the HFSS 3D Layout project. The polygon ``"poly_0"``
# is used as the outline of the PCB, and a dissipation of ``"1W"`` is applied to the PCB.

project_file = hfss3d_lo.project_file
design_name = hfss3d_lo.design_name

ipk.create_pcb_from_3dlayout(
    component_name="PCB_pyAEDT",
    project_name=project_file,
    design_name=design_name,
    extent_type="Polygon",
    outline_polygon="poly_0",
    power_in=1,
)

# Delete the simplified PCB object coming from the IDF import.

ipk.modeler.delete_objects_containing("IDF_BoardOutline", False)

# ## Release AEDT

ipk.save_project()
ipk.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
