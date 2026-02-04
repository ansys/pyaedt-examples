# # Flex cable CPWG
#
# This example shows how to use PyAEDT to create a flex cable CPWG
# (coplanar waveguide with ground).
#
# Keywords: **HFSS**, **flex cable**, **CPWG**.

# ## Prerequisites
#
# ### Perform imports

# +
import tempfile
import time
from math import cos, radians, sin, sqrt
from pathlib import Path

import ansys.aedt.core
# -

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.2"
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Model preparation
#
# HFSS will be launched and a rigid flex cable model 
# will be created.
#
# ### Launch HFSS

hfss = ansys.aedt.core.Hfss(
    version=AEDT_VERSION,
    project=Path(temp_folder.name) / "flex_cable.aedt",
    solution_type="DrivenTerminal",
    new_desktop=True,
    non_graphical=NG_MODE,
)
hfss.save_project()

# ### Update design settings

hfss.change_material_override(True)
hfss.change_automatically_use_causal_materials(True)
hfss.create_open_region("100GHz")
hfss.modeler.model_units = "mil"
hfss.mesh.assign_initial_mesh_from_slider(curvilinear=True)

# ### Create variables
#
# Create input variables for creating the flex cable coplanar waveguide.

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

# ### Define a function to bend the flex cable
#
# The ``create_bending()`` method creates a list of points for
# the bend based on the radius of curvature and extension.


def create_bend(radius, extension=0):
    points = [(-xt, 0, -radius), (0, 0, -radius)]

    for i in [radians(i) for i in range(theta)] + [radians(theta + 0.000000001)]:
        points.append((radius * sin(i), 0, -radius * cos(i)))

    x1, y1, z1 = points[-1]
    x0, y0, z0 = points[-2]

    scale = (xt + extension) / sqrt((x1 - x0) ** 2 + (z1 - z0) ** 2)
    x, y, z = (x1 - x0) * scale + x0, 0, (z1 - z0) * scale + z0

    points[-1] = (x, y, z)
    return points

# ## Build the model
#
# Draw a signal line to create a bent signal wire.

points = create_bend(r, 1)
line = hfss.modeler.create_polyline(
    points=points,
    xsection_type="Rectangle",
    xsection_width=height,
    xsection_height=width,
    material="copper",
)

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

# Draw a dielectric to create a dielectric cable.

# +
points = create_bend(r + (height + gnd_thickness) / 2)

fr4 = hfss.modeler.create_polyline(
    points=points,
    xsection_type="Rectangle",
    xsection_width=gnd_thickness,
    xsection_height=width + 2 * spacing + 2 * gnd_width,
    material="FR4_epoxy",
)
# -

# Create the bottom metal.

# +
points = create_bend(r + height + gnd_thickness, 1)

bot = hfss.modeler.create_polyline(
    points=points,
    xsection_type="Rectangle",
    xsection_width=height,
    xsection_height=width + 2 * spacing + 2 * gnd_width,
    material="copper",
)
# -

# ### Assign sources and boundary conditions
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

# Creates a Perfect E boundary condition.

boundary = []
for face in [fr4.top_face_y, fr4.bottom_face_y]:
    s = hfss.modeler.create_object_from_face(face)
    boundary.append(s)
    hfss.assign_perfecte_to_sheets(s)

# Create ports.

for s, port_name in zip(port_faces, ["1", "2"]):
    reference = [i.name for i in gnd_objs + boundary + [bot]] + ["b1", "b2"]

    hfss.wave_port(s.id, name=port_name, reference=reference)

# ### Specify the solution setup
#
# Create the setup and frequency sweep.

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

# The model is now ready to analyze.
#
# ## Finish
#
# ### Save the project

hfss.save_project()
hfss.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)


# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files.
# The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
