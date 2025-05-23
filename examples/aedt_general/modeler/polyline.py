# # Polyline creation
#
# This example shows how to use PyAEDT to create and manipulate polylines.
#
# Keywords: **AEDT**, **modeler**, **polyline**.

# ## Import packages and define constants
# Import the required packages.

# +
import os
import tempfile
import time

import ansys.aedt.core
# -

# Define constants

AEDT_VERSION = "2025.1"
NG_MODE = False  # Open AEDT UI when it is launched.


# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Create Maxwell 3D object
#
# Create a `Maxwell3d` object and set the unit type to ``"mm"``.

project_name = os.path.join(temp_folder.name, "polyline.aedt")
maxwell = ansys.aedt.core.Maxwell3d(
    project=project_name,
    solution_type="Transient",
    design="test_polyline_3D",
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
)
maxwell.modeler.model_units = "mm"
modeler = maxwell.modeler

# ## Define variables
#
# Define two design variables as parameters for the polyline objects.

maxwell["p1"] = "100mm"
maxwell["p2"] = "71mm"

# ## Input data
#
# Input data. All data for the polyline functions can be entered as either floating point
# values or strings. Floating point values are assumed to be in model units
# (``maxwell.modeler.model_units``).

test_points = [
    ["0mm", "p1", "0mm"],
    ["-p1", "0mm", "0mm"],
    ["-p1/2", "-p1/2", "0mm"],
    ["0mm", "0mm", "0mm"],
]

# ## Create polyline primitives
#
# The following examples are for creating polyline primitives.

# ### Create line primitive
#
# Create a line primitive. The basic polyline command takes a list of positions
# (``[X, Y, Z]`` coordinates) and creates a polyline object with one or more
# segments. The supported segment types are ``Line``, ``Arc`` (3 points),
# ``AngularArc`` (center-point + angle), and ``Spline``.

line1 = modeler.create_polyline(points=test_points[0:2], name="PL01_line")
print("Created Polyline with name: {}".format(modeler.objects[line1.id].name))
print("Segment types : {}".format([s.type for s in line1.segment_types]))
print("primitive id = {}".format(line1.id))

# ### Create arc primitive
#
# Create an arc primitive. The ``position_list`` parameter must contain at
# least three position values. The first three position values are used.

line2 = modeler.create_polyline(
    points=test_points[0:3], segment_type="Arc", name="PL02_arc"
)
print(
    "Created object with id {} and name {}.".format(
        line2.id, modeler.objects[line2.id].name
    )
)

# ### Create spline primitive
#
# Create a spline primitive. Defining the segment using a ``PolylineSegment``
# object allows you to provide additional input parameters for the spine, such
# as the number of points (in this case 4). The ``points`` parameter
# must contain at least four position values.

line3 = modeler.create_polyline(
    points=test_points,
    segment_type=modeler.polyline_segment("Spline", num_points=4),
    name="PL03_spline_4pt",
)

# ### Create center-point arc primitive
#
# Create a center-point arc primitive. A center-point arc segment is defined
# by a starting point, a center point, and an angle of rotation around the
# center point. The rotation occurs in a plane parallel to the XY, YZ, or ZX
# plane of the active coordinate system. The starting point and the center point
# must therefore have one coordinate value (X, Y, or Z) with the same value.
#
# In this first code example, ``start-point`` and ``center-point`` have a common
# Z position, ``"0mm"``. The curve therefore lies in the XY plane at $ z = 0 $.

start_point = [100, 100, 0]
center_point = [0, 0, 0]
line4 = modeler.create_polyline(
    points=[start_point],
    segment_type=modeler.polyline_segment(
        "AngularArc", arc_center=center_point, arc_angle="30deg"
    ),
    name="PL04_center_point_arc",
)

# In this second code example, ``start_point`` and ``center_point`` have the same
# values for the Y and Z coordinates, so the plane or rotation could be either XY or ZX.
# For these special cases when the rotation plane is ambiguous, you can specify
# the plane explicitly.

start_point = [100, 0, 0]
center_point = [0, 0, 0]
line4_xy = modeler.create_polyline(
    points=[start_point],
    segment_type=modeler.polyline_segment(
        "AngularArc", arc_center=center_point, arc_angle="30deg", arc_plane="XY"
    ),
    name="PL04_center_point_arc_rot_XY",
)
line4_zx = modeler.create_polyline(
    points=[start_point],
    segment_type=modeler.polyline_segment(
        "AngularArc", arc_center=center_point, arc_angle="30deg", arc_plane="ZX"
    ),
    name="PL04_center_point_arc_rot_ZX",
)

# ## Create compound polylines
#
# You can pass a list of points to the ``create_polyline()`` method to create a multi-segment
# polyline.
#
# If the type of segment is not specified, all points
# are connected by straight line segments.

line6 = modeler.create_polyline(points=test_points, name="PL06_segmented_compound_line")

# You can specify the segment type as an optional named argument to
# define the segment type used to connect the points.

line5 = modeler.create_polyline(
    points=test_points, segment_type=["Line", "Arc"], name="PL05_compound_line_arc"
)

# Setting the named argument ``close_surface=True`` ensures
# that the polyline starting point and
# ending point are the same. You can also explicitly close the
# polyline by setting the last point equal
# to the first point in the list of points.

line7 = modeler.create_polyline(
    points=test_points, close_surface=True, name="PL07_segmented_compound_line_closed"
)

# Setting the named argument ``cover_surface=True`` also
# covers the polyline and creates a sheet object.

