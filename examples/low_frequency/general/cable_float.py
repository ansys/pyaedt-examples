# # Example of a reference subsea power cable construction for floating offshore application

# This example shows how to use PyAEDT to perform these tasks:
#
#  - Import Design Variables and Material definitions from a json configuration file.
#  - Create a Maxwell2D design.
#  - Generate the geometry for a reference cable for floating offshore wind applications.
#
#
# For information on the cable model used in this example, see
# (https://www.mdpi.com/2071-1050/16/7/2899).
#
# Keywords: **Maxwell2D**, **subsea power cable**.

# ## Perform imports and define constants
#
# Perform required imports.

# +

from dataclasses import dataclass
import os
import tempfile
import time
from pathlib import Path

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_file

# -

# Define constants.

AEDT_VERSION = "2026.1"
NG_MODE = False  # Open AEDT UI when it is launched.
JSON_FILENAME = "config_power_cable.json"

# ## Create temporary directory and paths
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
data_folder = Path(download_file(r"pyaedt/maxwell_power_cable", local_path=temp_folder.name))
json_path = data_folder / JSON_FILENAME

# ## Set up for model creation
#
# Start an instance of Maxwell 2d, providing the version, project name, design
# name, and type.

project_name = os.path.join(temp_folder.name, "PowerCableExample.aedt")
m2d_design_name = "2D_Cable"
setup_name = "AnalysisSetup"
sweep_name = "FreqSweep"
tb_design_name = "CableSystem"
m2d = ansys.aedt.core.Maxwell2d(
    project=project_name,
    design=m2d_design_name,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
)
m2d.modeler.model_units = "mm"

# Download and import json configuration file for design variables and material definition

conf_settings = m2d.configurations.import_config(json_path)
mat_from_json_keys_list = list(m2d.materials.material_keys.keys())
for mat_name in mat_from_json_keys_list:
    m2d.materials.add_material(name=mat_name)

# ## Create model
#
# Create the geometry for the conductor structures.

m2d.modeler.create_coordinate_system(origin=["x0_cond", "y0_cond", "0mm"], name="CS_cond_1")
m2d.modeler.set_working_coordinate_system("CS_cond_1")

# Create cable layer object
@dataclass
class CableLayer:
    radius: str
    name: str
    material: str
    color: tuple

# Create layer instances
obj_cond_1 = CableLayer("dia_conductor/2", "cond_1", "copper", (255,0,0))
obj_cond_screen_1 = CableLayer("dia_conductor_screen/2", "cond_screen_1", "copper", (255,0,0))
obj_cond_ins_1 = CableLayer("dia_conductor_insulation/2", "cond_insulation_1", "XLPE", (255,255,0))
obj_cond_ins_screen_1 = CableLayer("dia_conductor_insulation_screen/2", "cond_insulation_screen_1", "copper", (0, 128, 128))
obj_cond_sheat_1 = CableLayer("dia_conductor_sheat/2", "cond_dia_conductor_sheat_1", "MDPE", (143,159,165))
cond_layers = [
    obj_cond_1,
    obj_cond_screen_1,
    obj_cond_ins_1,
    obj_cond_ins_screen_1,
    obj_cond_sheat_1,
]

# Create conductor assembly layer by layer
cond_ids = [
    m2d.modeler.create_circle(
        origin = ["0mm", "0mm", "0mm"],
        radius = layer.radius,
        name = layer.name,
        material = layer.material,
        color = layer.color
    )
    for layer in cond_layers
]

# Duplicate around axis to generate the further 2 inner cables
m2d.modeler.set_working_coordinate_system("Global")
all_obj_names = m2d.get_all_conductors_names() + m2d.get_all_dielectrics_names()
m2d.modeler.duplicate_around_axis(all_obj_names, axis="Z", angle=120, clones=3)

# Create the geometry for the outer structures.

# Create layer instances
obj_filler= CableLayer ("dia_filler/2","filler_background","MDPE", (175,143,175))
obj_bedding = CableLayer("dia_bedding/2","bedding","PPY",(128,0,255))
obj_inner_sheat = CableLayer("dia_inner_sheath/2","inner_sheath","HDPE",(128,0,255))
obj_inner_armor = CableLayer("dia_armor_inner/2","inner_armor","stainless_steel",(128,0,255))
obj_armor_bedding = CableLayer("dia_bedding_armor/2","bedding_armor","PPY",(128,0,255))
obj_outer_armor = CableLayer("dia_armor_outer/2","outer_armour","stainless_steel",(128,0,255))
obj_outer_sheat = CableLayer("dia_outer_sheat/2","outer_sheat","HDPE",(128,0,255))
outer_layers = [
    obj_filler,
    obj_bedding,
    obj_inner_sheat,
    obj_inner_armor,
    obj_armor_bedding,
    obj_outer_armor,
    obj_outer_sheat,
]

# Create outer assembly layer by layer

outer_ids = [
    m2d.modeler.create_circle(
        origin = ["0mm", "0mm", "0mm"],
        radius = layer.radius,
        name = layer.name,
        material = layer.material,
        color = layer.color
    ) for layer in outer_layers
]


# Finalize the filler modeling
# create local coordinate sys to split the object

m2d.modeler.copy(outer_ids[0])
filler_background_water = m2d.modeler.paste()
m2d.assign_material(filler_background_water,"water_sea")
m2d.modeler.create_coordinate_system(
    origin = ["0mm", "0mm", "0mm"],
    mode = "axis",
    x_pointing = ["cos(30deg)", "-sin(30deg)", "0mm"],
    y_pointing = ["sin(30deg)", "cos(30deg)", "0mm"],
    name = "CS_rot_1"
)
m2d.modeler.split(outer_ids[0],"ZX")
m2d.modeler.create_coordinate_system(
    origin = ["0mm", "0mm", "0mm"],
    mode = "axis",
    x_pointing = ["-cos(30deg)", "-sin(30deg)", "0mm"],
    y_pointing = ["-sin(30deg)", "cos(30deg)", "0mm"],
    name = "CS_rot_2"
)
m2d.modeler.split(outer_ids[0],"ZX")
m2d.modeler.delete_objects_containing("Split")
m2d.modeler.set_working_coordinate_system("Global")
tool_ellipse = m2d.modeler.create_ellipse(
    origin = ["0mm","-65mm","0mm"],
    major_radius = 60,
    ratio = 0.55
)
m2d.modeler.intersect([outer_ids[0],tool_ellipse])
m2d.modeler.subtract(
    [outer_ids[0]],
    ["cond_dia_conductor_sheat_1","cond_dia_conductor_sheat_1_2"]
)
m2d.modeler.duplicate_around_axis(outer_ids[0], axis="Z", angle=120, clones=3)

# ## Release AEDT

m2d.save_project()
m2d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()


