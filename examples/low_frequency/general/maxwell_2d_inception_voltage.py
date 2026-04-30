# # Automated workflow for Inception Voltage Evaluation
#
#
# The workflow is performed following the steps
# 1. Import packages and start a Maxwell Electrostatic Simulation.
# 2. Create the simulation model.
# 3. Update Inception Voltage Parameters and perform Evaluation
# 4. Export the Results To File
# 5. Set a parametric sweep with proper Inception Voltage parameters.
# 4. Perform the evaluation on the Optimetrics sweep points and export the results.
#
# Keywords: **Electric Motor Windings**, **Electrostatic 2D**, **Inception Voltage Evaluation**

# ### Perform imports

# +
import os
import tempfile
import time
from pathlib import Path

import ansys.aedt.core  # Interface to Ansys Electronics Desktop
from ansys.aedt.core.examples.downloads import download_file

# -

# ### Define constants

AEDT_VERSION = "2026.1"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Define dictionaries

# Dictionaries contain the parameter definitions, enabling a parametric design

mat_params_dielectrics = {
    "ins_epsilon_r": "3.77",
    "dielectric_base_epsilon_r": "2.5",
}
design_params_geom = {
    "dia_wire": "1.8mm",
    "ins_thickness": "43um",
    "V_input": "904V",
}

# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
results_script_folder = Path(temp_folder.name)

# Launch an AEDT instance and insert a Maxwell 2D project.

project_name = os.path.join(temp_folder.name, "TP_Webinar_automated.aedt")
m2d = ansys.aedt.core.Maxwell2d(
    project=project_name,
    design="TwistedPair_2D",
    solution_type="Electrostatic",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)


# ## Model Preparation
#
# Description of steps used to create and prepare the model for simulation.
# Define Project Parameters

for k, v in mat_params_dielectrics.items():
    m2d["$" + k] = v

# Define Design Parameters

for k, v in design_params_geom.items():
    m2d[k] = v

# Define wire insulation material

mat_wire_insulation = m2d.materials.add_material("wire_ins")
mat_wire_insulation.update()
mat_wire_insulation.conductivity = "0"
mat_wire_insulation.permittivity = "$" + "ins_epsilon_r"

# Define dielectric base insulation material

mat_dielectric_base = m2d.materials.add_material("dielectric_base")
mat_dielectric_base.update()
mat_dielectric_base.conductivity = "0"
mat_dielectric_base.permittivity = "$" + "dielectric_base_epsilon_r"

# ### Create 2D model
#

dielectric_base_rect = m2d.modeler.create_rectangle(
    origin=["-20mm", "-(ins_thickness +dia_wire/2)", "0mm"], orientation="XY", sizes=["40mm", "-5mm"], name="dielectric_base", material="dielectric_base"
)
dielectric_base_rect.color = (255, 255, 0)
air_mesh_rect = m2d.modeler.create_rectangle(
    origin=["-1.25*abs(-(ins_thickness +dia_wire))", "-(ins_thickness +dia_wire/2)", "0"],
    orientation="XY",
    sizes=["2.5*abs(-(ins_thickness +dia_wire))", "1.25*abs(-(ins_thickness +dia_wire))"],
    name="air_mesh",
    material="vacuum",
)
air_mesh_rect.color = (128, 255, 255)
air_mesh_rect_2 = m2d.modeler.create_rectangle(
    origin=["-1.25*abs(-(ins_thickness +dia_wire/6))", "-dia_wire/3", "0"], orientation="XY", sizes=["2.5*abs(-(ins_thickness +dia_wire/6))", "2*dia_wire/3"], name="air_mesh_2", material="vacuum"
)
air_mesh_rect.color = (128, 255, 255)
tp_wire_1 = m2d.modeler.create_circle(origin=["-ins_thickness-dia_wire/2", 0, 0], orientation="XY", radius="dia_wire/2", num_sides="0", is_covered=True, name="tp_wire_1", material="copper")
tp_wire_1.color = (255, 128, 64)
ins_tp_wire_1 = m2d.modeler.create_circle(
    origin=["-ins_thickness-dia_wire/2", 0, 0], orientation="XY", radius="ins_thickness+dia_wire/2", num_sides="0", is_covered=True, name="ins_tp_wire_1", material="wire_ins"
)
ins_tp_wire_1.color = (0, 255, 0)
m2d.modeler.subtract(ins_tp_wire_1, tp_wire_1, keep_originals=True)
mirrored = m2d.modeler.duplicate_and_mirror(assignment=[tp_wire_1, ins_tp_wire_1], origin=[0, 0, 0], vector=[1, 0, 0])
tp_wire_1_mirr = m2d.modeler.get_object_from_name(mirrored[0])
ins_tp_wire_1_mirr = m2d.modeler.get_object_from_name(mirrored[1])
m2d.modeler.subtract(ins_tp_wire_1, tp_wire_1, keep_originals=True)
m2d.modeler.subtract(air_mesh_rect, [tp_wire_1, ins_tp_wire_1, tp_wire_1_mirr, ins_tp_wire_1_mirr, air_mesh_rect_2], keep_originals=True)
m2d.modeler.subtract(air_mesh_rect_2, [tp_wire_1, ins_tp_wire_1, tp_wire_1_mirr, ins_tp_wire_1_mirr], keep_originals=True)
region = m2d.modeler.create_region(["5", "100", "5", "0"])
region.material_name = "vacuum"

