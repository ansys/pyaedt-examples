# # Dipole antenna
#
# This example shows how to create a dipole antenna in HFSS
# and view the simulation results.
#
# Keywords: **HFSS**, **modal**, **antenna**, **3D components**, **far field**.

# ## Prerequisites
#
# ### Perform imports

# +
import os
import tempfile
import time

import ansys.aedt.core
# -

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ### Create an HFSS Design
#
# Create an instance of
# the ``Hfss`` class. The Ansys Electronics Desktop will be launched
# with an active HFSS design. The ``hfss`` object is subsequently
# used to
# create and simulate the dipole antenna.

project_name = os.path.join(temp_folder.name, "dipole.aedt")
hfss = ansys.aedt.core.Hfss( version=AEDT_VERSION,
                            non_graphical=NG_MODE,
                            project=project_name,
                            new_desktop=True,
                            solution_type="Modal",
                            )

# ## Model Preparation
#
# ### Define the dipole length as a parameter
#
# The parameter ``l_dipole`` can be modified to change
# the length of the dipole antenna.

hfss["l_dipole"] = "10.2cm"
component_name = "Dipole_Antenna_DM"
freq_range = ["1GHz", "2GHz"]      # Frequency range for analysis and post-processing.
center_freq = "1.5GHz"             # Center frequency
freq_step = "0.5GHz"


# ### Insert the dipole antenna
#
# The 3D component "Dipole_Antenna_DM" will be inserted from
# the built-in ``syslib`` folder. The full path to 3D components
# can be retrieved from 
# ``hfss.components3d`` which provides the full path to all
# 3D components located in the _syslib_ or _userlib_.
#
# The component is inserted using the method
# ``hfss.modeler.insert_3d_component()``.
#
#   - The first argument passed to ``insert_3d_component()`` 
#     full name of the
#       ``*.a3dcomp`` file.
#   - The second argument is a ``dict`` whose keys are the parameter names
#     defined in the 3D component. In this case, we pass the
#     dipole length, ``"l_dipole"`` as the value of ``dipole_length``
#     and leave other values unchanged.

compfile = hfss.components3d[component_name]              # Full file name.
comp_params = hfss.get_components3d_vars(component_name)  # Dict of name/value pairs.
comp_params["dipole_length"] = "l_dipole"                 # Update the dipole length.
hfss.modeler.insert_3d_component(compfile, geometry_parameters=comp_params)

# ### Define the solution domain
#
# An open region object places a an airbox around the dipole antenna 
# and assigns a radition boundary to the outer surfaces of the region.

hfss.create_open_region(frequency=center_freq)

# ### Specify the solution setup
#
# The solution setup is used to specify parameters used to generate the HFSS solution:
# - ``"Frequency"`` specifies the solution frequency used
#   to adapt the finite element mesh.
# - ``"MaximumPasses"`` specifies the maximum number of passes used for automatic
#   adaptive mesh refinement.
# - ``"MultipleAdaptiveFreqsSetup"`` specifies the solution frequencies at which
#   the antenna will be solved during adaptive mesh refinement. For resonant structures
#   it is advisable to select at least two frequencies, one above and one below the
#   expected resonance frequency.

# +
setup = hfss.create_setup(name="MySetup", MultipleAdaptiveFreqsSetup=freq_range, MaximumPasses=2)

disc_sweep = setup.add_sweep(name="DiscreteSweep", sweep_type="Discrete",
                             RangeStart=freq_range[0], RangeEnd=freq_range[1], RangeStep=freq_step,
                             SaveFields=True)
interp_sweep = setup.add_sweep(name="InterpolatingSweep", sweep_type="Interpolating",
                               RangeStart=freq_range[0], RangeEnd=freq_range[1])
# -

# ### Run simulation

hfss.analyze_setup(name="MySetup", cores=NUM_CORES)

# ### Postprocess
#
# Plot s-parameters and far field.

hfss.create_scattering("MyScattering", sweep=interp_sweep.name)
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
    "db(RealizedGainTotal)", disc_sweep, "3D", Freq=center_freq,
)
new_report.report_type = "3D Polar Plot"
new_report.secondary_sweep = "Phi"
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
    frequencies=["1000MHz"],
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
