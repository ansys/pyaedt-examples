# # HFSS to EMIT Coupling
#
# This example shows how to link an HFSS design
# to EMIT and model RF interference among various components.
#
# <img src="_static/emit_hfss.png" width="400">
#
# > **Note:** This example uses the ``Cell Phone RFI Desense``
# > project that is available with the AEDT installation in the
# > ``\Examples\EMIT\`` directory.
#
# Keywords: **EMIT**, **Coupling**.

# ## Prerequisites
#
# ### Perform imports

# +
import os
import shutil
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.emit_core.emit_constants import ResultType, TxRxMode

# -

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2026.1"
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ### Launch application
#
# Launch AEDT with EMIT. The ``Desktop`` class initializes AEDT and starts it
# on the specified version and in the specified graphical mode.

d = ansys.aedt.core.launch_desktop(version=AEDT_VERSION, non_graphical=NG_MODE, new_desktop=True)

# ## Model Preparation
#
# ### Copy example files
#
# Copy the ``Cell Phone RFI Desense`` example data from the
# installed ``Examples`` directory to the temporary working
# directory.
#
# > **Note:** The HFSS design from the installed example
# > used to model the RF environment
# > has been pre-solved. Hence, the results folder is copied and
# > the RF interference between transceivers is calculated in EMIT using
# > results from the linked HFSS design.

file_name = lambda s: s + ".aedt"
results_name = lambda s: s + ".aedtresults"
pdf_name = lambda s: s + " Example.pdf"

example = "Cell Phone RFI Desense"
example_dir = os.path.join(d.install_path, "Examples\\EMIT")
example_project = os.path.join(example_dir, file_name(example))
example_results_folder = os.path.join(example_dir, results_name(example))
example_pdf = os.path.join(example_dir, pdf_name(example))

project_name = shutil.copyfile(example_project, os.path.join(temp_folder.name, file_name(example)))
results_folder = shutil.copytree(example_results_folder, os.path.join(temp_folder.name, results_name(example)))
project_pdf = shutil.copyfile(example_pdf, os.path.join(temp_folder.name, pdf_name(example)))

# Open the project in the working directory.

aedtapp = ansys.aedt.core.Emit(project_name, version=AEDT_VERSION)

# ### Create and connect EMIT components
#
# Create two radios with antennas connected to each one.

rad1, ant1 = aedtapp.schematic.create_radio_antenna("Bluetooth Low Energy (LE)")
rad2, ant2 = aedtapp.schematic.create_radio_antenna("Bluetooth Low Energy (LE)")

# ### Define coupling among RF systems
#
# Link and update coupling among the RF systems.

for link in aedtapp.couplings.linkable_design_names:
    aedtapp.couplings.add_link(link)
    print('linked "' + link + '".')

for link in aedtapp.couplings.coupling_names:
    aedtapp.couplings.update_link(link)
    print('linked "' + link + '".')

# ### Run analysis
#
# Run the EMIT simulation to calculate RF interference.

if AEDT_VERSION > "2023.1":
    rev = aedtapp.results.analyze()

# ## Postprocess
#
# Evaluate the worst-case EMI between the two Bluetooth radios.

if AEDT_VERSION > "2023.1":
    rx_bands = rev.get_band_names(radio_node=rad1, tx_rx_mode=TxRxMode.RX)
    tx_bands = rev.get_band_names(radio_node=rad2, tx_rx_mode=TxRxMode.TX)
    domain = aedtapp.results.interaction_domain()
    domain.set_receiver(rad1.name, rx_bands[0], -1)
    domain.set_interferer(rad2.name, tx_bands[0])
    interaction = rev.run(domain)
    worst = interaction.get_worst_instance(ResultType.EMI)
    if worst.has_valid_values():
        emi = worst.get_value(ResultType.EMI)
        print("Worst case interference is: {} dB".format(emi))

# ## Finish
#
# ### Save the project

aedtapp.save_project()
aedtapp.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
