# # Antenna Cosite Interference
#
# This example shows how to create a project in EMIT for
# the simulation of an antenna cosite interference scenario.
#
# <img src="_static/emit_simple_cosite.png" width="400">
#
# Keywords: **EMIT**, **Antenna**.

# ## Prerequisites
#
# ### Perform imports

# +
import os
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.emit_core.emit_constants import ResultType, TxRxMode
from ansys.aedt.core.emit_core.nodes.generated import AntennaNode, RadioNode

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
# Launch AEDT with EMIT. The ``Emit`` class initializes AEDT
# and creates an EMIT design in the project.

project_name = os.path.join(temp_folder.name, "antenna_cosite.aedt")
aedtapp = ansys.aedt.core.Emit(
    project=project_name,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Model Preparation
#
# Create radios and antennas and connect them in the EMIT schematic.
#
# ### Create and connect EMIT components
#
# Create a radio and connect an antenna to it.

rad1: RadioNode = aedtapp.schematic.create_component("New Radio")
ant1: AntennaNode = aedtapp.schematic.create_component("Antenna")
if rad1 and ant1:
    aedtapp.schematic.connect_components(rad1.name, ant1.name)

# ### Place radio/antenna pairs
#
# Use the ``create_radio_antenna()`` method to place additional radio/antenna pairs.
# The first argument is the type of radio. The second argument is the name to
# assign to the radio.

rad2, ant2 = aedtapp.schematic.create_radio_antenna("GPS Receiver")
rad3, ant3 = aedtapp.schematic.create_radio_antenna("Bluetooth Low Energy (LE)", "Bluetooth")

# ### Define the RF environment
#
# Specify the RF coupling among antennas.
# This functionality is not yet implemented in the API, but it can be entered from the UI.
#
# <img src="_static/coupling.png" width="250">

# ### Run analysis
#
# Run the EMIT simulation.

if AEDT_VERSION > "2023.1":
    rev = aedtapp.results.analyze()

# ## Postprocess
#
# Evaluate the worst-case EMI between the GPS receiver and Bluetooth radio.

if AEDT_VERSION > "2023.1":
    rx_bands = rev.get_band_names(radio_node=rad2, tx_rx_mode=TxRxMode.RX)
    tx_bands = rev.get_band_names(radio_node=rad3, tx_rx_mode=TxRxMode.TX)
    domain = aedtapp.results.interaction_domain()
    domain.set_receiver(rad2.name, rx_bands[0], -1)
    domain.set_interferer(rad3.name, tx_bands[0])
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
