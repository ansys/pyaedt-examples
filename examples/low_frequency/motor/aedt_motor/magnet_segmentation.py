# # Magnet segmentation

# This example shows how to use PyAEDT to segment magnets of an electric motor.
# The method is valid and usable for any object you would like to segment.
#
# Keywords: **Maxwell 3D**, **Magnet segmentation**.

# ## Perform imports and define constants
#
# Perform required imports.

# +
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_file
# -

# Define constants.

AEDT_VERSION = "2025.1"
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download AEDT file example
#
# Set the local temporary folder to export the AEDT file to.

aedt_file = download_file(
    source="object_segmentation",
    name="Motor3D_obj_segments.aedt",
    local_path=temp_folder.name,
)

# ## Launch Maxwell 3D
#
# Launch Maxwell 3D, providing the version, rgw path to the project, and the graphical mode.

m3d = ansys.aedt.core.Maxwell3d(
    project=aedt_file,
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
)

# ## Segment first magnet by specifying number of segments
#
# Select the first magnet to segment by specifying the number of segments.
# The method accepts as input the list of magnets names to segment,
# magnet IDs, or the magnet :class:`ansys.aedt.core.modeler.cad.object3d.Object3d` object.
# When ``apply_mesh_sheets`` is enabled, the mesh sheets are also
# applied in the geometry.
# In the following code, the name of the magnet is also given as an input.

segments_number = 2
object_name = "PM_I1"
sheets_1 = m3d.modeler.objects_segmentation(
    object_name,
    segments=segments_number,
    apply_mesh_sheets=True,
    mesh_sheets=3,
)

# ## Segment second magnet by specifying number of segments
#
# Select the second magnet to segment by specifying the number of segments.
# The following code gives the ID of the magnet as an input.

segments_number = 2
object_name = "PM_I1_1"
magnet_id = [obj.id for obj in m3d.modeler.object_list if obj.name == object_name][0]
sheets_2 = m3d.modeler.objects_segmentation(
    magnet_id, segments=segments_number, apply_mesh_sheets=True
)

# ## Segment third magnet by specifying segmentation thickness
#
# Select the third magnet to segment by specifying the segmentation thickness.
# The following code gives the magnet object type `ansys.aedt.core.modeler.cad.object3d.Object3d`
# as an input.

segmentation_thickness = 1
object_name = "PM_O1"
magnet = [obj for obj in m3d.modeler.object_list if obj.name == object_name][0]
sheets_3 = m3d.modeler.objects_segmentation(
    magnet, segmentation_thickness=segmentation_thickness, apply_mesh_sheets=True
)

# ## Segment fourth magnet by specifying number of segments
#
# Select the fourth magnet to segment by specifying the number of segments.
# The following code gives the name of the magnet as input and disables the mesh sheets.

object_name = "PM_O1_1"
segments_number = 2
sheets_4 = m3d.modeler.objects_segmentation(object_name, segments=segments_number)

# ## Release AEDT

m3d.save_project()
m3d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
