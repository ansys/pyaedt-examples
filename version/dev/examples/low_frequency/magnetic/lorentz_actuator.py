# # Lorentz actuator
#
# This example uses PyAEDT to set up a Lorentz actuator
# and solve it using the Maxwell 2D transient solver.
#
# Keywords: **Maxwell2D**, **transient**, **translational motion**, **mechanical transient**

# ## Perform imports and define constantss
#
# Perform required imports.

# +
import os
import tempfile
import time

import ansys.aedt.core
# -

# Define constants.

AEDT_VERSION = "2025.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Initialize dictionaries
#
# Initialize the following:
#
# - Electric and geometric parameters for the actuator
# - Simulation specifications
# - Materials for the actuator component

dimensions = {
    "Core_outer_x": "100mm",
    "Core_outer_y": "80mm",
    "Core_thickness": "10mm",
    "Magnet_thickness": "10mm",
    "Coil_width": "30mm",
    "Coil_thickness": "5mm",
    "Coil_inner_diameter": "20mm",
    "Coil_magnet_distance": "5mm",
    "Coil_start_position": "3mm",
    "Band_clearance": "1mm",
}

coil_specifications = {
    "Winding_current": "5A",
    "No_of_turns": "100",
    "Coil_mass": "0.2kg",
}

simulation_specifications = {
    "Mesh_bands": "0.5mm",
    "Mesh_other_objects": "2mm",
    "Stop_time": "10ms",
    "Time_step": "0.5ms",
    "Save_fields_interval": "1",
}

materials = {
    "Coil_material": "copper",
    "Core_material": "steel_1008",
    "Magnet_material": "NdFe30",
}

# ## Launch AEDT and Maxwell 2D
#
# Launch AEDT and Maxwell 2D after first setting up the project name.
# The following code also creates an instance of the
# ``Maxwell2d`` class named ``m2d`` by providing
# the project name, the design name, the solver, the version, and the graphical mode.

project_name = os.path.join(temp_folder.name, "Lorentz_actuator.aedt")
m2d = ansys.aedt.core.Maxwell2d(
    project=project_name,
    design="1 transient 2D",
    solution_type="TransientXY",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
)

# ## Define variables from dictionaries
#
# Define design variables from the created dictionaries.

m2d.variable_manager.set_variable(name="Dimensions")
for k, v in dimensions.items():
    m2d[k] = v

m2d.variable_manager.set_variable(name="Winding data")
for k, v in coil_specifications.items():
    m2d[k] = v

m2d.variable_manager.set_variable(name="Simulation data")
for k, v in simulation_specifications.items():
    m2d[k] = v

# Definem materials.

m2d.variable_manager.set_variable(name="Material data")
m2d.logger.clear_messages()
for i, key in enumerate(materials.keys()):
    if key == "Coil_material":
        coil_mat_index = i
    elif key == "Core_material":
        core_mat_index = i
    elif key == "Magnet_material":
        magnet_mat_index = i
material_array = []
for k, v in materials.items():
    material_array.append('"' + v + '"')
s = ", ".join(material_array)
m2d["Materials"] = "[{}]".format(s)

# ## Create geometry
#
# Create magnetic core, coils, and magnets. Assign materials and create a coordinate system to
# define the magnet orientation.

core_id = m2d.modeler.create_rectangle(
    origin=[0, 0, 0],
    sizes=["Core_outer_x", "Core_outer_y"],
    name="Core",
    material="Materials[" + str(core_mat_index) + "]",
)

hole_id = m2d.modeler.create_rectangle(
    origin=["Core_thickness", "Core_thickness", 0],
    sizes=["Core_outer_x-2*Core_thickness", "Core_outer_y-2*Core_thickness"],
    name="hole",
)
m2d.modeler.subtract(blank_list=[core_id], tool_list=[hole_id])

magnet_n_id = m2d.modeler.create_rectangle(
    origin=["Core_thickness", "Core_outer_y-2*Core_thickness", 0],
    sizes=["Core_outer_x-2*Core_thickness", "Magnet_thickness"],
    name="magnet_n",
    material="Materials[" + str(magnet_mat_index) + "]",
)
magnet_s_id = m2d.modeler.create_rectangle(
    origin=["Core_thickness", "Core_thickness", 0],
    sizes=["Core_outer_x-2*Core_thickness", "Magnet_thickness"],
    name="magnet_s",
    material="Materials[" + str(magnet_mat_index) + "]",
)

m2d.modeler.create_coordinate_system(
    origin=[0, 0, 0], x_pointing=[0, 1, 0], y_pointing=[1, 0, 0], name="cs_x_positive"
)
m2d.modeler.create_coordinate_system(
    origin=[0, 0, 0], x_pointing=[0, -1, 0], y_pointing=[1, 0, 0], name="cs_x_negative"
)
magnet_s_id.part_coordinate_system = "cs_x_positive"
magnet_n_id.part_coordinate_system = "cs_x_negative"
m2d.modeler.set_working_coordinate_system("Global")

