# # 3D component creation and reuse
#
# This example demonstrates how to create and use an HFSS 3D component by
# performing the following:
# 1. Create a patch antenna using the HFSS 3D Modeler.
# 2. Save the antenna as a 3D component on the disk.
# 3. Import multiple instances of patch antenna as
#    a 3D component in a new project to create a small array.
# 5. Set up the new design for simulation and optimization.
#
# Keywords: **AEDT**, **Antenna**, **3D component**.

# ## Prerequisites
#
# ### Perform imports

# +
import os
import tempfile
import time

from ansys.aedt.core import Hfss
# -

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2024.2"
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.
#
# This example creates two projects defined in `project_names. 
# The first will be used to
# create the patch antenna model and the 2nd project
# will be used to demonstrate the use 3D components.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
project_names = [os.path.join(temp_folder.name, "start_project.aedt"),
                 os.path.join(temp_folder.name, "final_project.aedt"),
                ]

# ### Launch HFSS
# AEDT is started when an instance of the ``Hfss()`` class is
# instantiated. An HFSS design is automatically inserted in the
# AEDT project.

hfss = Hfss(
    version=AEDT_VERSION,
    design="build_comp",
    new_desktop=True,  # Set to False if you want to connect to an existing AEDT session.
    close_on_exit=True,
    non_graphical=NG_MODE,
    solution_type="Modal",
)
hfss.save_project(project_names[0])

# ## Model preparation
#
# ### Define parameters
#
# Parameters can be defined in the HFSS design and subsequently 
# used to optimiuze
# performance, run parametric studies or 
# explore the impact of tolerance on performance.

hfss["thickness"] = "0.1mm"
hfss["width"] = "1mm"

# ###  Build the antenna model
#
# The compact, 
# [pythonic syntax](https://docs.python-guide.org/writing/style/#code-style) 
# allows you to create the model from simple
# primitives. This patch antenna is comprised of the FR-4 substrate, a rectangle, 
# and the coaxial
# probe feed. Each primitive is of type ``Object3D``.
#
# > **Note: ** The feed length of the patch antenna is fixed and is not
# > parametric in HFSS.

# +
substrate = hfss.modeler.create_box(
    ["-width", "-width", "-thickness"],
    ["2*width", "2*width", "thickness"],
    material="FR4_epoxy",
    name="substrate",
)

feed_length = "0.1mm"  # This parameter is defined only in Python and is not varied

patch = hfss.modeler.create_rectangle(
    "XY", ["-width/2", "-width/2", "0mm"], ["width", "width"], name="patch"
)

inner_conductor = hfss.modeler.create_cylinder(
    2,
    ["-width/8", "-width/4", f"-thickness - {feed_length}"],
    "0.01mm",
    f"thickness + {feed_length}",
    material="copper",
    name="via_inner",
)

via_outer = hfss.modeler.create_cylinder(
    2,
    ["-width/8", "-width/4", "-thickness"],
    "0.025mm",
    f"-{feed_length}",
    material="Teflon_based",
    name="via_teflon",
)
# -

# ### Assign boundaries
#
# Boundary conditions can be assigned to faces or bodies in the model
# using methods of the ``Hfss`` class.

hfss.assign_perfecte_to_sheets(patch, name="patch_bc")

# ### Assign boundaries to the via
#
# The following statement selects the outer surface of the cylinder 
# ``via_outer``, excluding the upper and lower faces, and assigns
# the "perfect conductor" boundary condition.

# +
side_face = [i for i in via_outer.faces if i.id not in 
             [via_outer.top_face_z.id, via_outer.bottom_face_z.id]
            ]

hfss.assign_perfecte_to_sheets(side_face, name="feed_gnd")
hfss.assign_perfecte_to_sheets(substrate.bottom_face_z, name="ground_plane")
hfss.assign_perfecth_to_sheets(via_outer.top_face_z, name="feed_thru")  # Ensure power flows through the ground plane.
hfss.change_material_override(material_override=True)  # Allow the probe feed to extend outside the substrate.
# -

# ### Create wave port
#
# A wave port is assigned to the bottom face of the via. Note that the property `via_outer.bottom_face_z` 
# is a ``FacePrimitive`` object.

p1 = hfss.wave_port(
    via_outer.bottom_face_z,
    name="P1",
    create_pec_cap=True
)

# ### Query the object properties
#
# Everything in Python is an object. You can use the object
# properties to obtain detailed information as shown below:

