# # Encrypted 3D component conversion
#
# This example shows how to convert an encrypted
# 3D component from ACIS to Parasolid in different AEDT releases.
# If you have models previous to Ansys AEDT 2023 R1 with an ACIS kernel,
# you can convert it to Parasolid.
#
# Keywords: **HFSS**, **Encrypted**, **3D component**, **Modeler kernel**.

# <img src="_static/e3dcomp.png" width="500">

# ## Perform imports and define constants
#
# Import the required packages.
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
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download encrypted example
#
# Download the encrypted 3D component example.

a3dcomp = download_file(
    directory="component_3d",
    filename="SMA_Edge_Connector_23r2_encrypted_password_ansys.a3dcomp",
    destination=temp_folder.name,
)

# ## Enable multiple desktop support

settings.use_multi_desktop = True

# ## Prepare encrypted 3D component in ACIS
#
# Launch the old AEDT release.

aedt_old = Desktop(new_desktop=True, version=OLD_AEDT_VERSION)

# Insert an empty HFSS design.

hfss1 = Hfss(aedt_process_id=aedt_old.aedt_process_id, solution_type="Terminal")

# Insert the encrypted 3D component.

cmp = hfss1.modeler.insert_3d_component(comp_file=a3dcomp, password="ansys")

# Open the 3D component in an HFSS design.

app_comp = cmp.edit_definition(password="ansys")

# ## Create an encrypted 3D component in Parasolid
#
# Launch the new AEDT release

aedt = Desktop(new_desktop_session=True, specified_version=AEDT_VERSION)

# Insert an empty HFSS design.

hfss2 = Hfss(aedt_process_id=aedt.aedt_process_id, solution_type="Terminal")

# Copy objects from the old design.

hfss2.copy_solid_bodies_from(design=app_comp, no_vacuum=False, no_pec=False)

# Create the new encrypted 3D component.

hfss2.modeler.create_3dcomponent(
    input_file=os.path.join(temp_folder.name, r"SMA_Edge_Connector_encrypted.a3dcomp"),
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
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
