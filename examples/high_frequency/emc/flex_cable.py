# # Flex cable CPWG
#
# This example shows how to use PyAEDT to create a flex cable CPWG
# (coplanar waveguide with ground).
#
# Keywords: **HFSS**, **flex cable**, **CPWG**.

# ## Perform imports and define constants
#
# Perform required imports.

# +
import os
import tempfile
from math import cos, radians, sin, sqrt

import ansys.aedt.core
from ansys.aedt.core.generic.file_utils import generate_unique_name
# -

# Define constants.

AEDT_VERSION = "2025.1"

# ## Set non-graphical mode
#
# Set non-graphical mode.
# You can set ``non_graphical`` either to ``True`` or ``False``.

non_graphical = False

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT
#
# Launch AEDT, create an HFSS design, and save the project.

hfss = ansys.aedt.core.Hfss(
    version=AEDT_VERSION,
    solution_type="DrivenTerminal",
    new_desktop=True,
    non_graphical=non_graphical,
)
hfss.save_project(
    os.path.join(temp_folder.name, generate_unique_name("example") + ".aedt")
)

# ## Modify design settings
#
# Modify some design settings.

hfss.change_material_override(True)
hfss.change_automatically_use_causal_materials(True)
hfss.create_open_region("100GHz")
hfss.modeler.model_units = "mil"
hfss.mesh.assign_initial_mesh_from_slider(applycurvilinear=True)

# ## Create variables
#
# Create input variables for creating the flex cable CPWG.

# +
total_length = 300
theta = 120
r = 100
width = 3
height = 0.1
spacing = 1.53
gnd_width = 10
gnd_thickness = 2

xt = (total_length - r * radians(theta)) / 2
# -

# ## Create bend
#
# The ``create_bending()`` method creates a list of points for
# the bend based on the curvature radius and extension.


def create_bending(radius, extension=0):
    points = [(-xt, 0, -radius), (0, 0, -radius)]

    for i in [radians(i) for i in range(theta)] + [radians(theta + 0.000000001)]:
        points.append((radius * sin(i), 0, -radius * cos(i)))

    x1, y1, z1 = points[-1]
    x0, y0, z0 = points[-2]

    scale = (xt + extension) / sqrt((x1 - x0) ** 2 + (z1 - z0) ** 2)
    x, y, z = (x1 - x0) * scale + x0, 0, (z1 - z0) * scale + z0

    points[-1] = (x, y, z)
    return points


# ## Draw signal line
#
# Draw a signal line to create a bent signal wire.

points = create_bending(r, 1)
line = hfss.modeler.create_polyline(
    points=points,
    xsection_type="Rectangle",
    xsection_width=height,
    xsection_height=width,
    material="copper",
)

# ## Draw ground line
#
# Draw a ground line to create two bent ground wires.

# +
gnd_r = [(x, spacing + width / 2 + gnd_width / 2, z) for x, y, z in points]
gnd_l = [(x, -y, z) for x, y, z in gnd_r]

gnd_objs = []
for gnd in [gnd_r, gnd_l]:
    x = hfss.modeler.create_polyline(
        points=gnd,
        xsection_type="Rectangle",
        xsection_width=height,
        xsection_height=gnd_width,
        material="copper",
    )
    x.color = (255, 0, 0)
    gnd_objs.append(x)
# -

# ## Draw dielectric
#
# Draw a dielectric to create a dielectric cable.

# +
points = create_bending(r + (height + gnd_thickness) / 2)

fr4 = hfss.modeler.create_polyline(
    points=points,
    xsection_type="Rectangle",
    xsection_width=gnd_thickness,
    xsection_height=width + 2 * spacing + 2 * gnd_width,
    material="FR4_epoxy",
)
# -

# ## Create bottom metals
#
# Create the bottom metals.

# +
points = create_bending(r + height + gnd_thickness, 1)

bot = hfss.modeler.create_polyline(
    points=points,
    xsection_type="Rectangle",
    xsection_width=height,
    xsection_height=width + 2 * spacing + 2 * gnd_width,
    material="copper",
)
# -

# ## Create port interfaces
#
# Create port interfaces (PEC enclosures).

port_faces = []
for face, blockname in zip([fr4.top_face_z, fr4.bottom_face_x], ["b1", "b2"]):
    xc, yc, zc = face.center
    positions = [i.position for i in face.vertices]

    port_sheet_list = [
        ((x - xc) * 10 + xc, (y - yc) + yc, (z - zc) * 10 + zc) for x, y, z in positions
    ]
    s = hfss.modeler.create_polyline(
        port_sheet_list, close_surface=True, cover_surface=True
    )
    center = [round(i, 6) for i in s.faces[0].center]

    port_block = hfss.modeler.thicken_sheet(s.name, -5)
    port_block.name = blockname
    for f in port_block.faces:

        if [round(i, 6) for i in f.center] == center:
            port_faces.append(f)

    port_block.material_name = "PEC"

    for i in [line, bot] + gnd_objs:
        i.subtract([port_block], True)

    print(port_faces)

# ## Create boundary condition
#
# Creates a Perfect E boundary condition.

boundary = []
for face in [fr4.top_face_y, fr4.bottom_face_y]:
    s = hfss.modeler.create_object_from_face(face)
    boundary.append(s)
    hfss.assign_perfecte_to_sheets(s)

# ## Create ports
#
# Create ports.

for s, port_name in zip(port_faces, ["1", "2"]):
    reference = [i.name for i in gnd_objs + boundary + [bot]] + ["b1", "b2"]

    hfss.wave_port(s.id, name=port_name, reference=reference)

# ## Create setup and sweep
#
# Create the setup and sweep.

setup = hfss.create_setup("setup1")
setup["Frequency"] = "2GHz"
setup.props["MaximumPasses"] = 10
setup.props["MinimumConvergedPasses"] = 2
hfss.create_linear_count_sweep(
    setup="setup1",
    units="GHz",
    start_frequency=1e-1,
    stop_frequency=4,
    num_of_freq_points=101,
    name="sweep1",
    save_fields=False,
    sweep_type="Interpolating",
)

# ## Release AEDT

hfss.release_desktop()

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files.
# The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