out_str = f"A port named '{p1.name}' was assigned to a surface object"
out_str += f" of type \n   {type(via_outer.bottom_face_z)}\n"
out_str += f"which is located at the bottom surface of the object '{via_outer.name}'\n"
out_str += f"at the z-elevation: {via_outer.bottom_face_z.bottom_edge_z} "
out_str += f"{hfss.modeler.model_units}\n"
out_str += f"and has the face ID: {via_outer.bottom_face_z.id}."
print(out_str)

# ## Create 3D component
#
# You can now create a 3D component from the antenna model. The following statements
# save the component to the specified location with the name "patch_antenna".

component_path = os.path.join(temp_folder.name, "patch_antenna.a3dcomp")
hfss.modeler.create_3dcomponent(component_path, name="patch_antenna")

# A 2nd instance of HFSS is created to demonstrate how the new 3D component can be
# used within a new design.

hfss2 = Hfss(
    version=AEDT_VERSION,
    project=project_names[1],
    design="new_design",
    solution_type="Modal",
)
hfss2.change_material_override(material_override=True)

# ### Insert 3D components
#
# Place 4 antennas to make a small array. 
# - The substrate thickness is modified by creating the parameter "p_thick" and
#   assigning it to the "thickness" parameter of the components.
# - The first antenna is placed at the origin.
# - The spacing between elements is defined by the parameter $2\times w$

# +
# Define a parameter to use for the substrate thickness.
hfss2["p_thick"] = "0.2mm"

# Define a parameter to specify the patch width.
hfss2["w"] = "1mm"

# [x, y, z] location of the patch elements.
positions = [["2*w", "w", 0], ["-2*w", "w", 0], [0, "2.5*w", 0]]

# Keep track of patch elements and their coordinate systems in Python lists:
elements = []
cs = []

# The first patch is located at the origin.
elements.append(hfss2.modeler.insert_3d_component(component_path, name="patch_0"))
elements[0].parameters["thickness"] = "p_thick"
elements[0].parameters["width"] = "w"

# Now place the other 3 patches:
count = 1
for p in positions:
    cs.append(hfss2.modeler.create_coordinate_system(origin=p, name="cs_" + str(count)))  # Create the patch coordinate system.
    elements.append(hfss2.modeler.insert_3d_component(component_path,  # Place the patch element.
                                                      coordinate_system=cs[-1].name,
                                                      name="patch_" + str(count))
                    )
    count +=1

    elements[-1].parameters["thickness"] = "p_thick"
    elements[-1].parameters["width"] = "w"
# -

# You can inspect the component parameters.

units = hfss2.modeler.model_units  # Retrieve the length units as a string.
for e in elements:
    print(f"Component '{e.name}' is located at (x={e.center[0]} {units}, y={e.center[1]} {units})")

# ### Move 3D components
#
# The position of each 3D component can be changed by modifying the ``origin`` 
# of the corresponding coordinate system.

hfss2.modeler.coordinate_systems[0].origin = [0, "2*w", 0]

# ### Create air region
#
# The volume of the solution domain is defined
# by an air region object. The following cell creates the
# region object and assigns the radiation boundary to the outer surfaces of 
# the region.

hfss2.modeler.create_air_region( x_pos=2, y_pos=2, z_pos=2.5, x_neg=2, y_neg=2, z_neg=2, is_percentage=False)
hfss2.assign_radiation_boundary_to_faces(hfss2.modeler["Region"].faces)

# ### Create solution setup and optimetrics analysis
#
# Once a project is ready to be solved, define the solution setup and parametric analysis.

# +
setup1 = hfss2.create_setup(RangeStart="60GHz", RangeEnd="80GHz")
optim = hfss2.parametrics.add("w", start_point="0.8mm",
                              end_point="1.2mm",
                              step="0.05mm",
                              variation_type="LinearStep",
                              name="Sweep Patch Width")

if hfss.valid_design:
    print(f"The HFSS design '{hfss.design_name}' is ready to solve.")
else:
    print(f"Something is not quite right.")
# -

# ### Visualize the model

hfss2.modeler.fit_all()
hfss2.plot(
    show=False,
    output_file=os.path.join(hfss.working_directory, "Image.jpg"),
    plot_air_objects=True,
)

# ## Finish
#
# ### Save the project

hfss2.save_project()
hfss2.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
