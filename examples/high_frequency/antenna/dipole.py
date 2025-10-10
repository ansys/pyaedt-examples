# # Dipole antenna
#
# This example demonstrates how to create and analyze a half-wave dipole
# antenna in HFSS.
#
# Keywords: **HFSS**, **antenna**, **3D component**, **far field**.

# ## Prerequisites
#
# ### Perform imports
#
# Import the packages required to run this example.

# +
import os
import tempfile
import time

from ansys.aedt.core import Hfss
# -

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in this notebook cleans up the temporary folder. If you want to
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
# The dipole length can be modified by changing the
# parameter ``l_dipole`` to tune the resonance frequency.
#
# The dipole will nominally be resonant at the half-wavelength frequency:
# $$
# l = \lambda / 2 = \frac{c_0}{2f}
# $$

hfss["l_dipole"] = "10.2cm"
component_name = "Dipole_Antenna_DM"
freq_range = ["1GHz", "2GHz"]      # Frequency range for analysis and post-processing.
center_freq = "1.5GHz"             # Center frequency
freq_step = "0.5GHz"


# ### Insert the dipole antenna model
#
# The 3D component "Dipole_Antenna_DM" will be inserted from
# the built-in ``syslib`` folder. The full path to the 3D components
# can be retrieved from ``hfss.components3d``.
#
# The component is inserted using the method
# ``hfss.modeler.insert_3d_component()``.
#
#   - The first argument passed to ``insert_3d_component()``
#     is the full path and name of the
#       ``*.a3dcomp`` file.
#   - The second argument is a ``dict`` whose keys are the names of the parameters
#     accessible in the 3D component. In this case, we assign the
#     dipole length, ``"l_dipole"`` to the 3D Component
#     parameter ``dipole_length`` and leave other parameters unchanged.

component_fn = hfss.components3d[component_name]          # Full file name.
comp_params = hfss.get_component_variables(component_name)  # Retrieve dipole parameters.
comp_params["dipole_length"] = "l_dipole"                 # Update the dipole length.
hfss.modeler.insert_3d_component(component_fn, geometry_parameters=comp_params)

# ### Create the 3D domain region
#
# An open region object places a an airbox around the dipole antenna
# and assigns a radiation boundary to the outer surfaces of the region.

hfss.create_open_region(frequency=center_freq)

# ### Specify the solution setup
#
# The solution setup defines parameters that govern the HFSS solution process. This example demonstrates
# how to adapt the solution mesh simultaneously at two frequencies.
# - ``"MaximumPasses"`` specifies the maximum number of passes used for automatic
#   adaptive mesh refinement. In this example the solution runs very fast since only two passes
#   are used. Accuracy can be improved by increasing this value.
# - ``"MultipleAdaptiveFreqsSetup"`` specifies the solution frequencies used during adaptive
#   mesh refinement. Selection of two frequencies, one above and one below the
#   expected resonance frequency help improve mesh quality at the resonant frequency.
#
# > **Note:** The parameter names used here are passed directly to the native AEDT API and therfore
# > do not adhere to [PEP-8](https://peps.python.org/pep-0008/).
#
# Both a discrete frequency sweep and an interpolating sweep are added to the solution setup.
# The discrete sweep provides access to field solution data for post-processing.
# The interpolating sweep builds the
# rational polynomial fit for the network (scattering) parameters over the
# frequency interval defined by ``RangeStart`` and
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
#
# The following cell runs the analysis in HFSS including adaptive mesh refinement and
# solution of both frequency sweeps.

setup.analyze()

# ### Postprocess
#
# Plot the return loss in Ansys Electronics Desktop (AEDT). A plot similar to the one shown here will be
# generated in the HFSS design.
#
# <img src="_static/dipole_return_loss.png" width="800">

spar_plot = hfss.create_scattering(plot="Return Loss", sweep=interp_sweep.name)

# ### Visualize far-field data
#
# Parameters passed to ``hfss.post.create_report()`` specify which quantities will be
# displayed in the HFSS design.
# Below you can see how parameters map from Python to the reporter in the AEDT user interface.
#
# <img src="_static/ff_report_ui_1.png" width="800">
# <img src="_static/ff_report_ui_2.png" width="800">
#
# > **Note:** These images were created using the 25R1 release.

variations = hfss.available_variations.nominal_values
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
# The ``hfss.post.reports_by_category`` helps simplify the syntax required to access
# post-processing capabilities. In this case, results are shown for the current
# variation. The concept of
# "variations" is essential for managing parametric solutions
# in HFSS.
#
# The argument ``sphere_name`` specifies the far-field sphere used to generate the plot.
# In this case, the far-field sphere "3D" was automatically created when HFSS was launched by
# instantiating the ``Hfss`` class.
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

# ### Retrieve solution data for post-processing in Python
#
# An instance of the ``SolutionData`` class can be created from the report by calling ``get_solution_data()``. 
# This class provides access to data for further post-processing using
# [Matplotlib](https://matplotlib.org/).

report_3d_data = report_3d.get_solution_data()
new_plot = report_3d_data.plot_3d()

# ### View cross-polarization
#
# The dipole is linearly polarized as can be seen from the comparison of $\theta$-polarized
# and $\phi$-polarized "realized gain" at $\theta=90^\circ$ degrees.
# The following code creates the gain plots in AEDT.

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
