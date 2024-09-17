# # Import an ECAD into Icepak and modify stackup properties

# This example shows how to import an ECAD as a PCB component into Icepak.
# It will also demonstrate how to change the materials of the PCB layers and
# update the PCB in Icepak.
#
# Keywords: **Icepak**, **PCB**

# ## Perform required imports
# Perform required imports including the operating system, Ansys PyAEDT packages.

import os
import time
import tempfile

import ansys.aedt.core

# Define constants

AEDT_VERSION = "2024.2"
NG_MODE = False     # Open AEDT user interface when False

# ## Create temporary directory
#
# Open an empty project in graphical mode, using a temporary directory.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")


# ## Launch Icepak and open project
#
# Launch HFSS and open the project

# +
project_name = "Icepak_ECAD_Import"
project_path = os.path.join(temp_folder.name, f"{project_name}.aedt")
ipk = ansys.aedt.core.Icepak(
    project=project_name,
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
)

print(f"Project name: {project_name}")

# Disable autosave
ipk.autosave_disable()

# Save Icepak project
ipk.save_project()
# -

# ## Download the ECAD file
# Download the ECAD file needed to run the example.

ecad_path = ansys.aedt.core.downloads.download_file(
    source="edb/ANSYS-HSD_V1.aedb",
    name="edb.def",
    destination=temp_folder.name,
)

# ## Import ECAD 
# Add an HFSS 3D Layout design with the layout information of the PCB.
h3d_design_name = "PCB_TEMP"
h3d = ansys.aedt.core.Hfss3dLayout(
    project=project_name, 
    design=h3d_design_name, 
    version=AEDT_VERSION,
)
# Import EDB file
h3d.import_edb(ecad_path)

# Save 3D Layout project
h3d.save_project()

# Delete the empty placeholder HFSS 3D layout design 
ipk.delete_design(name=h3d_design_name, fallback_design=None)

# Set component name, ECAD source name and ECAD project path to be linked to Icepak
component_name = "PCB_ECAD"
layout_name = h3d.design_name
ecad_source = os.path.join(h3d.project_path, f"{h3d.project_name}.aedt")

# ## Create PCB component in Icepak
# Create a PCB component in Icepak linked to the 3D Layout project. 
# Polygon ``"poly_5949"`` is used as the outline of the PCB and 
# a dissipation of ``"1W"`` is applied to the PCB.

pcb_comp = ipk.create_pcb_from_3dlayout(
    component_name=component_name, 
    project_name=ecad_source,
    design_name=layout_name,
    resolution=3,
    extent_type="Polygon",
    outline_polygon="poly_5949",
    power_in=1,
)

# Save project
ipk.save_project()

# ## Modify PCB stackup 
# Initialize PyEDB object to modify ECAD
edb = ansys.aedt.core.Edb(edbpath=ecad_path, edbversion=AEDT_VERSION)

# Change dielectric fill in signal layers
for name, layer in edb.stackup.signal_layers.items():
    layer.dielectric_fill = "FR4_epoxy"

# Change material of dielectric layers
for name, layer in edb.stackup.dielectric_layers.items():
    layer.material = "FR4_epoxy"

# Save EDB
edb.save_edb()

# Close edb session
edb.close_edb()

# Update layers of PCB with new materials in PCB component
pcb_comp.update()

# ## Modify PCB materials in Icepak
# Change properties of PCB component such as board cutout material and via fill material
pcb_comp.board_cutout_material = "FR4_epoxy"
pcb_comp.via_holes_material = "FR4_epoxy"

# Modify the power specified on PCB
pcb_comp.power = "2W"

# Print path of the linked ECAD source defintion
print(pcb_comp.native_properties["DefnLink"]["Project"])

# ## Save project and release desktop
ipk.save_project()
ipk.release_desktop()

# Wait 3 seconds to allow Electronics Desktop to shut down 
# before cleaning the temporary directory.
time.sleep(3)

# ## Cleanup
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
