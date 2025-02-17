# # Dipole antenna
#
# This example shows how to create, analyze and review simulation results for a
# half-wavelength dipole antenna in HFSS.
#
# Keywords: **HFSS**, **antenna**, **3D component**, **far field**.

# ## Prerequisites
#
# ### Perform imports

# +
import os
import tempfile
import time

from ansys.aedt.core import Hfss
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

# ### Launch HFSS
#
# Create an instance of
# the ``Hfss`` class. The Ansys Electronics Desktop will be launched
# with an active HFSS design. The ``hfss`` object is subsequently
# used to
# create and simulate the dipole antenna.

project_name = os.path.join(temp_folder.name, "dipole.aedt")
hfss = Hfss(version=AEDT_VERSION,
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


# ### Insert the dipole antenna model
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

component_fn = hfss.components3d[component_name]          # Full file name.
comp_params = hfss.get_components3d_vars(component_name)  # Retrieve dipole parameters.
comp_params["dipole_length"] = "l_dipole"                 # Update the dipole length.
hfss.modeler.insert_3d_component(component_fn, geometry_parameters=comp_params)

# ### Create the 3D domain region
#
# An open region object places a an airbox around the dipole antenna 
# and assigns a radition boundary to the outer surfaces of the region.

hfss.create_open_region(frequency=center_freq)

# ### Specify the solution setup
#
# The solution setup defines parameters that govern the HFSS solution process. This example demonstrates
# how to set up the solution to use two solution frequencies for adaptive refinement. This approach can improve solution
# efficiency for resonant structures wherein the final resonance frequency may not be known.
# - ``"MaximumPasses"`` specifies the maximum number of passes used for automatic
#   adaptive mesh refinement.
# - ``"MultipleAdaptiveFreqsSetup"`` specifies the solution frequencies at which
#   the antenna will be solved during adaptive mesh refinement. For resonant structures
#   it is advisable to select at least two frequencies, one above and one below the
#   expected resonance frequency.
#
# > **Note:** The parameter names used here are passed directly to the native AEDT API and therfore
# > do not adhere to [PEP-8](https://peps.python.org/pep-0008/). Readability and adherence to
# > PEP-8 will improve as PyAEDT evolves.
#
# Both a discrete frequency sweep and an interpolating sweep are added to the solution setup. The discrete
# sweep provides access to field solution data for post-processing. The interpolating sweep builds the
# rational fit of network parameters over the frequency interval defined by ``RangeStart`` and
# ``RangeEnd``.  The solutions from the discrete sweep are used as the starting
# solutions for the interpolating sweep.

# +
setup = hfss.create_setup(name="MySetup", MultipleAdaptiveFreqsSetup=freq_range, MaximumPasses=2)

disc_sweep = setup.add_sweep(name="DiscreteSweep", sweep_type="Discrete",
                             RangeStart=freq_range[0], RangeEnd=freq_range[1], RangeStep=freq_step,
                             SaveFields=True)
interp_sweep = setup.add_sweep(name="InterpolatingSweep", sweep_type="Interpolating",
                               RangeStart=freq_range[0], RangeEnd=freq_range[1],
                               SaveFields=False)
# -

# ### Run simulation

setup.analyze()

# ### Postprocess
#
# Plot s-parameters and far field.

#spar_plot = hfss.post.create_report_from_configuration(input_file=spar_template,solution_name=interp_sweep.name)
spar_plot = hfss.create_scattering(plot="Return Loss", sweep=interp_sweep.name)

# ### Visualize far-field data
#
# Parameters passed to ``hfss.post.create_report()`` specify the details of the report that will be created in AEDT.
# Below you can see how the parameters map to the reporter user interface.
#
# <img src="_static/ff_report_ui_1.png" width="800">
# <img src="_static/ff_report_ui_2.png" width="800">
#
# > **Note:** These images are from the 24R2 release

variations = hfss.available_variations.nominal_w_values_dict
variations["Freq"] = [center_freq]
variations["Theta"] = ["All"]
variations["Phi"] = ["All"]
elevation_ffd_plot = hfss.post.create_report(expressions="db(GainTheta)",
                                             setup_sweep_name=disc_sweep.name,
                                             variations=variations,
                                             primary_sweep_variable="Theta",
                                             context="Elevation",           # Far-field setup is pre-defined.
                                             report_category="Far Fields",
                                             plot_type="Radiation Pattern",
                                             plot_name="Elevation Gain (dB)"
                                            )
elevation_ffd_plot.children["Legend"].properties["Show Trace Name"] = False
elevation_ffd_plot.children["Legend"].properties["Show Solution Name"] = False

# ### Create a far-field report
#
# The ``hfss.post.reports_by_category`` provides direct access to specific post-processing capabilities and can simplify
# syntax. Note that the variation is not passed to the method. In this case, the currently active variation will be used. The concept of a "variation" is useful when you generate multiple parametric solutions for a single HFSS design.
#
# The argument ``sphere_name`` specifies the far-field sphere used to generate the plot. In this case, the far-field sphere "3D" was automatically created when HFSS was launched by instantiating the ``Hfss`` class.
#
# <img src="_static/sphere_3d.png" width="550">

# +
report_3d = hfss.post.reports_by_category.far_field("db(RealizedGainTheta)",
                                                      disc_sweep.name,
                                                      sphere_name="3D",
                                                      Freq= [center_freq],)

report_3d.report_type = "3D Polar Plot"
report_3d.create(name="Realized Gain (dB)")
# -

# ### Retrieve solution data for external post-processing
#
# An instance of the ``SolutionData`` class can be created from the report by calling the ``get_solution_data()`` 
# method. This class makes data accessible for further post-processing using
# [Matplotlib](https://matplotlib.org/) and is used, for example, to create plots that can be viewed
# directly in the browser or in PDF reports as shown below.

report_3d_data = report_3d.get_solution_data()
new_plot = report_3d_data.plot_3d()

# ### View Cross-Polarization
#
# The dipole is linearly polarized as can be seen from the comparison of $\theta$-polarized
# and $\phi$-polarized gain at $\theta=90\degree$. The following code creates the gain plots
# in AEDT.

# +
xpol_expressions = ["db(RealizedGainTheta)", "db(RealizedGainPhi)"]
xpol = hfss.post.reports_by_category.far_field(["db(RealizedGainTheta)", "db(RealizedGainPhi)"],
                                                disc_sweep.name,
                                                name="Cross Polarization",
                                                sphere_name="Azimuth",
                                                Freq= [center_freq],)

xpol.report_type = "Radiation Pattern"
xpol.create(name="xpol")
xpol.children["Legend"].properties["Show Solution Name"] = False
xpol.children["Legend"].properties["Show Variation Key"] = False
# -

# The ``get_solution_data()`` method is again used to create an inline plot of cross-polarization from
# the report in HFSS.

ff_el_data = elevation_ffd_plot.get_solution_data()
ff_el_data.plot(x_label="Theta", y_label="Gain", is_polar=True)


# ### Change the antenna phase center
#
# A new coordinate system can be created for post-processing to change the phase-center for the far-field plots.
# In this example, the coordinate system is shifted by 13mm in the $+z$ direction.
#
# The ``sweep`` parameter is used here to modify the plot in AEDT by updating the ``ff_setup.properties``. 
#
# > **Note:** Properties of many PyAEDT objects can be accessed through the ``properties`` property as shown
# > here. The keywords used to access properties are documented in the native AEDT API.

# +
hfss.modeler.create_coordinate_system(origin=[0, 0, "13mm"], name="Offset_CS")
ff_setup = hfss.insert_infinite_sphere(custom_coordinate_system="Offset_CS", name="Offset")
sweep = dict(ThetaStart="-180deg", ThetaStop="180deg", ThetaStep="5deg",
             PhiStart="0deg", PhiStop="180deg", PhiStep="10deg",
             )
for key, value in sweep.items():
    ff_setup.properties[key] = value

gain_dB = hfss.post.reports_by_category.far_field(
    "dB(GainTotal)", disc_sweep.name, "3D", Freq= [center_freq],
)
# -

# ### Plot far-field outside of AEDT
#
# Again use ``get_solution_data()`` to create the far-field plot for rendering and 
# post-processing outside the Ansys Electronics Desktop.

gain_offset_data = gain_dB.get_solution_data()
gain_offset_data.plot()

# ## Release AEDT

# +
hfss.save_project()
hfss.release_desktop()

# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)
# -

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files.
# The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
