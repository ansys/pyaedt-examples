# # Magnet segmentation

# This example shows how you can use PyAEDT to segment magnets of an electric motor.
# The method is valid and usable for any object the user would like to segment.
#
# Keywords: **Maxwell 3D**, **Magnet segmentation**.

# ## Perform required imports
#
# Perform required imports.

import os
import tempfile
import time

from ansys.aedt.core import Maxwell3d, downloads

# ## Define constants

AEDT_VERSION = "2024.2"
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory
#
# Create temporary directory.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download .aedt file example
#
# Set local temporary folder to export the .aedt file to.

aedt_file = downloads.download_file(
    source="object_segmentation",
    name="Motor3D_obj_segments.aedt",
    destination=temp_folder.name,
)

# ## Launch Maxwell 3D
#
# Launch Maxwell 3D, providing the version, path to the project and the graphical mode.

m3d = Maxwell3d(
    project=aedt_file,
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
)

# ## Segment first magnet by specifying the number of segments
#
# Select first magnet to segment by specifying the number of segments.
# The method accepts in input either the list of magnets names to segment or
# magnets ids or the magnet object :class:`ansys.aedt.core.modeler.cad.object3d.Object3d`.
# ``apply_mesh_sheets`` is enabled which means that the mesh sheets will
# be applied in the geometry too.
# In this specific case we give as input the name of the magnet.

segments_number = 2
object_name = "PM_I1"
sheets_1 = m3d.modeler.objects_segmentation(
    object_name,
    segments=segments_number,
    apply_mesh_sheets=True,
    mesh_sheets=3,
)

# ## Segment second magnet by specifying the number of segments
#
# Select second magnet to segment by specifying the number of segments.
# In this specific case we give as input the id of the magnet.

segments_number = 2
object_name = "PM_I1_1"
magnet_id = [obj.id for obj in m3d.modeler.object_list if obj.name == object_name][0]
sheets_2 = m3d.modeler.objects_segmentation(
    magnet_id, segments=segments_number, apply_mesh_sheets=True
)

# ## Segment third magnet by specifying the segmentation thickness
#
# Select third magnet to segment by specifying the segmentation thickness.
# In this specific case we give as input the magnet object
# of type `ansys.aedt.core.modeler.cad.object3d.Object3d`.

segmentation_thickness = 1
object_name = "PM_O1"
magnet = [obj for obj in m3d.modeler.object_list if obj.name == object_name][0]
sheets_3 = m3d.modeler.objects_segmentation(
    magnet, segmentation_thickness=segmentation_thickness, apply_mesh_sheets=True
)

# ## Segment fourth magnet by specifying the number of segments
#
# Select fourth magnet to segment by specifying the number of segments.
# In this specific case we give as input the name of the magnet and we disable the mesh sheets.

object_name = "PM_O1_1"
segments_number = 2
sheets_4 = m3d.modeler.objects_segmentation(object_name, segments=segments_number)

# ## Plot model

model = m3d.plot(show=False)
model.plot(os.path.join(temp_folder.name, "Image.jpg"))

# ## Release AEDT

m3d.save_project()
m3d.release_desktop()
# Wait 3 seconds to allow Electronics Desktop to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Cleanup
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
