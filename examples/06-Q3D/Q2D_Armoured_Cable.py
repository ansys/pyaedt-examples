# # Cable parameter identification

# This example shows how you can use PyAEDT to perform these tasks:
#
#  - Create a Q2D design using modeler primitives and imported CAD.
#  - Set up the simulation.
#  - Link the solution to a Simplorer design.
#
# For information on the cable model used in this example please see the following link:
#
# - [4 Core Armoured Power Cable]
# (https://www.luxingcable.com/low-voltage-cables/4-core-armoured-power-cable.html)
#
# Keywords: **Q2D**, **Cable**.

# ## Perform required imports
#

import math
import os
import tempfile
import time

import ansys.aedt.core

# ## Create temporary directory

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# Define constants.

AEDT_VERSION = "2024.2"
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Set up for model creation
#
# Initialize cable sizing - radii in mm.

c_strand_radius = 2.575
cable_n_cores = 4
core_n_strands = 6
core_xlpe_ins_thickness = 0.5
core_xy_coord = math.ceil(3 * c_strand_radius + 2 * core_xlpe_ins_thickness)

# Initialize radii of further structures incrementally adding thicknesses.

filling_radius = 1.4142 * (
    core_xy_coord + 3 * c_strand_radius + core_xlpe_ins_thickness + 0.5
)
inner_sheath_radius = filling_radius + 0.75
armour_thickness = 3
armour_radius = inner_sheath_radius + armour_thickness
outer_sheath_radius = armour_radius + 2

# Initialize radii.

armour_centre_pos = inner_sheath_radius + armour_thickness / 2.0
arm_strand_rad = armour_thickness / 2.0 - 0.2
n_arm_strands = 30

# Start an instance of the Q2D extractor, providing the version, project name, design
# name and type.

project_name = os.path.join(temp_folder.name, "Q2D_ArmouredCableExample.aedt")
q2d_design_name = "2D_Extractor_Cable"
setup_name = "AnalysisSeetup"
sweep_name = "FreqSweep"
tb_design_name = "CableSystem"
q2d = ansys.aedt.core.Q2d(
    project=project_name,
    design=q2d_design_name,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
)
q2d.modeler.model_units = "mm"

# Assign the variables to the Q3D design.

core_params = {
    "n_cores": str(cable_n_cores),
    "n_strands_core": str(core_n_strands),
    "c_strand_radius": str(c_strand_radius) + "mm",
    "c_strand_xy_coord": str(core_xy_coord) + "mm",
}
outer_params = {
    "filling_radius": str(filling_radius) + "mm",
    "inner_sheath_radius": str(inner_sheath_radius) + "mm",
    "armour_radius": str(armour_radius) + "mm",
    "outer_sheath_radius": str(outer_sheath_radius) + "mm",
}
armour_params = {
    "armour_centre_pos": str(armour_centre_pos) + "mm",
    "arm_strand_rad": str(arm_strand_rad) + "mm",
    "n_arm_strands": str(n_arm_strands),
}
for k, v in core_params.items():
    q2d[k] = v
for k, v in outer_params.items():
    q2d[k] = v
for k, v in armour_params.items():
    q2d[k] = v

# Cable insulators require the definition of specific materials since they are not
# included in the Sys Library.
# Plastic, PE (cross-linked, wire, and cable grade)

mat_pe_cable_grade = q2d.materials.add_material("plastic_pe_cable_grade")
mat_pe_cable_grade.conductivity = "1.40573e-16"
mat_pe_cable_grade.permittivity = "2.09762"
mat_pe_cable_grade.dielectric_loss_tangent = "0.000264575"
mat_pe_cable_grade.update()

# Plastic, PP (10% carbon fiber)

mat_pp = q2d.materials.add_material("plastic_pp_carbon_fiber")
mat_pp.conductivity = "0.0003161"
mat_pp.update()

# ## Model Creation
#
# Create the geometry for core strands, fill, and XLPE insulation.

q2d.modeler.create_coordinate_system(
    origin=["c_strand_xy_coord", "c_strand_xy_coord", "0mm"], name="CS_c_strand_1"
)
q2d.modeler.set_working_coordinate_system("CS_c_strand_1")
c1_id = q2d.modeler.create_circle(
    origin=["0mm", "0mm", "0mm"],
    radius="c_strand_radius",
    name="c_strand_1",
    material="copper",
)
c2_id = c1_id.duplicate_along_line(
    vector=["0mm", "2.0*c_strand_radius", "0mm"], clones=2
)
q2d.modeler.duplicate_around_axis(c2_id, axis="Z", angle=360 / core_n_strands, clones=6)
c_unite_name = q2d.modeler.unite(q2d.get_all_conductors_names())

