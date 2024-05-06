# # Icepak: Importing a PCB and its components via IDF and EDB

# This example shows how to import a PCB and its components using IDF files (*.ldb/*.bdf).
# The *.emn/*.emp combination can also be used in a similar way.

# ## Perform required imports
#
# Perform required imports including the operating system, Ansys PyAEDT packages.

# Generic Python packages

import os

from ansys.pyaedt.examples.constants import AEDT_VERSION
import pyaedt
from pyaedt import Hfss3dLayout

# PyAEDT Packages


# ## Set non-graphical mode
#
# Set non-graphical mode.
# You can set ``non_graphical`` either to ``True`` or ``False``.

non_graphical = False


# ## Download and open project
#
# Download the project, open it, and save it to the temporary folder.

# +
temp_folder = pyaedt.generate_unique_folder_name()

ipk = pyaedt.Icepak(
    projectname=os.path.join(temp_folder, "Icepak_ECAD_Import.aedt"),
    specified_version=AEDT_VERSION,
    new_desktop_session=True,
    non_graphical=non_graphical,
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
# inductors, power, size, ...
# There are also options for the PCB creation (number o flayers, copper percentages, layer sizes).
# In this example, the default values are used for the PCB.
# The imported PCB here will be deleted later and replaced by a PCB that has the trace
# information for higher accuracy.

# +
def_path = pyaedt.downloads.download_file(
    source="icepak/Icepak_ECAD_Import/A1_uprev.aedb", name="edb.def", destination=temp_folder
)
board_path = pyaedt.downloads.download_file(source="icepak/Icepak_ECAD_Import/", name="A1.bdf", destination=temp_folder)
library_path = pyaedt.downloads.download_file(
    source="icepak/Icepak_ECAD_Import/", name="A1.ldf", destination=temp_folder
)

ipk.import_idf(board_path=board_path)
# -

# ## Save the project
ipk.save_project()

# ## Import ECAD
# Add an HFSS 3D Layout design with the layout information of the PCB

hfss3d_lo = Hfss3dLayout(projectname=def_path)
hfss3d_lo.save_project()

# Create a PCB component in Icepak linked to the 3D Layout project. The poly_0 polygon is used as the outline of the PCB
# and a dissipation od "1W" is applied to the PCB.
ipk.create_pcb_from_3dlayout(
    component_name="PCB_pyAEDT",
    project_name=hfss3d_lo.project_name,
    design_name=hfss3d_lo.design_name,
    extenttype="Polygon",
    outlinepolygon="poly_0",
    power_in=1,
)

# Delete the simplified PCB object coming from IDF import.

ipk.modeler.delete_objects_containing(contained_string="IDF_BoardOutline", case_sensitive=False)

# ## Compute power budget
#

# Creates a setup to be able to calculate the power
ipk.create_setup(name="setup1")

power_budget, total_power = ipk.post.power_budget(units="W")

# Print the total power and the power_budget dictionary
print(f"The total power is {total_power}.")
print(power_budget)

# ## Release AEDT
#
# Release AEDT.

ipk.release_desktop(close_projects=True, close_desktop=True)
