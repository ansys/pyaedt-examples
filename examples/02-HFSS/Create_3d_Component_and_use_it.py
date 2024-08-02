# # Create a 3D Component and reuse it

# Summary of the workflow:
# 1. Create an antenna using PyAEDT and HFSS 3D Modeler (same can be done with EDB and
# HFSS 3D Layout).
# 2. Store the object as a 3D Component on the disk.
# 3. Reuse the 3D component in another project.
# 4. Parametrize and optimize target design.
#
# Keywords: **HFSS**, **3D Component**.

# ## Preparation
# Import the required packages

import os
import tempfile
import time

from pyaedt import Hfss

# ## Project setup
#
# Define constants

AEDT_VERSION = "2024.1"
NG_MODE = False  # Open Electronics UI when the application is launched.

# Create temporary directory

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")

# Create an HFSS object.

hfss = Hfss(
    version=AEDT_VERSION,
    new_desktop=True,
    close_on_exit=True,
    non_graphical=NG_MODE,
)
hfss.save_project(os.path.join(temp_dir.name, "example.aedt"))

# ## Variable definition
#
# PyAEDT can create and store all variables available in AEDT (Design, Project, Post Processing).

hfss["thick"] = "0.1mm"
hfss["width"] = "1mm"

# ##  Modeler
#
# PyAEDT supports all modeler functionalities available in the Desktop.
# Objects can be created, deleted and modified using all available boolean operations.
# History is also fully accessible to PyAEDT.

# +
substrate = hfss.modeler.create_box(
    ["-width", "-width", "-thick"],
    ["2*width", "2*width", "thick"],
    matname="FR4_epoxy",
    name="sub",
)

patch = hfss.modeler.create_rectangle(
    "XY", ["-width/2", "-width/2", "0mm"], ["width", "width"], name="patch1"
)

via1 = hfss.modeler.create_cylinder(
    2,
    ["-width/8", "-width/4", "-thick"],
    "0.01mm",
    "thick",
    matname="copper",
    name="via_inner",
)

via_outer = hfss.modeler.create_cylinder(
    2,
    ["-width/8", "-width/4", "-thick"],
    "0.025mm",
    "thick",
    matname="Teflon_based",
    name="via_teflon",
)
# -

# ## Boundaries
#
# Most of HFSS boundaries and excitations are already available in PyAEDT.
# User can assign easily a boundary to a face or to an object by taking benefits of
# Object-Oriented Programming (OOP) available in PyAEDT.

hfss.assign_perfecte_to_sheets(patch)

# ## Assign boundary to faces
#
# Assign boundaries to the top and bottom faces of an object.

# +
side_face = [
    i
    for i in via_outer.faces
    if i.id not in [via_outer.top_face_z.id, via_outer.bottom_face_z.id]
]

hfss.assign_perfecte_to_sheets(side_face)
hfss.assign_perfecte_to_sheets(substrate.bottom_face_z)
# -

# ## Create Wave Port
#
# Wave port can be assigned to a sheet or to a face of an object.

hfss.wave_port(
    via_outer.bottom_face_z,
    name="P1",
)

# ## Create 3D Component
#
# Once the model is ready a 3D Component can be created.
# Multiple options are available to partially select objects, cs, boundaries and mesh operations.
# Furthermore, encrypted 3d comp can be created too.

component_path = os.path.join(temp_dir.name, "component_test.aedbcomp")
hfss.modeler.create_3dcomponent(component_path, "patch_antenna")

# ## Multiple project management
#
# PyAEDT allows to control multiple projects, design and solution type at the same time.

new_project = os.path.join(temp_dir.name, "new_project.aedt")
hfss2 = Hfss(project=new_project, design="new_design")

# ## Insert 3D component
#
# The 3D component can be inserted without any additional info.
# All needed info will be read from the file itself.

hfss2.modeler.insert_3d_component(component_path)

# ## 3D Component Parameters
#
# All 3D Component parameters are available and can be parametrized.

hfss2.modeler.user_defined_components["patch_antenna1"].parameters
hfss2["p_thick"] = "1mm"
hfss2.modeler.user_defined_components["patch_antenna1"].parameters["thick"] = "p_thick"

# ## Multiple 3D Components
#
# There is no limit to the number of 3D components that can be added to the same design.
# They can be the same or linked to different files.

hfss2.modeler.create_coordinate_system(origin=[20, 20, 10], name="Second_antenna")
ant2 = hfss2.modeler.insert_3d_component(component_path, coordinate_system="Second_antenna")

# ## Move 3D components
#
# The 3D component can be moved by changing is position or moving the relative coordinate system.

hfss2.modeler.coordinate_systems[0].origin = [10, 10, 3]

# ## Create air region
#
# Assign a boundary to a face or an object.

hfss2.modeler.create_air_region(30, 30, 30, 30, 30, 30)
hfss2.assign_radiation_boundary_to_faces(hfss2.modeler["Region"].faces)

# ## Create Setup and Optimetrics.
#
# Once project is ready to be solved, a setup and parametrics analysis can be created with PyAEDT.
# All setup parameters can be edited.

setup1 = hfss2.create_setup()
optim = hfss2.parametrics.add("p_thick", "0.2mm", "1.5mm", step=14)

# ## Plot objects

hfss2.modeler.fit_all()
hfss2.plot(
    show=False,
    output_file=os.path.join(hfss.working_directory, "Image.jpg"),
    plot_air_objects=True,
)

# ## Release AEDT

hfss2.save_project()
hfss2.release_desktop()
# Wait 3 seconds to allow Electronics Desktop to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Cleanup
#
# All project files are saved in the folder ``temp_dir.name``.
# If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell removes
# all temporary files, including the project folder.

temp_dir.cleanup()
