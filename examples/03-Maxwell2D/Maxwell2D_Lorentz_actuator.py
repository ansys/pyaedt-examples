# # Lorentz actuator
#
# This example uses PyAEDT to set up a Lorentz actuator
# and solve it using the Maxwell 2D transient solver.
#
# Keywords: **Maxwell 2D**, **transient**, **translational motion**, **mechanical transient**

# ## Perform required imports
#
# Perform required imports.

import os
import tempfile
import time

import ansys.aedt.core

# ## Define constants

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory
#
# Create temporary directory.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")


# ## Initialize dictionaries
#
# Initialize electric and geometric parameters for the actuator.
# Initialize simulation specification.
# Initialize materials for the actuator component.

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
    "Band_clearance": "1mm"
}

coil_specifications = {
    "Winding_current": "5A",
    "No_of_turns": "100",
    "Coil_mass": "0.2kg"
}

simulation_specifications = {
    "Mesh_bands": "0.5mm",
    "Mesh_other_objects": "2mm",
    "Stop_time": "10ms",
    "Time_step": "0.5ms",
    "Save_fields_interval": "1"
}

materials = {
    "Coil_material": "copper",
    "Core_material": "steel_1008",
    "Magnet_material": "NdFe30"
}

# ## Launch AEDT and Maxwell 2D
#
# Launch AEDT and Maxwell 2D after first setting up the project and design names,
# the solver, and the version. The following code also creates an instance of the
# ``Maxwell2d`` class named ``m2d``.

project_name = os.path.join(temp_folder.name, "Lorentz_actuator.aedt")
m2d = ansys.aedt.core.Maxwell2d(
    projectname=project_name,
    designname="1 transient 2D",
    solution_type="TransientXY",
    specified_version=AEDT_VERSION,
    non_graphical=NG_MODE
)

# ## Define variables from dictionaries
#
# Define design variables from the created dictionaries.

m2d.variable_manager.set_variable(variable_name="Dimensions")
for k, v in dimensions.items():
    m2d[k] = v

m2d.variable_manager.set_variable(variable_name="Winding data")
for k, v in coil_specifications.items():
    m2d[k] = v

m2d.variable_manager.set_variable(variable_name="Simulation data")
for k, v in simulation_specifications.items():
    m2d[k] = v

# Materials.

m2d.variable_manager.set_variable(variable_name="Material data")
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
    material_array.append("\"" + v + "\"")
s = ', '.join(material_array)
m2d["Materials"] = "[{}]".format(s)

# ## Create geometry
#
# Create magnetic core, coils, and magnets. Assign materials and create a new coordinate system to
# define the magnet orientation.

mod = m2d.modeler
core_id = mod.create_rectangle(
    origin=[0, 0, 0],
    sizes=["Core_outer_x", "Core_outer_y"],
    name="Core")
m2d.modeler[core_id].material_name = "Materials[" + str(core_mat_index) + "]"

hole_id = mod.create_rectangle(
    origin=["Core_thickness", "Core_thickness", 0],
    sizes=["Core_outer_x-2*Core_thickness", "Core_outer_y-2*Core_thickness"],
    name="hole")
mod.subtract(blank_list=[core_id], tool_list=[hole_id])

magnet_n_id = mod.create_rectangle(
    origin=["Core_thickness", "Core_outer_y-2*Core_thickness", 0],
    sizes=["Core_outer_x-2*Core_thickness", "Magnet_thickness"],
    name="magnet_n")
magnet_s_id = mod.create_rectangle(
    origin=["Core_thickness", "Core_thickness", 0],
    sizes=["Core_outer_x-2*Core_thickness", "Magnet_thickness"],
    name="magnet_s")

m2d.modeler[magnet_n_id].material_name = "Materials[" + str(magnet_mat_index) + "]"
m2d.modeler[magnet_s_id].material_name = "Materials[" + str(magnet_mat_index) + "]"

mod.create_coordinate_system(origin=[0, 0, 0], x_pointing=[0, 1, 0], y_pointing=[1, 0, 0], name="cs_x_positive")
mod.create_coordinate_system(origin=[0, 0, 0], x_pointing=[0, -1, 0], y_pointing=[1, 0, 0], name="cs_x_negative")
magnet_s_id.part_coordinate_system = "cs_x_positive"
magnet_n_id.part_coordinate_system = "cs_x_negative"
mod.set_working_coordinate_system("Global")

# ## Assign current
#
# Create coil terminals with 100 turns and winding with 5A current.

