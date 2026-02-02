# # Eigenmode filter
#
# This example shows how to use PyAEDT to automate the Eigenmode solver in HFSS.
# Eigenmode analysis can be applied to open radiating structures
# using an absorbing boundary condition. This type of analysis is useful for
# determining the resonant frequency of a geometry or an antenna, and it can be used to refine
# the mesh at the resonance, even when the resonant frequency of the antenna is unknown.
#
# The challenge posed by this method is to identify and filter non-physical modes
# that result from reflection at the boundaries of the finite element domain.
# Non-physical modes can be identified and removed
# based on the very low quality factor.
#
# The general approach to calculate eigenmodes in HFSS relies on
# specification of a lower frequency bound for the search
# range. If modes are to be determined over a wide bandwith,
# the large number of modes being sought can increase compute time, becomming
# inefficient as the total number of modes increases. A manual
# iterative search may be
# required to determine all modes over a wide bandwidth.
#
# The following example shows how to automate the efficient
# calculation of physical modes over
# a wide bandwidth for open structures.
#
# This approach addresses two key challenges:
#   1. The non-physical modes due to truncation of the FEM domain are removed.
#   2. Modes are efficiently calculated over a wide bandwidth.
#
# Keywords: **HFSS**, **Eigenmode**, **resonance**.

# ## Prerequisites
#
# ### Perform imports

# +
from pathlib import Path
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_file
# -

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# # Model Preparation
#
# ### Download the model
#
# Download the 3D component that is needed to run the example.

project_path = download_file(
    "eigenmode", "emi_PCB_house.aedt", temp_folder.name
)

# ### Launch Ansys Electronics Desktop (AEDT)
#
# Create an HFSS design.

hfss = ansys.aedt.core.Hfss(
    project=project_path,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ### Define parameters for the eigenmode search
#
#  - ``num_modes``: Number of modes to be sought during each iteration. HFSS limits the
#    maximum number of modes to 20. In practice, fewer than 10 modes should be used
#    for the search to improve simulation time during the search.
#  - ``fmin``: The minimum frequency for the global search in GHz.
#  - ``fmax``: The maximum frequency for the global search (GHz). When a mode is found having
#    a frequency greater than or equal to this value, the iterations end.
#  - ``limit``: The lower bound on quality factor. Modes having a lower quality factor
#    are assumed to be non-physical and are filtered from the results.

num_modes = 6
fmin = 1
fmax = 2
limit = 10
resonance = {}

# ### Eigenmode search function
#
# The function ``find_resonance()`` defines the setup to use for eigenmode
# analysis, solves the design using the setup and returns the frequencies and quality
# factor for a limited number of modes.
# The function will be used later in this example inside a ``while``
# loop to extract all physical resonant modes for a metal enclosure
# over a wide bandwidth.


def find_resonance():
    # Setup creation
    next_min_freq = f"{next_fmin} GHz"
    setup_name = f"em_setup{setup_nr}"
    setup = hfss.create_setup(setup_name)
    setup.props["MinimumFrequency"] = next_min_freq
    setup.props["NumModes"] = num_modes
    setup.props["ConvergeOnRealFreq"] = True
    setup.props["MaximumPasses"] = 10
    setup.props["MinimumPasses"] = 3
    setup.props["MaxDeltaFreq"] = 5

    # Analyze the Eigenmode setup
    hfss.analyze_setup(setup_name, cores=NUM_CORES, use_auto_settings=True)

    # Get the Q and real frequency of each mode
    eigen_q_quantities = hfss.post.available_report_quantities(
        quantities_category="Eigen Q"
    )
    eigen_mode_quantities = hfss.post.available_report_quantities()
    data = {}
    for i, expression in enumerate(eigen_mode_quantities):
        eigen_q_value = hfss.post.get_solution_data(
            expressions=eigen_q_quantities[i],
            setup_sweep_name=f"{setup_name} : LastAdaptive",
            report_category="Eigenmode",
        )
        eigen_mode_value = hfss.post.get_solution_data(
            expressions=expression,
            setup_sweep_name=f"{setup_name} : LastAdaptive",
            report_category="Eigenmode",
        )
        data[i] = [eigen_q_value.get_expression_data(formula="real")[0],
                   eigen_mode_value.get_expression_data(formula="real")[0]]

    print(data)
    return data

# ### Automate the search for eigenmodes
#
# Initialize varibles for the ``while`` loop:

next_fmin = fmin  # Lowest frequency for the eigenmode search
setup_nr = 1      # Current iteration in the search loop.

# Run the search for all physical modes.

# +
while next_fmin < fmax:
    output = find_resonance()
    next_fmin = output[len(output) - 1][1] / 1e9
    setup_nr += 1
    cont_res = len(resonance)
    for q in output:
        if output[q][0] > limit:
            resonance[cont_res] = output[q]
            cont_res += 1

resonance_frequencies = [f"{resonance[i][1] / 1e9:.5} GHz" for i in resonance]
print(str(resonance_frequencies))
# -

# Display the model.

hfss.modeler.fit_all()
hfss.plot(
    show=False,
    output_file=Path(hfss.working_directory) / "Image.jpg",
    plot_air_objects=False,
)

# ## Finish
#
# ### Save the project

hfss.save_project()
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