#
# ### Assign Voltage Excitations
#

m2d.assign_voltage(assignment=tp_wire_1.id, amplitude="V_input", name="Vinput")
m2d.assign_voltage(assignment=tp_wire_1_mirr.id, amplitude=0, name="GND")

#
# ### Assign mesh operations
#

m2d.mesh.assign_initial_mesh(surface_deviation=0.0001, normal_deviation=0.5)
m2d.mesh.assign_length_mesh(air_mesh_rect_2, inside_selection=True, maximum_length=0.005, name="mesh_air_mesh")
m2d.mesh.assign_length_mesh([ins_tp_wire_1, ins_tp_wire_1.name + "_2"], inside_selection=True, maximum_length=0.01, name="mesh_wire_ins")

#
# ### Define solution setup
#

setup_name = "MySetupAuto"
setup = m2d.create_setup(name=setup_name)
setup.props["PercentError"] = 0.1
setup.update()

#
# ## Run analysis
#

m2d.save_project()
m2d.validate_simple()
m2d.analyze_setup(name=setup_name, use_auto_settings=False, cores=NUM_CORES)

#
# ## Postprocess
#

# Generate field line traces

selected_object = m2d.modeler.get_object_from_name(ins_tp_wire_1.name)
plot = m2d.post.create_fieldplot_line_traces(
    seeding_faces=[ins_tp_wire_1.name], surface_tracing_objs=[dielectric_base_rect.name], in_volume_tracing_objs=[air_mesh_rect_2.name], plot_name="LineTracesTest"
)
plot.SeedingPointsNumber = 99
plot.LineStyle = "Solid"
plot.LineWidth = 1
plot.FractionOfMaximum = 0.01
plot.update()

#
# ## Perform inception voltage evaluation for a predefined or user defined gas
#
# Four possible scenarios are showcased. Please uncomment the approach that applies.

# ### Example 1: dry air at 1.5 bar pressure.

m2d.post.modify_inception_parameters(plot.name, gas_type=0, gas_pressure=1.5, use_inception=True)

# ### Example 2: SF6 gas at 1.9 bar pressure.

m2d.post.modify_inception_parameters(plot.name, gas_type=1, gas_pressure=1.9, use_inception=True)

#
# ### Example 3: define a proper ionization equation
#
# Here f(x) = x for demo purposes used.

my_ionization_equation = "x"
m2d.post.modify_inception_parameters(plot.name, gas_type=2, use_inception=True, streamer_constant=6.09, ionization_check=True, ionization_equation=my_ionization_equation)

# ### Example 4: user define gas  with ionization equation defined via dataset
#
# Here, a fictitious dataset for demo purposes is used
#

m2d.post.modify_inception_parameters(plot.name, gas_type=2, use_inception=True, streamer_constant=6.09, ionization_check=False, ionization_dataset=[2, 0, 0.15, 0.2, 0.4])

