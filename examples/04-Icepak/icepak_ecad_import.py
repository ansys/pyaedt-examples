# # Icepak: Importing a PCB and its components via IDF and EDB

# This example shows how to import a PCB and its components using IDF files (*.ldb/*.bdf).
# The *.emn/*.emp combination can also be used in a similar way.

# ## Perform required imports
#
# Perform required imports including the operating system, Ansys PyAEDT packages.

import os
import tempfile
import pyaedt
from pyaedt import Hfss3dLayout

# Set constant values

AEDT_VERSION = "2024.1"
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Open project
#
# Open an empty project in non-graphical mode, using a temporary folder.

# +
temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

ipk = pyaedt.Icepak(
    project=os.path.join(temp_folder.name, "Icepak_ECAD_Import.aedt"),
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
)
# -

# ## Import the IDF files
#
# Sample *.bdf and *.ldf files are presented here.
#
# <img src="_static\bdf.png" width="400">
#
# <img src="_static\ldf.png" width="400">
#
# Imports the idf files with several filtering options including caps, resistors,
# inductors, power, specific power, size...
# There are also options for the PCB creation (number o flayers, copper percentages, layer sizes).
# In this example, the default values are used for the PCB.
# The imported PCB (from IDF) here will be deleted later and replaced by a PCB that has the trace
# information (from ECAD) for higher accuracy.

# Download ECAD and IDF files

def_path = pyaedt.downloads.download_file(
    source="icepak/Icepak_ECAD_Import/A1_uprev.aedb", name="edb.def", destination=temp_folder.name
)
board_path = pyaedt.downloads.download_file(
    source="icepak/Icepak_ECAD_Import/", name="A1.bdf", destination=temp_folder.name
)
library_path = pyaedt.downloads.download_file(
    source="icepak/Icepak_ECAD_Import/", name="A1.ldf", destination=temp_folder.name
)

# Import IDF

ipk.import_idf(board_path=board_path)

# Save the project

ipk.save_project()

# ## Import ECAD
# Add an HFSS 3D Layout design with the layout information of the PCB

hfss3d_lo = Hfss3dLayout(project=def_path)
hfss3d_lo.save_project()

# Create a PCB component in Icepak linked to the 3D Layout project. The polygon ``"poly_0"``
# is used as the outline of the PCB and a dissipation of ``"1W"`` is applied to the PCB.

ipk.create_pcb_from_3dlayout(
    component_name="PCB_pyAEDT",
    project_name=hfss3d_lo.project_file,
    design_name=hfss3d_lo.design_name,
    extenttype="Polygon",
    outlinepolygon="poly_0",
    power_in=1,
)

# Delete the simplified PCB object coming from IDF import.

ipk.modeler["IDF_BoardOutline"].delete()

# ## Plot model

ipk.plot(
    show=False,
    export_path=os.path.join(temp_folder.name, "ECAD_import.jpg"),
    plot_air_objects=False,
    force_opacity_value=1,
)

# ## Release AEDT

ipk.release_desktop(close_projects=True, close_desktop=True)

# ## Cleanup
#
# All project files are saved in the folder ``temp_dir.name``. If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