# ## Assign current
#
# Create coil terminals with 100 turns and winding with 5A current.

coil_in_id = m2d.modeler.create_rectangle(
    origin=[
        "Core_thickness+Coil_start_position",
        "Core_thickness+Magnet_thickness+Coil_magnet_distance",
        0,
    ],
    sizes=["Coil_width", "Coil_thickness"],
    name="coil_in",
    material="Materials[" + str(coil_mat_index) + "]",
)
coil_out_id = m2d.modeler.create_rectangle(
    origin=[
        "Core_thickness+Coil_start_position",
        "Core_thickness+Magnet_thickness+Coil_magnet_distance+Coil_inner_diameter+Coil_thickness",
        0,
    ],
    sizes=["Coil_width", "Coil_thickness"],
    name="coil_out",
    material="Materials[" + str(coil_mat_index) + "]",
)

m2d.assign_coil(
    assignment=[coil_in_id],
    conductors_number="No_of_turns",
    name="coil_terminal_in",
    polarity="Negative",
)
m2d.assign_coil(
    assignment=[coil_out_id],
    conductors_number="No_of_turns",
    name="coil_terminal_out",
    polarity="Positive",
)
m2d.assign_winding(is_solid=False, current="Winding_current", name="Winding1")
m2d.add_winding_coils(
    assignment="Winding1", coils=["coil_terminal_in", "coil_terminal_out"]
)

# ## Assign motion
#
# Create band objects. All the objects within the band move. The inner band ensures that the mesh is good,
# and additionally it is required when there is more than one moving object.
# Assign linear motion with mechanical transient.

band_id = m2d.modeler.create_rectangle(
    origin=[
        "Core_thickness + Band_clearance",
        "Core_thickness+Magnet_thickness+Band_clearance",
        0,
    ],
    sizes=[
        "Core_outer_x-2*(Core_thickness+Band_clearance)",
        "Core_outer_y-2*(Core_thickness+Band_clearance+Magnet_thickness)",
    ],
    name="Motion_band",
)
inner_band_id = m2d.modeler.create_rectangle(
    origin=[
        "Core_thickness+Coil_start_position-Band_clearance",
        "Core_thickness+Magnet_thickness+Coil_magnet_distance-Band_clearance",
        0,
    ],
    sizes=[
        "Coil_width + 2*Band_clearance",
        "Coil_inner_diameter+2*(Coil_thickness+Band_clearance)",
    ],
    name="Motion_band_inner",
)
motion_limit = "Core_outer_x-2*(Core_thickness+Band_clearance)-(Coil_width + 2*Band_clearance)-2*Band_clearance"
m2d.assign_translate_motion(
    assignment="Motion_band",
    axis="X",
    periodic_translate=None,
    mechanical_transient=True,
    mass="Coil_mass",
    start_position=0,
    negative_limit=0,
    positive_limit=motion_limit,
)

# ## Create simulation domain
#
# Create a region and assign zero vector potential on the region edges.

region_id = m2d.modeler.create_region(pad_percent=2)
m2d.assign_vector_potential(assignment=region_id.edges, boundary="VectorPotential1")

# ## Assign mesh operations
#
# The transient solver does not have adaptive mesh refinement, so the mesh operations must be assigned.

m2d.mesh.assign_length_mesh(
    assignment=[band_id, inner_band_id],
    maximum_length="Mesh_bands",
    maximum_elements=None,
    name="Bands",
)
m2d.mesh.assign_length_mesh(
    assignment=[coil_in_id, coil_in_id, core_id, magnet_n_id, magnet_s_id, region_id],
    maximum_length="Mesh_other_objects",
    maximum_elements=None,
    name="Coils_core_magnets",
)

# ## Turn on eddy effects
#
# Assign eddy effects to the magnets.

m2d.eddy_effects_on(assignment=["magnet_n", "magnet_s"])

# ## Turn on core loss
#
# Enable core loss for the core.

m2d.set_core_losses(assignment="Core")

# ## Create simulation setup

setup = m2d.create_setup(name="Setup1")
setup.props["StopTime"] = "Stop_time"
setup.props["TimeStep"] = "Time_step"
setup.props["SaveFieldsType"] = "Every N Steps"
setup.props["N Steps"] = "Save_fields_interval"
setup.props["Steps From"] = "0ms"
setup.props["Steps To"] = "Stop_time"

# ## Create report
#
# Create an XY-report with force on the coil, the position of the coil on the Y axis,
# and time on the X axis.

m2d.post.create_report(
    expressions=["Moving1.Force_x", "Moving1.Position"],
    plot_name="Force on Coil and Position of Coil",
    primary_sweep_variable="Time",
)

# ## Analyze project

setup.analyze(cores=NUM_CORES, use_auto_settings=False)

# ## Release AEDT

m2d.save_project()
m2d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_dir.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
