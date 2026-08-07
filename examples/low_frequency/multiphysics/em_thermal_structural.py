# # Electro-Thermal-Structural Analysis
#
# This example uses PyAEDT to model a copper busbar in Q3D, run a stepped DC analysis,
# and pass the resulting losses to a transient thermal simulation with two-way coupling
# and restart enabled at each substep.
# The example includes the following steps:
#
# 1. Import the required packages and load a Q3D project that contains a DC conduction design.
# 2. Run the simulation for a parametric source value.
# 3. Plot the mesh, current-density magnitude, and ohmic losses.
# 4. Enable two-way coupling with temperature feedback from Icepak to Q3D at each substep.
# 5. Complete the transient thermal simulation.
# 6. Create a structural analysis using the final object-averaged temperatures as thermal loads.
# 7. Run the structural analysis.
# 8. Visualize the resulting deformation.
#
# Keywords: **Multiphysics**, **Q3D**, **Icepak**, **Icepak FEA Structural**.

# ## Perform imports and define constants
#
# Perform required imports.

# +
import tempfile
import time
import numpy as np
from itertools import chain

import ansys.aedt.core  # Interface to Ansys Electronics Desktop
from ansys.aedt.core.generic.aedt_constants import IcepakFeaConstants
from ansys.aedt.core.examples.downloads import download_file
# -

# ## Define constants
#
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2026.1"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.
Q3D_DESIGN_NAME = "Q3DDesign"
ICEPAK_DESIGN_NAME = "Icepak"
TIME = [0, 6, 7, 12] #s
CURRENT = [100, 100, 50, 50] #A
Q3D_DESIGN_VAR_NAME = 'I_DC'
END_TIME = 4      #s, thermal transient end time
STEPS = 2        #n. of substeps
TH_TIME_STEP = 0.5 #s thermal transient time step

# ## Create temporary directory
#
# Create a temporary working directory and download the AEDT file.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
project_path = download_file(
    source=r"pyaedt/busbar_3_physics_q3d_icepak_icepakfea",
    name="Q3D_Busbar.aedt",
    local_path=temp_folder.name)

# ## Launch an instance AEDT
#
# Create an instance of the ``Q3d`` class.
# The Ansys Electronics Desktop will be launched with the active Q3d design.
# The ``q3d`` object is subsequently used to create and simulate the model.

q3d = ansys.aedt.core.Q3d(
    project=project_path,
    design=Q3D_DESIGN_NAME,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
)

# ## Model Preparation - Materials
#
# Create temperature dependent materials.
# Duplicate copper and add temperature dependent electrical conductivity.

target_material = "copper"

cu_temp = q3d.materials.duplicate_material(material=target_material, name="copper_temp_dep")
cu_temp.conductivity.add_thermal_modifier_free_form("1.0/(1.0+{}*(Temp-20))".format(0.000001))

matching_objects = [
    obj_name
    for obj_name in q3d.modeler.object_names
    if q3d.modeler[obj_name].material_name
    and q3d.modeler[obj_name].material_name.lower() == target_material.lower()
]

q3d.assign_material(assignment=matching_objects, material=cu_temp.name)

# ## Set objects temperature and enable feedback

q3d.modeler.set_objects_temperature(assignment=matching_objects, ambient_temperature=20)

# ## Define excitations

q3d[Q3D_DESIGN_VAR_NAME]= str(CURRENT[0])+"A"

# ## Create Icepak target design

q3d.create_em_target_design(design="Icepak", design_setup="Natural")
ipk = ansys.aedt.core.Icepak()
ipk.design_name = ICEPAK_DESIGN_NAME

# ## Define solution setup
#
# Set the current value for the coupling-step time using linear interpolation

coupling_time = END_TIME / STEPS
current_value = np.interp(coupling_time, TIME, CURRENT)
ipk[Q3D_DESIGN_VAR_NAME] = f"{current_value:.0f}A"

# Enable desktop logging

ipk.logger.enable_desktop_log()
ipk.logger.add_message(message_type=0, message_text="Solving substep n.1 of " + str(STEPS), level="Project", proj_name=ipk.project_name)

# Icepak transient simulation and time stepping setup

