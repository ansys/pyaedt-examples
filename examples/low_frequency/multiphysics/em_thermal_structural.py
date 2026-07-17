# # Electro-Thermal-Structural Analysis
#
#
#
# This example uses PyAEDT to open a copper  busbar model in Q3D and perform stepped DC analyses to be passed to a
# transient thermal process with 2-way coupling a restart enabled.
# the examples implements the following steps:
#
# 1. Import packages and load a Q3D project containing a  DC Conduction design.
# 2. Run the simulation for a parametric value for the source.
# 3. Plot the resulting mesh, current density magnitude and ohmic losses.
# 4. Enables two-way coupling with temperature feedback from Icepak to Q3D within each substep.
# 5. Complete the transient thermal simulation.
# 6. Create a subsequent Structural analysis with the final temperateures averaged over the objects as thermal loads.
# 7. Run the structural analysis.
# 8. Visualize the resulting Deformation
#
# Keywords: **Multiphysics**, **Q3D**, **Icepak**, **Icepak FEA Structural**.

# ## Prerequisites
#
# ### Perform imports

# +
import os
import tempfile
import time
import numpy as np
from pathlib import Path
from itertools import chain

import ansys.aedt.core  # Interface to Ansys Electronics Desktop
from ansys.aedt.core.generic.aedt_constants import IcepakFeaConstants
from ansys.aedt.core.examples.downloads import download_file
# -

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2026.1"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.


# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
results_script_folder = Path(temp_folder.name)
data_folder = Path(download_file(r"pyaedt/busbar_3_physics_q3d_icepak_icepakfea", local_path=temp_folder.name))

#
# ### Launch an AEDT instance and load Q3D project.
#

q3d_project_name = "Q3D_Busbar.aedt"
q3d_design_name = "Q3DDesign"
icepak_design_name = "Icepak"
initial_project_name = data_folder / q3d_project_name
project_name = os.path.join(temp_folder.name, "Busbars - Thermal Transient Coupling")

q3d = ansys.aedt.core.Q3d(
    project=initial_project_name,
    design=q3d_design_name,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
)

q3d.save_project(project_name + ".aedt")

# ## Model Preparation
#
# ### Create temperature dependent materials
#
# Duplicate copper and add temperature dependent electrical conductivity

cu_resistivity_temp_coefficient = 0.000001
target_material = "copper"

cu_temp = q3d.materials.duplicate_material(material=target_material, name="copper_temp_dep")
cu_temp.conductivity.add_thermal_modifier_free_form("1.0/(1.0+{}*(Temp-20))".format(cu_resistivity_temp_coefficient))

all_objects = q3d.modeler.object_names

matching_objects = []

for obj_name in all_objects:
    mat = q3d.modeler[obj_name].material_name
    if mat and mat.lower() == target_material.lower():
        matching_objects.append(obj_name)

q3d.assign_material(assignment=matching_objects, material=cu_temp.name)

# ### Set object temperature and enable feedback

q3d.modeler.set_objects_temperature(assignment=matching_objects,
                                    ambient_temperature=20)

# ### Define excitations

time_list = [0, 6, 7, 12] #s
current_list = [100, 100, 50, 50] #A

q3d_design_var_name = 'I_DC'
q3d[q3d_design_var_name]= str(current_list[0])+"A"

#
# ### Create Icepak target design
#

q3d.create_em_target_design(design="Icepak", design_setup="Natural")
ipk = ansys.aedt.core.Icepak()
ipk.design_name = icepak_design_name

#
# ### Define solution setup
#
# ### Thermal transient inputs for time stepping and sub cycling

end_time = 12      #s, thermal transient end time
n_steps = 6        #n. of substeps
th_time_step = 0.5 #s thermal transient time step

# ### Setup of the current value for the coupling step physical time using linear interpolation

ipk[q3d_design_var_name] = str(int(np.interp(end_time/n_steps,time_list,current_list)))+"A"

# ## Thermal transient simulation with sub cycling
#
# ### Coupling step #1 start

