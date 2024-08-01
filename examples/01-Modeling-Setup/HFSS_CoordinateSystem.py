# # General: coordinate system creation
#
# This example shows how you can use PyAEDT to create and modify coordinate systems in the modeler.
#
# ## Preparation
# Import the required packages

import tempfile
import time
import pyaedt
import os

# Define constants

AEDT_VERSION = "2024.1"
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT

d = pyaedt.launch_desktop(version=AEDT_VERSION, non_graphical=NG_MODE, new_desktop=True)

# ## Insert HFSS design
#
# Insert an HFSS design with the default name.

project_name = os.path.join(temp_dir.name, "CoordSysDemo.aedt")
hfss = pyaedt.Hfss(project=project_name)

# ## Create coordinate system
#
# The coordinate system is centered on the global origin and has the axis
# aligned to the global coordinate system. The new coordinate system is
# saved in the object ``cs1``.

cs1 = hfss.modeler.create_coordinate_system()

# ## Modify coordinate system
#
# The ``cs1`` object exposes properties and methods to manipulate the
# coordinate system. The origin can be changed.

cs1["OriginX"] = 10
cs1.props["OriginY"] = 10
cs1.props["OriginZ"] = 10

# The orientation of the coordinate system can be modified by
# updating the direction vectors for the coordinate system.

ypoint = [0, -1, 0]
cs1.props["YAxisXvec"] = ypoint[0]
cs1.props["YAxisYvec"] = ypoint[1]
cs1.props["YAxisZvec"] = ypoint[2]

# ## Rename coordinate system
#
# Rename the coordinate system.

cs1.rename("newCS")

# ## Change coordinate system mode
#
# Use the ``change_cs_mode`` method to change the mode. Options are
# - ``0`` for axis/position
# - ``1`` for Euler angle ZXZ
# - ``2`` for Euler angle ZYZ.
#
# Here ``1`` sets Euler angle ZXZ as the mode.

cs1.change_cs_mode(1)

# The following lines use the ZXZ Euler angle definition to rotate the coordinate system.

cs1.props["Phi"] = "10deg"
cs1.props["Theta"] = "22deg"
cs1.props["Psi"] = "30deg"

# ## Delete coordinate system
#
# Delete the coordinate system.

cs1.delete()

# ## Define a new coordinate system
#
# Create a coordinate system by defining the axes. You can
# specify all coordinate system properties as shown here.

cs2 = hfss.modeler.create_coordinate_system(
    name="CS2",
    origin=[1, 2, 3.5],
    mode="axis",
    x_pointing=[1, 0, 1],
    y_pointing=[0, -1, 0],
)

# A new coordinate system can also be created based on the Euler angle convention.

cs3 = hfss.modeler.create_coordinate_system(
    name="CS3", origin=[2, 2, 2], mode="zyz", phi=10, theta=20, psi=30
)

# Create a coordinate system that is defined by standard views in the modeler. The options are 
# - ``"iso"``
# - ``"XY"``
# - ``"XZ"``
# - ``"XY"``.
#
# Here ``"iso"`` is specified. The axes are set automatically.

cs4 = hfss.modeler.create_coordinate_system(
    name="CS4", origin=[1, 0, 0], reference_cs="CS3", mode="view", view="iso"
)

# ## Create coordinate system by defining axis and angle rotation
#
# Create a coordinate system by defining the axis and angle rotation. When you
# specify the axis and angle rotation, this data is automatically translated
# to Euler angles.

cs5 = hfss.modeler.create_coordinate_system(
    name="CS5", mode="axisrotation", u=[1, 0, 0], theta=123
)

# Face coordinate systems are bound to an object face.
# First create a box and then define the face coordinate system on one of its
# faces. To create the reference face for the face coordinate system, you must
# specify starting and ending points for the axis.

box = hfss.modeler.create_box([0, 0, 0], [2, 2, 2])
face = box.faces[0]
fcs1 = hfss.modeler.create_face_coordinate_system(
    face=face, origin=face.edges[0], axis_position=face.edges[1], name="FCS1"
)

# Create a face coordinate system centered on the face with the X axis pointing
# to the edge vertex.

fcs2 = hfss.modeler.create_face_coordinate_system(
    face=face, origin=face, axis_position=face.edges[0].vertices[0], name="FCS2"
)

# Swap the X axis and Y axis of the face coordinate system. The X axis is the
# pointing ``axis_position`` by default. You can optionally select the Y axis.

