# # HFSS-Mechanical MRI analysis
#
# The goal of this example is to use a coil tuned to 63.8 MHz to determine the temperature
# rise in a gel phantom near an implant given a background SAR of 1 W/kg.
#
# Steps to follow
# Step 1: Simulate coil loaded by empty phantom:
# Scale input to coil ports to produce desired background SAR of 1 W/kg at location
# that will later contain the implant.
# Step 2: Simulate coil loaded by phantom containing implant in proper location:
# View SAR in tissue surrounding implant.
# Step 3: Thermal simulation:
# Link HFSS to transient thermal solver to find temperature rise in tissue near implant vs. time.
#
# Keywords: **Multiphysics**, **HFSS**, **Mechanica AEDTl**, **Circuit**.

# ## Perform required imports
# Perform required imports.

# +
import os.path
import tempfile
import time

from ansys.aedt.core import Hfss, Icepak, Mechanical, downloads

# -

# ## Define constants

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open Electronics UI when the application is launched.


# ## Create temporary directory and download files
#
# Create a temporary directory where we store downloaded data or
# dumped data.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")


# ## Project load
#
# Open ANSYS Electronics Desktop
# Open project background_SAR.aedt
# Project contains phantom and airbox
# Phantom consists of two objects: phantom and implant_box
# Separate objects are used to selectively assign mesh operations
# Material properties defined in  this project already contain electrical and thermal properties.