fill_id = q2d.modeler.create_circle(
    origin=["0mm", "0mm", "0mm"],
    radius="3*c_strand_radius",
    name="c_strand_fill",
    material="plastic_pp_carbon_fiber",
)
fill_id.color = (255, 255, 0)

xlpe_id = q2d.modeler.create_circle(
    origin=["0mm", "0mm", "0mm"],
    radius="3*c_strand_radius+" + str(core_xlpe_ins_thickness) + "mm",
    name="c_strand_xlpe",
    material="plastic_pe_cable_grade",
)
xlpe_id.color = (0, 128, 128)

q2d.modeler.set_working_coordinate_system("Global")

all_obj_names = q2d.get_all_conductors_names() + q2d.get_all_dielectrics_names()

q2d.modeler.duplicate_around_axis(
    all_obj_names, axis="Z", angle=360 / cable_n_cores, clones=4
)
cond_names = q2d.get_all_conductors_names()

# Define the filling object.

filling_id = q2d.modeler.create_circle(
    origin=["0mm", "0mm", "0mm"],
    radius="filling_radius",
    name="Filling",
    material="plastic_pp_carbon_fiber",
)
filling_id.color = (255, 255, 180)

# Define the inner sheath.

inner_sheath_id = q2d.modeler.create_circle(
    origin=["0mm", "0mm", "0mm"],
    radius="inner_sheath_radius",
    name="InnerSheath",
    material="PVC plastic",
)
inner_sheath_id.color = (0, 0, 0)

# Create the armature fill.

arm_fill_id = q2d.modeler.create_circle(
    origin=["0mm", "0mm", "0mm"],
    radius="armour_radius",
    name="ArmourFilling",
    material="plastic_pp_carbon_fiber",
)
arm_fill_id.color = (255, 255, 255)

# Create geometry for the outer sheath.

outer_sheath_id = q2d.modeler.create_circle(
    origin=["0mm", "0mm", "0mm"],
    radius="outer_sheath_radius",
    name="OuterSheath",
    material="PVC plastic",
)
outer_sheath_id.color = (0, 0, 0)

# Create the geometry for armature steel strands.

arm_strand_1_id = q2d.modeler.create_circle(
    origin=["0mm", "armour_centre_pos", "0mm"],
    radius="1.1mm",
    name="arm_strand_1",
    material="steel_stainless",
)
arm_strand_1_id.color = (128, 128, 64)
arm_strand_1_id.duplicate_around_axis(
    axis="Z", angle="360deg/n_arm_strands", clones="n_arm_strands"
)
arm_strand_names = q2d.modeler.get_objects_w_string("arm_strand")

# Define the outer region that defines the solution domain.

region = q2d.modeler.create_region([500, 500, 500, 500])
region.material_name = "vacuum"

# Assign conductors and reference ground.

obj = [q2d.modeler.get_object_from_name(i) for i in cond_names]
[
    q2d.assign_single_conductor(
        name="C1" + str(obj.index(i) + 1), assignment=i, conductor_type="SignalLine"
    )
    for i in obj
]
obj = [q2d.modeler.get_object_from_name(i) for i in arm_strand_names]
q2d.assign_single_conductor(
    name="gnd", assignment=obj, conductor_type="ReferenceGround"
)
q2d.modeler.fit_all()

# ## Plot model

model = q2d.plot(show=False)
model.plot(os.path.join(temp_folder.name, "Image.jpg"))

# Specify the design settings

lumped_length = "100m"
q2d.design_settings["LumpedLength"] = lumped_length

# ## Solve the model
#
# Insert setup and frequency sweep

q2d_setup = q2d.create_setup(name=setup_name)
q2d_sweep = q2d_setup.add_sweep(name=sweep_name)

# The cable model is generated by running two solution types:
# 1. Capacitance and conductance per unit length (CG).
# For this model, the CG solution runs in a few seconds.
# 2. Series resistance and inductance (RL).
# For this model the solution time can range from 15-20 minutes,
# depending on the available hardware.
#
# Uncomment the following line to run the analysis.

# +
# q2d.analyze()
# -

# ## Evaluate results
#
# Add a Simplorer/Twin Builder design and the Q3D dynamic component

tb = ansys.aedt.core.TwinBuilder(design=tb_design_name, version=AEDT_VERSION)

# Add a Q2D dynamic component.

tb.add_q3d_dynamic_component(
    project_name,
    q2d_design_name,
    q2d_setup.name,
    q2d_sweep.name,
    model_depth=lumped_length,
    coupling_matrix_name="Original",
)

# ## Release AEDT

tb.save_project()
tb.release_desktop()
# Wait 3 seconds to allow Electronics Desktop to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Cleanup
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