fcs3 = hfss.modeler.create_face_coordinate_system(
    face=face, origin=face, axis_position=face.edges[0], axis="Y"
)

# The face coordinate system can also be rotated by changing the
# reference axis.

fcs3.props["WhichAxis"] = "X"


# ### Rotate the coordinate system
#
# Apply a rotation around the Z axis. The Z axis of a face coordinate system
# is always orthogonal to the face. A rotation can be applied at definition.
# Rotation is expressed in degrees.

fcs4 = hfss.modeler.create_face_coordinate_system(
    face=face, origin=face, axis_position=face.edges[1], rotation=10.3
)

# Rotation can also be changed after coordinate system creation

fcs4.props["ZRotationAngle"] = "3deg"

# ### Offset the coordinate system
#
# Apply an offset to the X axis and Y axis of a face coordinate system.
# The offset is in respect to the face coordinate system itself.

fcs5 = hfss.modeler.create_face_coordinate_system(
    face=face, origin=face, axis_position=face.edges[2], offset=[0.5, 0.3]
)

# The offset can be changed after the coordinate system has been created.

fcs5.props["XOffset"] = "0.2mm"
fcs5.props["YOffset"] = "0.1mm"

# ### Dependent coordinate systems
#
# The use of dependent coordinate systems can simplify model creation. The following
# cell demonstrates how to create a coordinate system whose reference is the face coordinate system.

face = box.faces[1]
fcs6 = hfss.modeler.create_face_coordinate_system(
    face=face, origin=face, axis_position=face.edges[0]
)
cs_fcs = hfss.modeler.create_coordinate_system(
    name="CS_FCS", origin=[0, 0, 0], reference_cs=fcs6.name, mode="view", view="iso"
)

# ### Object coordinate systems
#
# A coordinate system can also be defined relative to elements
# belonging to an object. For example, the coordinate system can be
# connected to an object face.

obj_cs = hfss.modeler.create_object_coordinate_system(
    assignment=box,
    origin=box.faces[0],
    x_axis=box.edges[0],
    y_axis=[0, 0, 0],
    name="box_obj_cs",
)
obj_cs.rename("new_obj_cs")

# Create an object coordinate system whose origin is linked to the edge of an object.

obj_cs_1 = hfss.modeler.create_object_coordinate_system(
    assignment=box.name,
    origin=box.edges[0],
    x_axis=[1, 0, 0],
    y_axis=[0, 1, 0],
    name="obj_cs_1",
)
obj_cs_1.set_as_working_cs()

# Create object coordinate system with origin specified on a point within an object.

obj_cs_2 = hfss.modeler.create_object_coordinate_system(
    assignment=box.name,
    origin=[0, 0.8, 0],
    x_axis=[1, 0, 0],
    y_axis=[0, 1, 0],
    name="obj_cs_2",
)
new_obj_cs_2 = hfss.modeler.duplicate_coordinate_system_to_global(obj_cs_2)
obj_cs_2.delete()

# Create object coordinate system with origin on vertex.

obj_cs_3 = hfss.modeler.create_object_coordinate_system(
    obj=box.name,
    origin=box.vertices[1],
    x_axis=box.faces[2],
    y_axis=box.faces[4],
    name="obj_cs_3",
)
obj_cs_3.props["MoveToEnd"] = False
obj_cs_3.update()

# ### Get all coordinate systems
#
# All coordinate systems can easily be retrieved and subsequently manipulated.

css = hfss.modeler.coordinate_systems
names = [i.name for i in css]
print(names)

# ## Select coordinate system
#
# Select an existing coordinate system.

css = hfss.modeler.coordinate_systems
cs_selected = css[0]
cs_selected.delete()

# ## Get point coordinate under another coordinate system
#
# Get a point coordinate under another coordinate system. A point coordinate
# can be translated in respect to any coordinate system.

hfss.modeler.create_box([-10, -10, -10], [20, 20, 20], "Box1")
p = hfss.modeler["Box1"].faces[0].vertices[0].position
print("Global: ", p)
p2 = hfss.modeler.global_to_cs(p, "CS5")
print("CS5 :", p2)

# ## Release AEDT
# Close the project and release AEDT.

d.release_desktop()
time.sleep(3)

# ## Cleanup
#
# All project files are saved in the folder ``temp_dir.name``. If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_dir.cleanup()
