# # Antenna
#
# This example shows how to create a project in EMIT for
# the simulation of an antenna using HFSS.
#
# <img src="_static/emit_simple_cosite.png" width="400">
#
# Keywords: **EMIT**, **Antenna**.

# ## Perform imports and define constants
#
# Perform required imports.

# +
import tempfile
import time

import ansys.aedt.core

# from ansys.aedt.core.emit_core.emit_constants import ResultType, TxRxMode
# -

# Define constants.

AEDT_VERSION = "2025.2"
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT with EMIT
#
# Launch AEDT with EMIT. The ``launch_desktop()`` method initializes AEDT
# using the specified version. The second argument can be set to ``True`` to
# run AEDT in non-graphical mode.

project_name = ansys.aedt.core.generate_unique_project_name(root_name=temp_folder.name, project_name="antenna_cosite")
d = ansys.aedt.core.launch_desktop(AEDT_VERSION, NG_MODE, new_desktop=True)
aedtapp = ansys.aedt.core.Emit(project_name, version=AEDT_VERSION)

# ## Create and connect EMIT components
#
# Create three radios and connect an antenna to each one.

rad1 = aedtapp.modeler.components.create_component("New Radio")
ant1 = aedtapp.modeler.components.create_component("Antenna")
if rad1 and ant1:
    ant1.move_and_connect_to(rad1)

# ## Place radio/antenna pair
#
# Use the ``create_radio_antenna()`` method to place the radio/antenna pair. The first
# argument is the type of radio. The second argument is the name to
# assign to the radio.

rad2, ant2 = aedtapp.modeler.components.create_radio_antenna("GPS Receiver")
rad3, ant3 = aedtapp.modeler.components.create_radio_antenna("Bluetooth Low Energy (LE)", "Bluetooth")

# ## Define the RF environment
#
# Specify the RF coupling among antennas.
# This functionality is not yet implemented in the API, but it can be entered from the UI.
#
# <img src="_static/coupling.png" width="250">


# ## Run EMIT simulation
#
# Run the EMIT simulation.
#
# This part of the example requires Ansys AEDT 2023 R2.

# > **Note:** You can uncomment the following code.
#
# if AEDT_VERSION > "2023.1":
#     rev = aedtapp.results.analyze()
#     rx_bands = rev.get_band_names(rad2.name, TxRxMode.RX)
#     tx_bands = rev.get_band_names(rad3.name, TxRxMode.TX)
#     domain = aedtapp.results.interaction_domain()
#     domain.set_receiver(rad2.name, rx_bands[0], -1)
#     domain.set_interferer(rad3.name, tx_bands[0])
#     interaction = rev.run(domain)
#     worst = interaction.get_worst_instance(ResultType.EMI)
#     if worst.has_valid_values():
#         emi = worst.get_value(ResultType.EMI)
#         print("Worst case interference is: {} dB".format(emi))

# ## Release AEDT
#
# Release AEDT and close the example.

aedtapp.save_project()
aedtapp.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``. If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
