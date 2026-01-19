# # HFSS-Mechanical MRI analysis
#
# This example uses a coil tuned to 63.8 MHz to determine the temperature
# rise in a gel phantom near an implant given a background SAR of 1 W/kg.
#
# Here is the workflow:

# Step 1: Simulate the coil loaded by the empty phantom:
# Scale input to coil ports to produce desired background SAR of 1 W/kg at the location
# that is to contain the implant.

# Step 2: Simulate the coil loaded by the phantom containing the implant in the proper location:
# View SAR in the tissue surrounding implant.

# Step 3: Thermal simulation:
# Link HFSS to the transient thermal solver to find the temperature rise in the tissue near the implant
# versus the time.
#
# Keywords: **multiphysics**, **HFSS**, **Mechanical AEDT**, **Circuit**.

# ## Perform imports and define constants
# Perform required imports.

# +
import os.path
import tempfile
import time

from ansys.aedt.core import Hfss, Icepak, Mechanical
from ansys.aedt.core.examples import downloads
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


# ## Load project
#
# Open AEDT and the ``background_SAR.aedt`` project. This project
# contains the phantom and airbox. The phantom consists of two objects: ``phantom`` and ``implant_box``.
#
# Separate objects are used to selectively assign mesh operations.
# Material properties defined in  this project already contain electrical and thermal properties.

project_path = downloads.download_file(source="mri", local_path=temp_folder.name)
project_name = os.path.join(project_path, "background_SAR.aedt")
hfss = Hfss(
    project=project_name,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Insert 3D component
#
# The MRI coil is saved as a separate 3D component.

# ‒ 3D components store geometry (including parameters),
# material properties, boundary conditions, mesh assignments,
# and excitations.
# ‒ 3D components make it easy to reuse and share parts of a simulation.

component_file = os.path.join(project_path, "coil.a3dcomp")
hfss.modeler.insert_3d_component(input_file=component_file)

# ## Define convergence criteria
#
#  On the **Expression Cache** tab, define additional convergence criteria for self
#  impedance of the four coil ports.

# Set each of these convergence criteria to 2.5 ohm.
# This example limits the number of passes to two to reduce simulation time.

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

# ## Edit sources
#
# The 3D component of the MRI coil contains all the ports,
# but the sources for these ports are not yet defined.
# Browse to and select the ``sources.csv`` file.
# The sources in this file were determined by tuning the coil at 63.8 MHz.
# Notice that ``input_scale`` is a multiplier that lets you quickly adjust the coil excitation power.

hfss.edit_source_from_file(os.path.join(project_path, "sources.csv"))

# ## Run simulation
#
# Save and analyze the project.

hfss.save_project(file_name=os.path.join(project_path, "solved.aedt"))
hfss.analyze(cores=NUM_CORES)

# ## Plot SAR on cut plane in phantom
#
# Ensure that the SAR averaging method is set to ``Gridless``.
# Plot ``Average_SAR`` on the global YZ plane.
# Draw ``Point1`` at the origin of the implant coordinate system.

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

# ## Adjust input Power to MRI coil
#
# Adjust the MRI coil’s input power so that the average SAR at ``Point1`` is 1 W/kg.
# Note that the SAR and input power are linearly related.
#
# To determine therequired input, calculate
# ``input_scale = 1/AverageSAR`` at ``Point1``.

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

# ## Analyze phantom with implant
#
# Import the implant geometry.
# Subtract the rod from the implant box.
# Assign titanium to the imported object rod.
# Analyze the project.

# +
hfss.modeler.import_3d_cad(os.path.join(project_path, "implant_rod.sat"))

hfss.modeler["implant_box"].subtract(tool_list="rod", keep_originals=True)
hfss.modeler["rod"].material_name = "titanium"
hfss.analyze(cores=NUM_CORES)
hfss.save_project()
# -

# ## Run a thermal simulation
#
# Initialize a new Mechanical transient thermal analysis.
# This type of analysis is available in AEDT in 2023 R2 and later as a beta feature.

mech = Mechanical(solution_type="Transient Thermal", version=AEDT_VERSION)

# ## Copy geometries
#
# Copy bodies from the HFSS project. The 3D component is not copied.

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

# ## Create setup
#
# Create a setup and edit properties.

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

# ## Analyze project
#
# Analyze the Mechanical project.

mech.analyze(cores=NUM_CORES)

# ## Plot fields
#
# Plot the temperature on cut plane.
# Plot the temperature on the point.

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
    variations=["10s", "30s"],
    filter_objects=["implant_box"],
    show=False,
)
# -

# ## Run a new thermal simulation
#
# Initialize a new Icepak transient thermal analysis.

ipk = Icepak(solution_type="Transient", version=AEDT_VERSION)
ipk.design_solutions.problem_type = "TemperatureOnly"

# ## Copy geometries
#
# Copy bodies from the HFSS project. The 3D component is not copied.

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

# ## Create setup
#
# Create a setup and edit properties.
# Simulation takes 30 seconds.

# +
setup = ipk.create_setup()

setup.props["Stop Time"] = 30
setup.props["N Steps"] = 2
setup.props["Time Step"] = 5
setup.props["Convergence Criteria - Energy"] = 1e-12
# -

# ## Create mesh region
#
# Create a mesh region and change the accuracy level to 4.

bound = ipk.modeler["implant_box"].bounding_box
mesh_box = ipk.modeler.create_box(
    origin=bound[:3],
    sizes=[bound[3] - bound[0], bound[4] - bound[1], bound[5] - bound[2]],
)
mesh_box.model = False
mesh_region = ipk.mesh.assign_mesh_region([mesh_box.name])
mesh_region.UserSpecifiedSettings = False
mesh_region.update()
mesh_region.properties["Mesh Resolution"] = 4

# ## Create point monitor
#
# Create a point monitor.

ipk.modeler.set_working_coordinate_system("implant")
ipk.monitor.assign_point_monitor(point_position=[0, 0, 0], monitor_name="Point1")
ipk.assign_openings(ipk.modeler["Region"].top_face_z)
# -

# ## Release AEDT
#
# Release AEDT and close the example.

hfss.save_project()
hfss.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``. If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
