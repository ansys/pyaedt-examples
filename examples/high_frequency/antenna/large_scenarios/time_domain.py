# # HFSS to SBR+ time animation
#
# This example shows how to use PyAEDT to create an SBR+ time animation
# and save it to a GIF file. This example works only on CPython.
#
# Keywords: **HFSS**, **SBR+**, **time domain**, **IFFT**.

# ## Perform imports and define constants
#
# Perform required imports.

# +
import base64
import os
import tempfile
import time

from IPython.display import HTML, display
from IPython.utils import io as ipio

from ansys.aedt.core import Hfss
from ansys.aedt.core.examples.downloads import download_sbr_time

# -

# Define constants.

AEDT_VERSION = "2026.1"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.


# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")


# ## Download project

project_file = download_sbr_time(local_path=temp_folder.name)

# ## Launch HFSS and analyze

hfss = Hfss(
    project=project_file,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

hfss.analyze(cores=NUM_CORES)

# ## Get solution data
#
# Get solution data. After the simulation is performed, you can load solutions
# in the ``solution_data`` object.

solution_data = hfss.post.get_solution_data(
    expressions=["NearEX", "NearEY", "NearEZ"],
    variations={"_u": ["All"], "_v": ["All"], "Freq": ["All"]},
    context="Near_Field",
    report_category="Near Fields",
)

# ## Compute IFFT
#
# Compute IFFT (Inverse Fast Fourier Transform).

t_matrix = solution_data.ifft("NearE", window=True)

# ## Export IFFT to CSV file
#
# Export IFFT to a CSV file.

frames_list_file = solution_data.ifft_to_file(
    coord_system_center=[-0.15, 0, 0],
    db_val=True,
    csv_path=os.path.join(hfss.working_directory, "csv"),
)

# ## Plot scene
#
# Plot the scene to create the time plot animation and save it to a GIF file.

gif_file = os.path.join(hfss.working_directory, "animation.gif")


with ipio.capture_output():
    hfss.post.plot_scene(
        frames=frames_list_file,
        gif_path=gif_file,
        norm_index=15,
        dy_rng=35,
        show=False,
        view="xy",
        zoom=1,
    )

# ## Display animation
#
# nbsphinx does not render ``image/gif`` cell outputs natively.
# The GIF is embedded as a base64 data URI inside an HTML ``<img>`` tag,
# which nbsphinx renders correctly in the static HTML documentation.

with open(gif_file, "rb") as f:
    gif_b64 = base64.b64encode(f.read()).decode()
display(HTML(f'<img src="data:image/gif;base64,{gif_b64}" width="600"/>'))

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
