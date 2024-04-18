# # HFSS: Encrypted 3D Component ACIS-to-Parasolid
#
# This example shows how to convert an encrypted
# 3D component from ACIS to Parasolid.
#
# Keywords: **HFSS**, **Encrypted**. **3D Component**

# <img src="_static/e3dcomp.png" width="500">

# ## Perform required imports
#
# Perform required imports.
#

import os
import tempfile

from pyaedt import Desktop, Hfss, settings
from pyedb.misc.downloads import download_file

# ## Set up environment

# Create temporary directory

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# Download the example encrypted 3D component

a3dcomp = download_file(
    directory="component_3d",
    filename="SMA_Edge_Connector_22r2_encrypted_password_ansys.a3dcomp",
    destination=temp_folder.name
)

# Enable multiple desktop support

settings.use_multi_desktop = True

# ## Prepare encrypted 3D component in ACIS
# Launch AEDT 2022 R2

d222 = Desktop(new_desktop_session=True, specified_version=222)

# Insert an empty HFSS design

hfss1 = Hfss(aedt_process_id=d222.aedt_process_id, solution_type="Terminal")

# Insert the encrypted 3D component

cmp = hfss1.modeler.insert_3d_component(comp_file=a3dcomp, password="ansys")

# Open 3D component in a HFSS design

app_comp = cmp.edit_definition(password="ansys")

# ## Create a new encrypted 3D component in Parasolid
# Launch AEDT 2023 R2

d232 = Desktop(new_desktop_session=True, specified_version=232)

# Insert an empty HFSS design

hfss2 = Hfss(aedt_process_id=d232.aedt_process_id, solution_type="Terminal")

# Copy objects from 2022 R2 design

hfss2.copy_solid_bodies_from(design=app_comp, no_vacuum=False, no_pec=False)

# Create a new encrypted 3D component

hfss2.modeler.create_3dcomponent(
    component_file=os.path.join(temp_folder.name, r'SMA_Edge_Connector_23r2_encrypted.a3dcomp'),
    is_encrypted=True,
    edit_password="ansys",
    hide_contents=False, allow_edit=True, password_type="InternalPassword"
)

# Release all desktops

d232.release_desktop()
d222.release_desktop()