project_path = downloads.download_file(source="mri", destination=temp_folder.name)
project_name = os.path.join(project_path, "background_SAR.aedt")
hfss = Hfss(
    project=project_name,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Insert 3D component
#
# The MRI Coil is saved as a separate 3D Component
# ‒ 3D Components store geometry (including parameters),
# material properties, boundary conditions, mesh assignments,
# and excitations
# ‒ 3D Components make it easy to reuse and share parts of a simulation

component_file = os.path.join(project_path, "coil.a3dcomp")
hfss.modeler.insert_3d_component(input_file=component_file)

# ## Expression Cache
#
#  On the expression cache tab, define additional convergence criteria for self
#  impedance of the four coil
# ports
# ‒ Set each of these convergence criteria to 2.5 ohm
# For this demo number of passes is limited to 2 to reduce simulation time.

# +
im_traces = hfss.get_traces_for_plot(
    get_mutual_terms=False, category="im(Z", first_element_filter="Coil1_p*"
)

hfss.setups[0].enable_expression_cache(
    report_type="Modal Solution Data",
    expressions=im_traces,
    isconvergence=True,
    isrelativeconvergence=False,
    conv_criteria=2.5,
    use_cache_for_freq=False,
)
hfss.setups[0].props["MaximumPasses"] = 1
# -

# ## Edit Sources
#
# The 3D Component of the MRI Coil contains all the ports,
# but the sources for these ports are not yet defined.
# Browse to and select sources.csv.
# These sources were determined by tuning this coil at 63.8 MHz.
# Notice the “*input_scale” multiplier to allow quick adjustment of the coil excitation power.

hfss.edit_sources_from_file(os.path.join(project_path, "sources.csv"))

# ## Run Simulation
#
# Save and analyze the project.

hfss.save_project(project_file=os.path.join(project_path, "solved.aedt"))
hfss.analyze(cores=NUM_CORES)

# ## Plot SAR on Cut Plane in Phantom
#
# Ensure that the SAR averaging method is set to Gridless
# Plot averagedSAR on GlobalYZ plane
# Draw Point1 at origin of the implant coordinate system

# +
hfss.sar_setup(
    assignment=-1,
    average_sar_method=1,
    tissue_mass=1,
    material_density=1,
)
hfss.post.create_fieldplot_cutplane(
    assignment=["implant:YZ"], quantity="Average_SAR", filter_objects=["implant_box"]
)

hfss.modeler.set_working_coordinate_system("implant")
hfss.modeler.create_point(position=[0, 0, 0], name="Point1")

plot = hfss.post.plot_field(
    quantity="Average_SAR",
    assignment="implant:YZ",
    plot_type="CutPlane",
    show_legend=False,
    filter_objects=["implant_box"],
    export_path=hfss.working_directory,
    show=False,
)
# -

# ## Adjust Input Power to MRI Coil
#
# The goal is to adjust the MRI coil’s input power, so that the averageSAR at Point1 is 1 W/kg
# Note that SAR and input power are linearly related
# To determine required input, calculate
# input_scale = 1/AverageSAR at Point1

# +
sol_data = hfss.post.get_solution_data(
    expressions="Average_SAR",
    primary_sweep_variable="Freq",
    context="Point1",
    report_category="Fields",
)
sol_data.data_real()

hfss["input_scale"] = 1 / sol_data.data_real()[0]
# -

# ## Phantom with Implant
#
# Import implant geometry.
# Subtract rod from implant_box.
# Assign titanium to the imported object rod.
# Analyze the project.

# +
hfss.modeler.import_3d_cad(os.path.join(project_path, "implant_rod.sat"))

hfss.modeler["implant_box"].subtract(tool_list="rod", keep_originals=True)
hfss.modeler["rod"].material_name = "titanium"
hfss.analyze(cores=NUM_CORES)
hfss.save_project()
# -

# ## Thermal Simulation
#
# Initialize a new Mechanical Transient Thermal analysis.
# Mechanical Transient Thermal is available in AEDT from 2023 R2 as a Beta feature.

mech = Mechanical(solution_type="Transient Thermal", version=AEDT_VERSION)

# ## Copy geometries
#
# Copy bodies from the HFSS project. 3D Component will not be copied.

mech.copy_solid_bodies_from(hfss)

# ## Link sources to EM losses
#
# Link sources to the EM losses.
# Assign external convection.

exc = mech.assign_em_losses(
    design=hfss.design_name,
    setup=hfss.setups[0].name,
    sweep="LastAdaptive",
    map_frequency=hfss.setups[0].props["Frequency"],
    surface_objects=mech.get_all_conductors_names(),
)
mech.assign_uniform_convection(
    assignment=mech.modeler["Region"].faces, convection_value=1
)

# ## Create Setup
#
# Create a new setup and edit properties.

# +
setup = mech.create_setup()
# setup.add_mesh_link("backgroundSAR")
# mech.create_dataset1d_design("PowerMap", [0, 239, 240, 360], [1, 1, 0, 0])
# exc.props["LossMultiplier"] = "pwl(PowerMap,Time)"

mech.modeler.set_working_coordinate_system("implant")
mech.modeler.create_point(position=[0, 0, 0], name="Point1")
setup.props["Stop Time"] = 30
setup.props["Time Step"] = "10s"
setup.props["SaveFieldsType"] = "Every N Steps"
setup.props["N Steps"] = "2"
# -

# ## Analyze Mechanical
#
# Analyze the project.

mech.analyze(cores=NUM_CORES)

# ## Plot Fields
#
# Plot Temperature on cut plane.
# Plot Temperature on point.

# +
mech.post.create_fieldplot_cutplane(
    assignment=["implant:YZ"],
    quantity="Temperature",
    filter_objects=["implant_box"],
    intrinsics={"Time": "10s"},
)
mech.save_project()

data = mech.post.get_solution_data(
    expressions="Temperature",
    primary_sweep_variable="Time",
    context="Point1",
    report_category="Fields",
)
data.plot()

mech.post.plot_animated_field(
    quantity="Temperature",
    assignment="implant:YZ",
    plot_type="CutPlane",
    intrinsics={"Time": "10s"},
    variation_variable="Time",
    variation_list=["10s", "20s", "30s"],
    filter_objects=["implant_box"],
)
# -

# ## Thermal Simulation
#
# Initialize a new Icepak Transient Thermal analysis.

ipk = Icepak(solution_type="Transient", version=AEDT_VERSION)
ipk.design_solutions.problem_type = "TemperatureOnly"

# ## Copy geometries
#
# Copy bodies from the HFSS project. 3D Component will not be copied.

ipk.modeler.delete("Region")
ipk.copy_solid_bodies_from(hfss)

# ## Link sources to EM losses
#
# Link sources to the EM losses.
# Assign external convection.

ipk.assign_em_losses(
    design=hfss.design_name,
    setup=hfss.setups[0].name,
    sweep="LastAdaptive",
    map_frequency=hfss.setups[0].props["Frequency"],
    surface_objects=ipk.get_all_conductors_names(),
)

# ## Create Setup
#
# Create a new setup and edit properties.
# Simulation will be for 30 seconds.

# +
setup = ipk.create_setup()

setup.props["Stop Time"] = 30
setup.props["N Steps"] = 2
setup.props["Time Step"] = 5
setup.props["Convergence Criteria - Energy"] = 1e-12
# -

# ## Mesh Region
#
# Create a new mesh region and change accuracy level to 4.

bound = ipk.modeler["implant_box"].bounding_box
mesh_box = ipk.modeler.create_box(
    origin=bound[:3],
    sizes=[bound[3] - bound[0], bound[4] - bound[1], bound[5] - bound[2]],
)
mesh_box.model = False
mesh_region = ipk.mesh.assign_mesh_region([mesh_box.name])
mesh_region.UserSpecifiedSettings = False
mesh_region.Level = 4
mesh_region.update()

# ## n Point Monitor
#
# Create a new point monitor.

ipk.modeler.set_working_coordinate_system("implant")
ipk.monitor.assign_point_monitor(point_position=[0, 0, 0], monitor_name="Point1")
ipk.assign_openings(ipk.modeler["Region"].top_face_z)

# ## Analyze and plot fields
#
# Analyze the project.
# Plot Temperature on cut plane.
# Plot Temperature on monitor point.

# +
ipk.analyze(cores=NUM_CORES, tasks=4)
ipk.post.create_fieldplot_cutplane(
    assignment=["implant:YZ"],
    quantity="Temperature",
    filter_objects=["implant_box"],
    intrinsics={"Time": "0s"},
)
ipk.save_project()

data = ipk.post.get_solution_data(
    expressions="Point1.Temperature",
    primary_sweep_variable="Time",
    report_category="Monitor",
)
data.plot()
# -

# ## Release AEDT
#
# Release AEDT and close the example.

hfss.save_project()
hfss.release_desktop()
# Wait 3 seconds to allow Electronics Desktop to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Cleanup
#
# All project files are saved in the folder ``temp_folder.name``. If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
