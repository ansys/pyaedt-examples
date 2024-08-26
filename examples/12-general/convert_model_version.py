# # Encrypted 3D Component ACIS-to-Parasolid
#
# This example shows how to convert an encrypted
# 3D component from different AEDT releases.
# This is useful if you have models previous to 2023R1 with ACIS kernel and you need to convert it to Parasolid.
#
# Keywords: **HFSS**, **Encrypted**, **3D Component**, **Modeler kernel**.

# <img src="_static/e3dcomp.png" width="500">

# ## Perform required imports
#
# Perform required imports.
#

import os
import tempfile
import time

from pyaedt import Desktop, Hfss, settings
from pyedb.misc.downloads import download_file

# Define constants.

AEDT_VERSION = "2024.2"
OLD_AEDT_VERSION = "2024.1"
NUM_CORES = 4
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# Download the example encrypted 3D component

a3dcomp = download_file(
    directory="component_3d",
    filename="SMA_Edge_Connector_23r2_encrypted_password_ansys.a3dcomp",
    destination=temp_folder.name,
)

# Enable multiple desktop support

settings.use_multi_desktop = True

# ## Prepare encrypted 3D component in ACIS
#
# Launch old AEDT release

aedt_old = Desktop(new_desktop_session=True, specified_version=OLD_AEDT_VERSION)

# Insert an empty HFSS design

hfss1 = Hfss(aedt_process_id=aedt_old.aedt_process_id, solution_type="Terminal")

# Insert the encrypted 3D component

cmp = hfss1.modeler.insert_3d_component(comp_file=a3dcomp, password="ansys")

# Open 3D component in a HFSS design

app_comp = cmp.edit_definition(password="ansys")

# ## Create a new encrypted 3D component in Parasolid
#
# Launch new AEDT release

aedt = Desktop(new_desktop_session=True, specified_version=AEDT_VERSION)

# Insert an empty HFSS design

hfss2 = Hfss(aedt_process_id=aedt.aedt_process_id, solution_type="Terminal")

# Copy objects from old design

hfss2.copy_solid_bodies_from(design=app_comp, no_vacuum=False, no_pec=False)

# Create a new encrypted 3D component

hfss2.modeler.create_3dcomponent(
    component_file=os.path.join(
        temp_folder.name, r"SMA_Edge_Connector_encrypted.a3dcomp"
    ),
    is_encrypted=True,
    edit_password="ansys",
    hide_contents=False,
    allow_edit=True,
    password_type="InternalPassword",
)

# ## Release AEDT

aedt.save_project()
aedt_old.save_project()
aedt.release_desktop()
aedt_old.release_desktop()
# Wait 3 seconds to allow Electronics Desktop to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Cleanup
#
# All project files are saved in the folder ``temp_dir.name``.
# If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
