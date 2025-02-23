# # Dipole antenna
#
# This example shows how to use PyAEDT to create a dipole antenna in HFSS
# and postprocess results.
#
# Keywords: **HFSS**, **modal**, **antenna**, **3D components**, **far field**.

# ## Perform imports and define constants
#
# Perform required imports.

import os
import tempfile
import time

import ansys.aedt.core

# Define constants.

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT

d = ansys.aedt.core.launch_desktop(
    AEDT_VERSION, non_graphical=NG_MODE, new_desktop=True
)

# ## Launch HFSS
#
# Create an HFSS design.

project_name = os.path.join(temp_folder.name, "dipole.aedt")
hfss = ansys.aedt.core.Hfss(
    version=AEDT_VERSION, project=project_name, solution_type="Modal"
)

# ## Define variable
#
# Define a variable for the dipole length.

hfss["l_dipole"] = "13.5cm"

# ## Get 3D component from system library
#
# Get a 3D component from the ``syslib`` directory. For this example to run
# correctly, you must get all geometry parameters of the 3D component or, in
# case of an encrypted 3D component, create a dictionary of the parameters.

compfile = hfss.components3d["Dipole_Antenna_DM"]
geometryparams = hfss.get_components3d_vars("Dipole_Antenna_DM")
geometryparams["dipole_length"] = "l_dipole"
hfss.modeler.insert_3d_component(compfile, geometryparams)

# ## Create boundaries
#
# Create an open region.

hfss.create_open_region(frequency="1GHz")

# ## Create setup

setup = hfss.create_setup("MySetup")
setup.props["Frequency"] = "1GHz"
setup.props["MaximumPasses"] = 1


# ## Run simulation

hfss.analyze_setup(name="MySetup", cores=NUM_CORES)

# ### Postprocess
#
# Plot s-parameters and far field.

hfss.create_scattering("MyScattering")
variations = hfss.available_variations.nominal_w_values_dict
variations["Freq"] = ["1GHz"]
variations["Theta"] = ["All"]
variations["Phi"] = ["All"]
hfss.post.create_report(
    "db(GainTotal)",
    hfss.nominal_adaptive,
    variations,
    primary_sweep_variable="Theta",
    context="3D",
    report_category="Far Fields",
)

# Create a far field report.

new_report = hfss.post.reports_by_category.far_field(
    "db(RealizedGainTotal)", hfss.nominal_adaptive, "3D"
)
new_report.report_type = "3D Polar Plot"
new_report.secondary_sweep = "Phi"
new_report.variations["Freq"] = ["1000MHz"]
new_report.create("Realized3D")

# This code generates a 2D plot.

hfss.field_setups[2].phi_step = 90
new_report2 = hfss.post.reports_by_category.far_field(
    "db(RealizedGainTotal)", hfss.nominal_adaptive, hfss.field_setups[2].name
)
new_report2.variations = variations
new_report2.primary_sweep = "Theta"
new_report2.create("Realized2D")

# Get solution data using the ``new_report`` object and postprocess or plot the
# data outside AEDT.

solution_data = new_report.get_solution_data()
solution_data.plot()

# Generate a far field plot by creating a postprocessing variable and assigning
# it to a new coordinate system. You can use the ``post`` prefix to create a
# postprocessing variable directly from a setter, or you can use the ``set_variable()``
# method with an arbitrary name.

hfss["post_x"] = 2
hfss.variable_manager.set_variable(name="y_post", expression=1, is_post_processing=True)
hfss.modeler.create_coordinate_system(origin=["post_x", "y_post", 0], name="CS_Post")
hfss.insert_infinite_sphere(custom_coordinate_system="CS_Post", name="Sphere_Custom")

# ## Retrieve solution data
#
# You can also process solution data using Python libraries like Matplotlib.

new_report = hfss.post.reports_by_category.far_field(
    "GainTotal", hfss.nominal_adaptive, "3D"
)
new_report.primary_sweep = "Theta"
new_report.far_field_sphere = "3D"
new_report.variations["Freq"] = ["1000MHz"]
solutions = new_report.get_solution_data()

# Generate a 3D plot using Matplotlib.

solutions.plot_3d()

# Generate a far fields plot using Matplotlib.

new_report.far_field_sphere = "Sphere_Custom"
solutions_custom = new_report.get_solution_data()
solutions_custom.plot_3d()

# Generate a 2D plot using Matplotlib where you specify whether it is a polar
# plot or a rectangular plot.

solutions.plot(formula="db20", is_polar=True)

# ## Retrieve far-field data
#
# After the simulation completes, the far
# field data is generated port by port and stored in a data class. You can use this data
# once AEDT is released.

ffdata = hfss.get_antenna_data(
    sphere="Sphere_Custom",
    setup=hfss.nominal_adaptive,
    frequencies=1
)

# ## Generate 2D cutout plot
#
# Generate a 2D cutout plot. You can define the Theta scan
# and Phi scan.

ffdata.farfield_data.plot_cut(
    primary_sweep="theta",
    secondary_sweep_value=0,
    quantity="RealizedGain",
    title="FarField",
    quantity_format="dB20",
    is_polar=True,
)

# ## Release AEDT

hfss.save_project()
d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files.
# The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