coil_in_id = mod.create_rectangle(
    origin=["Core_thickness+Coil_start_position", "Core_thickness+Magnet_thickness+Coil_magnet_distance", 0],
    sizes=["Coil_width", "Coil_thickness"],
    name="coil_in"
)
coil_out_id = mod.create_rectangle(
    origin=["Core_thickness+Coil_start_position",
            "Core_thickness+Magnet_thickness+Coil_magnet_distance+Coil_inner_diameter+Coil_thickness", 0],
    sizes=["Coil_width", "Coil_thickness"],
    name="coil_out"
)
m2d.modeler[coil_in_id].material_name = "Materials[" + str(coil_mat_index) + "]"
m2d.modeler[coil_out_id].material_name = "Materials[" + str(coil_mat_index) + "]"

m2d.assign_coil(
    assignment=[coil_in_id],
    conductors_number="No_of_turns",
    name="coil_terminal_in",
    polarity="Negative"
)
m2d.assign_coil(
    assignment=[coil_out_id],
    conductors_number="No_of_turns",
    name="coil_terminal_out",
    polarity="Positive"
)
m2d.assign_winding(is_solid=False, current="Winding_current", name="Winding1")
m2d.add_winding_coils(assignment="Winding1", coils=["coil_terminal_in", "coil_terminal_out"])

# ## Assign motion
#
# Create band objects: All the objects within the band move. Inner band ensures that the mesh is good,
# and additionally it is required when there more than 1 moving objects.
# Assign linear motion with mechanical transient.

band_id = mod.create_rectangle(
    origin=["Core_thickness + Band_clearance", "Core_thickness+Magnet_thickness+Band_clearance", 0],
    sizes=["Core_outer_x-2*(Core_thickness+Band_clearance)",
           "Core_outer_y-2*(Core_thickness+Band_clearance+Magnet_thickness)"],
    name="Motion_band")
inner_band_id = mod.create_rectangle(
    origin=["Core_thickness+Coil_start_position-Band_clearance",
            "Core_thickness+Magnet_thickness+Coil_magnet_distance-Band_clearance", 0],
    sizes=["Coil_width + 2*Band_clearance", "Coil_inner_diameter+2*(Coil_thickness+Band_clearance)"],
    name="Motion_band_inner")
motion_limit = "Core_outer_x-2*(Core_thickness+Band_clearance)-(Coil_width + 2*Band_clearance)-2*Band_clearance"
m2d.assign_translate_motion(
    assignment="Motion_band", axis="X", periodic_translate=None, mechanical_transient=True,
    mass="Coil_mass", start_position=0, negative_limit=0, positive_limit=motion_limit
)

# ## Create simulation domain
#
# Create region and assign zero vector potential on the region edges.

region_id = mod.create_region(pad_percent=2)
m2d.assign_vector_potential(assignment=region_id.edges, boundary="VectorPotential1")

# ## Assign mesh operations
#
# Transient solver does not have adaptive mesh refinement, so the mesh operations have to be assigned.

m2d.mesh.assign_length_mesh(assignment=[band_id, inner_band_id],
                            maximum_length="Mesh_bands", maximum_elements=None, name="Bands")
m2d.mesh.assign_length_mesh(
    assignment=[coil_in_id, coil_in_id, core_id, magnet_n_id, magnet_s_id, region_id],
    maximum_length="Mesh_other_objects", maximum_elements=None, name="Coils_core_magnets"
)

# ## Turn on eddy effects
#
# Turn on eddy effects.

# m2d.eddy_effects_on(assignment=["magnet_n", "magnet_s"])

# ## Turn on core loss
#
# Turn on core loss.

# m2d.set_core_losses(assignment="Core")

# ## Create setup
#
# Create the simulation setup.

# ## Set model depth
#
# Set the model depth.

setup = m2d.create_setup(name="Setup1")
setup.props["StopTime"] = "Stop_time"
setup.props["TimeStep"] = "Time_step"
setup.props["SaveFieldsType"] = "Every N Steps"
setup.props["N Steps"] = "Save_fields_interval"
setup.props["Steps From"] = "0ms"
setup.props["Steps To"] = "Stop_time"

# ## Create report
#
# Create a XY-report with force on coil and the position of the coil on Y-axis, time on X-axis.

m2d.post.create_report(
    expressions=["Moving1.Force_x", "Moving1.Position"],
    plot_name="Force on Coil and Position of Coil", primary_sweep_variable="Time"
)

# ## Analyze project
#
# Analyze the project.

setup.analyze(cores=NUM_CORES, use_auto_settings=False)

# ## Release AEDT

m2d.save_project()
m2d.release_desktop()
# Wait 3 seconds to allow Electronics Desktop to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Cleanup
#
# All project files are saved in the folder ``temp_dir.name``.
# If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()