line_cover = modeler.create_polyline(
    points=test_points, cover_surface=True, name="SPL01_segmented_compound_line"
)

# ## Insert compound lines
#
# The following examples are for inserting compound lines.
#
# ### Insert line segment
#
# Insert a line segment starting at vertex 1 ``["100mm", "0mm", "0mm"]``
# of an existing polyline and ending at some new point ``["90mm", "20mm", "0mm"].``
# By numerical comparison of the starting point with the existing vertices of the
# original polyline object, it is determined automatically that the segment is
# inserted after the first segment of the original polyline.

line8_segment = modeler.create_polyline(
    points=test_points,
    close_surface=True,
    name="PL08_segmented_compound_insert_segment",
)
points_line8_segment = line8_segment.points[1]
insert_point = ["-100mm", "20mm", "0mm"]
line8_segment.insert_segment(points=[insert_point, points_line8_segment])

# ### Insert compound line with insert curve
#
# Insert a compound line starting a line segment at vertex 1 ``["100mm", "0mm", "0mm"]``
# of an existing polyline and ending at some new point ``["90mm", "20mm", "0mm"]``.
# By numerical comparison of the starting point, it is determined automatically
# that the segment is inserted after the first segment of the original polyline.

# +
line8_segment_arc = modeler.create_polyline(
    points=test_points, close_surface=False, name="PL08_segmented_compound_insert_arc"
)

start_point = line8_segment_arc.vertex_positions[1]
insert_point1 = ["90mm", "20mm", "0mm"]
insert_point2 = [40, 40, 0]

line8_segment_arc.insert_segment(
    points=[start_point, insert_point1, insert_point2], segment="Arc"
)
# -

# ### Insert compound line at end of a center-point arc
#
# Insert a compound line at the end of a center-point arc (``type="AngularArc"``).
# This is a special case.
#
# Step 1: Draw a center-point arc.

# +
start_point = [2200.0, 0.0, 1200.0]
arc_center_1 = [1400, 0, 800]
arc_angle_1 = "43.47deg"

line_arc = modeler.create_polyline(
    name="First_Arc",
    points=[start_point],
    segment_type=modeler.polyline_segment(
        type="AngularArc", arc_angle=arc_angle_1, arc_center=arc_center_1
    ),
)
# -

# Step 2: Insert a line segment at the end of the arc with a specified end point.

start_of_line_segment = line_arc.end_point
end_of_line_segment = [3600, 200, 30]
line_arc.insert_segment(points=[start_of_line_segment, end_of_line_segment])

# Step 3: Append a center-point arc segment to the line object.

arc_angle_2 = "39.716deg"
arc_center_2 = [3400, 200, 3800]
line_arc.insert_segment(
    points=[end_of_line_segment],
    segment=modeler.polyline_segment(
        type="AngularArc", arc_center=arc_center_2, arc_angle=arc_angle_2
    ),
)

# You can use the compound polyline definition to complete all three steps in
# a single step.

modeler.create_polyline(
    points=[start_point, end_of_line_segment],
    segment_type=[
        modeler.polyline_segment(
            type="AngularArc", arc_angle="43.47deg", arc_center=arc_center_1
        ),
        modeler.polyline_segment(type="Line"),
        modeler.polyline_segment(
            type="AngularArc", arc_angle=arc_angle_2, arc_center=arc_center_2
        ),
    ],
    name="Compound_Polyline_One_Command",
)

# ## Insert two 3-point arcs forming a circle
#
# Insert two 3-point arcs forming a circle.
# Note that the last point of the second arc segment is not defined in
# the position list.

line_three_points = modeler.create_polyline(
    points=[
        [34.1004, 14.1248, 0],
        [27.646, 16.7984, 0],
        [24.9725, 10.3439, 0],
        [31.4269, 7.6704, 0],
    ],
    segment_type=["Arc", "Arc"],
    cover_surface=True,
    close_surface=True,
    name="line_covered",
    material="vacuum",
)

# Here is an example of a complex polyline where the number of points is
# insufficient to populate the requested segments. This results in an
# ``IndexError`` that PyAEDT catches silently. The return value of the command
# is ``False``, which can be caught at the app level.  While this example might
# not be so useful in a Jupyter Notebook, it is important for unit tests.

line_points = [
    ["67.1332mm", "2.9901mm", "0mm"],
    ["65.9357mm", "2.9116mm", "0mm"],
    ["65.9839mm", "1.4562mm", "0mm"],
    ["66mm", "0mm", "0mm"],
    ["99mm", "0mm", "0mm"],
    ["98.788mm", "6.4749mm", "0mm"],
    ["98.153mm", "12.9221mm", "0mm"],
    ["97.0977mm", "19.3139mm", "0mm"],
]


line_segments = ["Line", "Arc", "Line", "Arc", "Line"]
line_complex1 = modeler.create_polyline(
    points=line_points, segment_type=line_segments, name="Polyline_example"
)

# Here is an example that provides more points than the segment list requires.
# This is valid usage. The remaining points are ignored.

line_segments = ["Line", "Arc", "Line", "Arc"]
line_complex2 = modeler.create_polyline(
    line_points, segment_type=line_segments, name="Polyline_example2"
)

# ## Save project
#
# Save the project.

maxwell.save_project()
maxwell.release_desktop()
time.sleep(3)  # Allow AEDT to shut down before cleaning the temporary project folder.

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes
# all temporary files, including the project folder.

temp_folder.cleanup()