ipk.logger.enable_desktop_log()
ipk.logger.add_message(message_type=0, message_text="Solving substep n.1 of " + str(n_steps), level="Project", proj_name=ipk.project_name)

em_name = q3d.design_name

# ### Icepak transient simulation and time stepping setup

ipk.solution_type = "Transient"
setup = ipk.setups[0]
ipk.save_project()
setup.props["Stop Time"] = str(end_time/n_steps)+"s"
setup.props["Time Step"] = str(th_time_step)+"s"
setup.props["N Steps"] = 1

# ### Get the list of object names included in the EM Loss

for x in range(len(ipk.boundaries)):
    if ipk.boundaries[x].type == "EM Loss" or ipk.boundaries[x].type == "EMLoss":
        emloss = ipk.boundaries[x]

obj = emloss.properties["Assignment"]
obj_names = obj.split(", ")
emloss.delete()

# ### Re-creation of the EM Loss with mapping of the current pulse parameter between Icepak and Maxwell

# With this setting, the value of the current pulse to be used in the Maxwell simulation is driven from Icepak

ipk.assign_em_losses(design=em_name, setup="Setup1", assignment=obj_names, parameters=[q3d_design_var_name], sweep="LastAdaptive", q3d_loss_type="DCVolOrACSurfLoss", map_frequency="1kHz")

ipk.assign_2way_coupling(setup="Setup1", number_of_iterations=2)

ipk.logger.add_message(0, "Current value " + str(ipk[q3d_design_var_name]), level="Project", proj_name=ipk.project_name)

#
# ## Run analysis
#
# ### Run of the simulation for the current coupling step

ipk.analyze()

ipk.logger.add_message(0, "Substep n.1 of " + str(n_steps) + " completed", level="Project", proj_name=ipk.project_name)

# ### Additional coupling steps loop definition

for n in range(n_steps-1):

    step = n + 2
    ipk.logger.add_message(0, "Solving substep n." + str(step) + " of " + str(n_steps), level="Project", proj_name=ipk.project_name)

# ### Duplicate Icepak design from previous substep and enable the restart
#
# The current pulse variable (q3d_design_var_name) in the Icepak restart needs to be mapped to the same value used in the previous substep so that it doesn't trigger a new solution of the source Icepak design
# The "copy fields from source" makes a copy of the results from the source design to the target design, so that at the end only the last Icepak design can be kept

    ipk_name = ipk.design_name
    ipk.duplicate_design(ipk_name)
    ipk = ansys.aedt.core.Icepak()
    ipk.cleanup_solution()
    ipk.save_project()

    setup = ipk.setups[0]
    setup.props["Import Start Time"] = True
    setup.props["Copy Fields From Source"] = True
    setup.start_continue_from_previous_setup(design=ipk_name, solution=setup.name + " : Transient", map_variables_by_name=False, parameters={q3d_design_var_name:str(int(np.interp((step-1)*end_time/n_steps,time_list,current_list)))+"A"})
    setup.props["Stop Time"] = str(step*end_time/n_steps)+"s"

# ### Setup of the current pulse value for the current coupling step physical time using linear interpolation

    ipk[q3d_design_var_name] = str(int(np.interp(step*end_time/n_steps, time_list, current_list))) + "A"
    ipk.logger.add_message(0, "Current value " + str(ipk[q3d_design_var_name]), level="Project", proj_name=ipk.project_name)

# ### Run of the simulation for the current coupling step

    ipk.analyze()
    ipk.logger.add_message(0, "Substep n." + str(step) + " of " + str(n_steps) + " completed", level="Project", proj_name=ipk.project_name)

# ### Remove all the Icepak designs except the last one (all the field data are copied into the last Icepak design)

desktop = ansys.aedt.core.Desktop()
designs = desktop.design_list()
designs.remove(q3d_design_name)
designs.remove(ipk.design_name)

for design in designs:
    ipk.delete_design(design)

# ## Icepak Thremal Transient Postprocess
#
# Access the FieldSummary functionality

field_sum = ipk.post.create_field_summary()

# Compute time steps