ipk.solution_type = "Transient"
setup = ipk.setups[0]
setup.props["Stop Time"] = str(END_TIME/STEPS)+"s"
setup.props["Time Step"] = str(TH_TIME_STEP)+"s"
setup.props["N Steps"] = 1
ipk.save_project()

# Get the list of object names included in the EM Loss and delete the EM Loss boundary.

em_loss = next(bound for bound in ipk.boundaries if bound.type == "EM Loss")
objs = [ipk.modeler.objects[obj_id].name for obj_id in em_loss.props["Objects"]]
em_loss.delete()

# ## Re-creation of the EM Loss
#
# Re-creation of the EM Loss with mapping of the current pulse parameter between Icepak and Maxwell.
# With this setting, the value of the current pulse to be used in the Maxwell simulation is driven from Icepak.

ipk.assign_em_losses(design=Q3D_DESIGN_NAME, setup="Setup1", assignment=objs, parameters=[Q3D_DESIGN_VAR_NAME], sweep="LastAdaptive", q3d_loss_type="DCVolOrACSurfLoss", map_frequency="1kHz")
ipk.assign_2way_coupling(setup=setup.name, number_of_iterations=2)
ipk.logger.add_message(0, "Current value " + str(ipk[Q3D_DESIGN_VAR_NAME]), level="Project", proj_name=ipk.project_name)

# ## Run analysis
#
# Run simulation for the current coupling step

ipk.analyze()
ipk.logger.add_message(0, "Substep n.1 of " + str(STEPS) + " completed", level="Project", proj_name=ipk.project_name)

# Additional coupling steps loop definition

for n in range(STEPS-1):
    step = n + 2
    ipk.logger.add_message(0, "Solving substep n." + str(step) + " of " + str(STEPS), level="Project", proj_name=ipk.project_name)

# ### Duplicate Icepak design from previous substep and enable the restart
#
# Map ``Q3D_DESIGN_VAR_NAME`` to the value used in the previous substep to avoid
# re-solving the source Icepak design.
# ``Copy Fields From Source`` transfers the results to the restarted design, so only
# the final Icepak design must be kept.

    ipk_name = ipk.design_name
    ipk.duplicate_design(ipk_name)
    ipk = ansys.aedt.core.Icepak()
    ipk.cleanup_solution()
    ipk.save_project()

    setup = ipk.setups[0]
    setup.props["Import Start Time"] = True
    setup.props["Copy Fields From Source"] = True
    setup.start_continue_from_previous_setup(design=ipk_name, solution=setup.name + " : Transient", map_variables_by_name=False, parameters={Q3D_DESIGN_VAR_NAME:f"{np.interp((step - 1) * END_TIME / STEPS, TIME, CURRENT):.0f}A"})
    setup.props["Stop Time"] = str(step*END_TIME/STEPS)+"s"

# Setup of the current pulse value for the current coupling step using linear interpolation

    ipk[Q3D_DESIGN_VAR_NAME] = str(int(np.interp(step*END_TIME/STEPS, TIME, CURRENT))) + "A"
    ipk.logger.add_message(0, "Current value " + str(ipk[Q3D_DESIGN_VAR_NAME]), level="Project", proj_name=ipk.project_name)

# Simulation run for the current coupling step

    ipk.analyze()
    ipk.logger.add_message(0, "Substep n." + str(step) + " of " + str(STEPS) + " completed", level="Project", proj_name=ipk.project_name)

# ## Remove all Icepak designs
#
# Remove all Icepak designs except the last one because all the field data are copied into the last Icepak design.

[ipk.delete_design(d) for d in ipk.design_list if d == ICEPAK_DESIGN_NAME]

# ## Icepak Thermal Transient Postprocess
#
# Access the FieldSummary functionality

field_sum = ipk.post.create_field_summary()

# Compute time steps

substep_time = END_TIME / STEPS
time_substeps_ns = range(
    0,
    int((END_TIME + substep_time) * 1e9),
    int(substep_time * 1e9),
)

# Convert time steps values to strings to be passed to field summary calculation

