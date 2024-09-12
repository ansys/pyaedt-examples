# # FSS unit cell simulation
#
# This example shows how to use PyAEDT to model and simulate a unit cell
# for a frequency-selective surface in HFSS.
#
# Keywords: **HFSS**, **FSS**, **Floquet**.

# ## Perform imports and define constants
#
# Perform required imports.

import os
import tempfile
import time

import ansys.aedt.core

# Define constants.

AEDT_VERSION = "2024.2"
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT

project_name = os.path.join(temp_folder.name, "FSS.aedt")
d = ansys.aedt.core.launch_desktop(
    AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Launch HFSS
#
# Create an HFSS design.

hfss = ansys.aedt.core.Hfss(
    version=AEDT_VERSION, project=project_name, solution_type="Modal"
)

# ## Define variable
#
# Define a variable for the 3D component.

hfss["patch_dim"] = "10mm"

# ## Set up model
#
# Download the 3D component from the example data and insert the 3D component.

unitcell_3d_component_path = ansys.aedt.core.downloads.download_FSS_3dcomponent(
    destination=temp_folder.name
)
unitcell_path = os.path.join(unitcell_3d_component_path, "FSS_unitcell_23R2.a3dcomp")
comp = hfss.modeler.insert_3d_component(unitcell_path)

# Assign the parameter to the 3D component.

component_name = hfss.modeler.user_defined_component_names
comp.parameters["a"] = "patch_dim"

# Create an open region along +Z direction for unit cell analysis.

# +
bounding_dimensions = hfss.modeler.get_bounding_dimension()

periodicity_x = bounding_dimensions[0]
periodicity_y = bounding_dimensions[1]

region = hfss.modeler.create_air_region(
    z_pos=10 * bounding_dimensions[2],
    is_percentage=False,
)

[x_min, y_min, z_min, x_max, y_max, z_max] = region.bounding_box
# -

# Assign the lattice pair boundary condition.

hfss.auto_assign_lattice_pairs(assignment=region.name)

# Define the Floquet port.

id_z_pos = region.top_face_z
hfss.create_floquet_port(
    assignment=id_z_pos,
    lattice_origin=[0, 0, z_max],
    lattice_a_end=[0, y_max, z_max],
    lattice_b_end=[x_max, 0, z_max],
    name="port_z_max",
    deembed_distance=10 * bounding_dimensions[2],
)

# Create a solution setup, including the frequency sweep.

setup = hfss.create_setup("MySetup")
setup.props["Frequency"] = "10GHz"
setup.props["MaximumPasses"] = 10
hfss.create_linear_count_sweep(
    setup=setup.name,
    units="GHz",
    start_frequency=6,
    stop_frequency=15,
    num_of_freq_points=51,
    name="sweep1",
    sweep_type="Interpolating",
    interpolation_tol=6,
    save_fields=False,
)

# ## Postprocess
#
# Create S-parameter reports.

# +
all_quantities = hfss.post.available_report_quantities()
str_mag = []
str_ang = []

variation = {"Freq": ["All"]}

for i in all_quantities:
    str_mag.append("mag(" + i + ")")
    str_ang.append("ang_deg(" + i + ")")

hfss.post.create_report(
    expressions=str_mag,
    variations=variation,
    plot_name="magnitude_plot",
)
hfss.post.create_report(
    expressions=str_ang,
    variations=variation,
    plot_name="phase_plot",
)
# -

# ## Save and run simulation
#
# Save and run the simulation. Uncomment the following line to run the analysis.

# hfss.analyze()
hfss.save_project()

# ## Release AEDT

hfss.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes
# all temporary files, including the project folder.

temp_folder.cleanup()
