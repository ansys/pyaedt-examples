# # Eigenmode filter
#
# This example illustrates and efficient approach to calculate eigenmode frequencies
# over a wide bandwidth for open structures using HFSS.
#
# The model is comprised of a metal chassis and a simple PCB
# inside the enclosure.
#
# <img src="_static\eigenmode\eigenmode_chassis.png" width="600">
#
# HFSS relies on
# specification of a lower frequency limit for the search5
# range. The number of desired modes must also be specified. 
#
# If performance is to be determined over a wide bandwith,
# the large number of modes can increase compute time. An
# iterative search that limits the number of modes being sought
# for each iteration improves time and memory requirements.
#
# Keywords: **HFSS**, **Eigenmode**, **resonance**.

# ## Prerequisites
#
# ### Perform imports

# +
from pathlib import Path
import tempfile
import time
import numpy as np

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_file
from ansys.aedt.core.generic.settings import settings
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
# The model used in this example will be downloaded from the
# [example-data](https://github.com/ansys/example-data)
# GitHub repository.

project_path = download_file(
    "eigenmode", "emi_PCB_house.aedt", temp_folder.name
)

# ### Launch Ansys Electronics Desktop (AEDT)
#
#

hfss = ansys.aedt.core.Hfss(
    project=project_path,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=False,
)
hfss.desktop_class.logger.log_on_stdout = False

# ### Eigenmode search function
#
# The function ``find_resonance()`` creates a solution setup,
# runs an analysis and returns the Q-factor and frequency values of
# ``num_modes`` resonant modes.
#
# This function will then be called inside a ``while``
# loop that filters all physical resonant modes over a wide
# bandwidth to retain only those modes having a quality factor
# greater than the user-defined ``limit``.
#
# The workflow used to retrieve solution data from
# HFSS is comprised of the following steps
# and corresponding method calls:
# | Step | Description | Method |
# |---|---|---|
# | 1. | Retrieve a list of all available<br>solution "categories".| ``hfss.post.avilable_report_quantities()`` |
# | 2. | Retrieve a ``SolutionData`` object <br> to provide an interface<br> to the solution data. | ``hfss.post.get_solution_data()`` |
# | 3. | Retrieve the data | ``get_expression_data()``|
#
# These steps mirror the reporter UI in the Electronics Desktop:
#
# <img src="_static\eigenmode\post_proc_category.png" width="800">
#
#

def find_resonance(num_modes):
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

    # Get the quantity names for the quality factor values.
    q_solution_names = hfss.post.available_report_quantities(
        quantities_category="Eigen Q"
    )

    # Get the quantity names for the frequency.
    f_solution_names = hfss.post.available_report_quantities(
        quantities_category="Eigen Modes"
    )

    # Store a list of [q_factor, frequency] pairs
    data = []

    get_solution = lambda quantity: hfss.post.get_solution_data(expressions=quantity, report_category="Eigenmode")
    get_data = lambda solution: float(solution.get_expression_data()[1][0])
   
    for q_name, f_name in zip(q_solution_names, f_solution_names):
        eigen_q_value = get_solution(q_name)
        eigen_f_value = get_solution(f_name)
        data.append([get_data(eigen_q_value), get_data(eigen_f_value)])

    return np.array(data)

# ### Automate the search for eigenmodes
# #### Specify parameters for the eigenmode search
#
#  - ``fmin``: The minimum frequency for the global search in GHz.
#  - ``fmax``: The maximum frequency for the global search (GHz). When a mode is found having
#    a frequency greater than or equal to this value, the iterations end.
#  - ``limit``: The lower bound on quality factor. Modes having a lower quality factor
#    are assumed to be non-physical and are removed from the results.

# +
fmin = 1          # Minimum frequency in search range (GHz)
fmax = 2          # Maximum frequency in search range
limit = 10        # Q-factor threshold (low Q modes will be ignored)
next_fmin = fmin  # Current lowest frequency in the iterative search
setup_nr = 1      # Current iteration in the search loop.
valid_modes = None

while next_fmin < fmax:
    modes = find_resonance(6)  # Limit the search to 6 modes per iteration.
    next_fmin = modes[-1][1] / 1E9
    setup_nr += 1
    cont_res = len(modes)
    valid_modes = [q for q in modes if q[0] > limit]

count = 1
if valid_modes:
    for mode in valid_modes:
        print(f"Mode {count}: Q= {mode[0]}, f= {mode[1]/1e9:.3f} GHz")
        count += 1
else:
    print("No valid modes found.")
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