#
# ### Evaluate inception voltage for the given gas on all field line traces
#
# For the remainder of the analysis results as per Example 3 are used.
#

m2d.post.evaluate_inception_voltage(plot.name)

# Export inception voltage evaluation results to a TXT file

IV_FILENAME = "IV_" + "nominal" + ".txt"
file_inc_voltage_path = results_script_folder / IV_FILENAME
m2d.post.export_inception_voltage(plot.name, str(file_inc_voltage_path))

#
# ## Define Optimetrics setups from files
#

sweep_name_wire = "ParametricSweep_wire"

# Download the csv file containing the variable names and values from the [example-data]
# (https://github.com/ansys/example-data/tree/main/pyaedt) repository.

data_folder = Path(download_file(r"pyaedt/maxwell_2d_twisted_pair", local_path=temp_folder.name))
OPT_FILENAME = "ParametricSweep_wire_table_3par.csv"
param_path = data_folder / OPT_FILENAME
param_sweep = m2d.parametrics.add_from_file(str(param_path), name=sweep_name_wire)
param_sweep["SaveFields"] = True
param_sweep["CopyMesh"] = False

# Define Streamer constant corresponding to each Optimetrics sweep point (cannot be defined parametrically)

param_streamer_constant = [5.50, 5.03, 4.97, 5.74]

# Solve parametric sweep

param_sweep.analyze(cores=NUM_CORES)

# ## Optimetrics Postprocess
#

# Retrieve names and values of project and design variables

mxwl_variables = m2d.available_variations.nominal_values

# Retrieve the list of all the optimetrics variations from the setup

swept_variables = param_sweep.props["Sweeps"]["SweepDefinition"]
swept_table_var_names = []
swept_table_var_values = []
for i in range(len(swept_variables)):
    swept_table_var_names.append(swept_variables[i]["Variable"])
    swept_table_var_values.append(swept_variables[i]["Data"])
opt_variations = [swept_table_var_values] + param_sweep.props["Sweep Operations"]["add"]
opt_variations_transposed = list(map(list, zip(*opt_variations)))
opt_variations_dict = dict(zip(swept_table_var_names, opt_variations_transposed))
keys_to_update = opt_variations_dict.keys()

# Update Inception Voltage Parameters and perform the evaluation for all Optimetrics sweep points

for index_opt in range(len(opt_variations)):
    # Generate field line traces
    selected_object = m2d.modeler.get_object_from_name(ins_tp_wire_1.name)
    plot_opt = m2d.post.create_fieldplot_line_traces(
        seeding_faces=[ins_tp_wire_1.name], surface_tracing_objs=[dielectric_base_rect.name], in_volume_tracing_objs=[air_mesh_rect_2.name], plot_name="LineTracesTest_" + str(index_opt + 1)
    )
    plot_opt.SeedingPointsNumber = 99
    plot_opt.LineStyle = "Solid"
    plot_opt.LineWidth = 1
    plot_opt.FractionOfMaximum = 0.01
    plot_opt.update()

    # Apply solved variation
    mxwl_variables.update({k: opt_variations_dict[k][index_opt] for k in keys_to_update})
    m2d.apply_solved_variation(mxwl_variables)

    # Modify the inception voltage parameters - update the streamer constant
    m2d.post.modify_inception_parameters(
        plot_opt.name, gas_type=2, use_inception=True, streamer_constant=param_streamer_constant[index_opt], ionization_check=True, ionization_equation=my_ionization_equation
    )
    # Evaluate Inception Voltage and Export the results to File
    m2d.post.evaluate_inception_voltage(plot_opt.name)
    IV_FILENAME_OPT = "IV_optimetrics_" + str(index_opt + 1) + ".txt"
    file_inc_voltage_path_opt = results_script_folder / IV_FILENAME_OPT
    m2d.post.export_inception_voltage(plot_opt.name, str(file_inc_voltage_path_opt))
    index_opt = index_opt + 1

#
# ## Finish
#

# ### Save the project and release AEDT

m2d.save_project()
m2d.release_desktop()

# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.

time.sleep(3)

# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