t_step = end_time/n_steps
time_substeps =list(range(0,int((end_time+t_step)*1e9),int(end_time/n_steps*1e9)))

# Convert time steps values to strings to be passed to filed sum calculations

time_substeps_str = [str(x)+'ns' for x in time_substeps]

temp_out = []

for obj_index in obj_names:
    temp_avg_dict = {
        "name": "temp_avg_"+obj_index,
        "description": "Average Temperature on given object",
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
                                                          assignment=obj_index,
                                                          name="T_avg_"+obj_index)
    report_temp = ipk.post.create_report(expressions=expr_name, primary_sweep_variable='Time')

    [field_sum.add_calculation(entity="Object", geometry="Volume",
                               geometry_name=obj_index,
                               quantity="Temperature",
                               time=t) for t in time_substeps_str]


temp_out_new = field_sum.get_field_summary_data(pandas_output=True, intrinsics="All times",
                                    variation=ipk.available_variations.variations("Setup1 : Transient", True)[0])

# Extract mean values for the varistor object at each timestep
#
temp_obj = temp_out_new.iloc[1::]['Mean'].values

# Create the array of varistor average temperatures at each time step
avg_temp_varistor = temp_obj [-(n_steps+1):]
# Take the time step at which the average temperature of the varistor reaches the maximum (worst case)
n_th_max = np.argmax(avg_temp_varistor)
# Extract the average temperature for all the objects at the n_th_max time-step
avg_temp_obj = temp_out_new.iloc[n_th_max::n_th_max+1]['Mean'].values
order_obj = temp_out_new.iloc[n_th_max::n_th_max+1]['Entity'].values

# ## Mechanical Structural Static simulation
#

q3d.create_em_target_design(design=IcepakFeaConstants.NAME)
design_list = q3d.design_list

# Assuming there is only one IcepakFEA design in the active project, select it.
ipk_fea_index = [i for i, design_list in enumerate(design_list) if 'IcepakFEA' in design_list]
mech = ansys.aedt.core.Mechanical(
	design=design_list[ipk_fea_index[0]]
)
# Change the design type
mech.solution_type="Structural"
obj_list = mech.modeler.object_list

# find how to reorder avg temp list
order_temp_map = [obj.name for obj in obj_list]

# reorder avg_temp prior to subsequent assignment and create mapping
mapping = dict(zip(order_obj, avg_temp_obj))
# reorder values according to new_order
reordered_avg_temp = [mapping[name] for name in order_temp_map]
# assign uniform temperature excitations
for t, avg in zip(obj_list, reordered_avg_temp):
    mech.assign_thermal_condition_uniform(assignment=[t.name], temperature =str(avg)+"cel", name="ThermalCond_"+t.name)

# Retrieve from Q3D the Named selections face IDs
#
named_selections = q3d.modeler.user_lists
my_faces = [named_selections[f]['List'] for f in range(len(named_selections))]
# Generate a nested list of face centers
face_centers = [[q3d.modeler.get_face_center(assignment=fid) for fid in sublist] for sublist in my_faces]
# Generate a nested list of face IDs in mechanical where fixed support need to be applied
my_mech_faces = [[mech.modeler.get_faceid_from_position(position=fpos) for fpos in sublist] for sublist in face_centers]
my_fixed = list(chain.from_iterable(my_mech_faces))
# Generate a fixed support boundary conditions
mech.assign_fixed_support(assignment=my_fixed, name='Fixed')

# Create the solution setup
mech_setup = mech.create_setup()
mech.validate_simple()
mech.analyze()

plot_stress = mech.post.create_fieldplot_surface(
    assignment=mech.modeler.object_list, quantity="Equivalent Stress", plot_name="Equivalent Stress")

plot_displ = mech.post.create_fieldplot_surface(
    assignment=mech.modeler.object_list, quantity="Mag_Displacement", plot_name="Mag_Displacement")

#
# ## Finish
#

# ### Save the project and release AEDT

mech.save_project()
mech.release_desktop()

# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.

time.sleep(3)

# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()