time_substeps_str = [f"{time_ns}ns" for time_ns in time_substeps_ns]
for obj in objs:
    temp_avg_dict = {
        "name": "temp_avg_"+ obj,
        "description": f"Average Temperature on {obj}",
        "design_type": ["Icepak"],
        "fields_type": ["Fields"],
        "solution_type": "Transient",
        "primary_sweep": "",
        "assignment": "",
        "assignment_type": ["Solid"],
        "operations": [
        "Fundamental_Quantity('Temp')",
        "EnterVolume('assignment')",
        "Operation('VolumeValue')",
        "Operation('Mean')",
        ],
        "report": ["Field3D"]
    }
    expr_name = ipk.post.fields_calculator.add_expression(calculation=temp_avg_dict,
                                                          assignment=obj,
                                                          name="T_avg_"+obj)
    report_temp = ipk.post.create_report(expressions=expr_name, primary_sweep_variable='Time')

    [field_sum.add_calculation(
        entity="Object",
        geometry="Volume",
        geometry_name=obj,
        quantity="Temperature",
        time=t) for t in time_substeps_str]

# GET SETUP TRANSIENT
temperature_data = field_sum.get_field_summary_data(
    pandas_output=True,
    intrinsics="All times",
    variation=ipk.available_variations.variations(ipk.nominal_adaptive, True)[0]
)

# Extract the average temperatures of the reference object at each time step

reference_temperatures = temperature_data["Mean"].iloc[1:].to_numpy()[-(STEPS + 1):]

# Find the time step with the maximum reference temperature

worst_step_index = np.argmax(reference_temperatures)

# Extract object temperatures at the worst-case time step

worst_case_data = temperature_data.iloc[worst_step_index : worst_step_index + 1]
temperature_by_object = dict(zip(worst_case_data["Entity"], worst_case_data["Mean"]))

# ## Create EM Target design
#
# Mechanical Structural Static simulation

q3d.create_em_target_design(design=IcepakFeaConstants.NAME)
design_list = q3d.design_list

# Connect to the newly created IcepakFEA design.

mech = ansys.aedt.core.Mechanical(version=AEDT_VERSION)

# Change the solution type to Structural

mech.solution_type="Structural"

# reorder values according to new_order

# QUESTION
# reordered_avg_temp = [temperature_by_object[name] for name in mech.modeler.object_list if name in  temperature_by_object.keys()]

# assign uniform temperature excitations

# QUESTION
for obj, temp in temperature_by_object.items():
    mech.assign_thermal_condition_uniform(assignment=[obj], temperature =str(temp)+"cel", name=f"ThermalCond_{obj}")

# ## Retrieve from Q3D the Named selections face IDs
#
# Retrieve Q3D named selection face IDs.
# IcepakFEA EM target designs do not automatically inherit Q3D named selections.
# The IDs are remapped in IcepakFEA before applying structural constraints.

q3d_face_ids = [face_id for ns in q3d.modeler.user_lists for face_id in ns.props["List"]]

object_to_Save = {}
mech_face_ids = []

for obj in q3d.modeler.object_list:
    matching_faces = [face.id for face in obj.faces if face.id in q3d_face_ids]
    if matching_faces:
        for face_id in matching_faces:
            fpos = q3d.modeler.get_face_center(assignment=face_id)
            mech_face_ids.append(mech.modeler.get_faceid_from_position(position=fpos, assignment=obj.name))

# Assign ``Fixed support`` boundary condition

mech.assign_fixed_support(assignment=mech_face_ids, name='Fixed')

# ## Create the solution setup
#
# Create a new setup, validate and analyze

mech_setup = mech.create_setup()
mech.validate_simple()
mech.analyze()

# ## Post-processing
#
# Create postprocessing surface plots of equivalent stress and displacement magnitude for all model objects.

plot_stress = mech.post.create_fieldplot_surface(
    assignment=mech.modeler.object_list, quantity="Equivalent Stress", plot_name="Equivalent Stress")

plot_displ = mech.post.create_fieldplot_surface(
    assignment=mech.modeler.object_list, quantity="Mag_Displacement", plot_name="Mag_Displacement")

# ## Release AEDT

ipk.save_project()
ipk.release_desktop()

# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()

