# # Compute receiver protection levels
#
# This example shows how to open an AEDT project with
# an EMIT design and analyze the results to determine if the received
# power at the input to each receiver exceeds the specified protection
# levels.
#
# Keywords: **EMIT**, **protection levels**.

# ## Perform imports and define constants
#

# +
import os
import sys
import tempfile
import time

import plotly.graph_objects as go
from ansys.aedt.core import Emit
# -

# from ansys.aedt.core.emit_core.emit_constants import \
#     InterfererType  # noqa: F401

# Define constants.

AEDT_VERSION = "2025.1"
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
# Launch AEDT with EMIT. The ``Desktop`` class initializes AEDT and starts it
# on the specified version and in the specified graphical mode.
#
# Check that the correct version of EMIT is installed.

if AEDT_VERSION <= "2023.1":
    print("Warning: This example requires AEDT 2023.2 or later.")
    sys.exit()

project_name = os.path.join(temp_folder.name, "emit.aedt")

emitapp = Emit(
    non_graphical=NG_MODE, new_desktop=True, project=project_name, version=AEDT_VERSION
)

# ## Specify protection levels
#
# The protection levels are specified in dBm.
# If the damage threshold is exceeded, permanent damage to the receiver front
# end may occur.
# Exceeding the overload threshold severely densensitizes the receiver.
# Exceeding the intermod threshold can drive the victim receiver into non-linear
# operation, where it operates as a mixer.
# Exceeding the desense threshold reduces the signal-to-noise ratio and can
# reduce the maximum range, maximum bandwidth, and/or the overall link quality.

# +
header_color = "grey"
damage_threshold = 30
overload_threshold = -4
intermod_threshold = -30
desense_threshold = -104

protection_levels = [
    damage_threshold,
    overload_threshold,
    intermod_threshold,
    desense_threshold,
]
# -

# ## Create and connect EMIT components
#
# Set up the scenario with radios connected to antennas.

bluetooth, blue_ant = emitapp.modeler.components.create_radio_antenna(
    "Bluetooth Low Energy (LE)", "Bluetooth"
)
gps, gps_ant = emitapp.modeler.components.create_radio_antenna("GPS Receiver", "GPS")
wifi, wifi_ant = emitapp.modeler.components.create_radio_antenna(
    "WiFi - 802.11-2012", "WiFi"
)

# ## Configure the radios
#
# Enable the HR-DSSS bands for the Wi-Fi radio and set the power level
# for all transmit bands to -20 dBm.

# +
bands = wifi.bands()
for band in bands:
    if "HR-DSSS" in band.node_name:
        if "Ch 1-13" in band.node_name:
            band.enabled = True
            band.set_band_power_level(-20)

# Reduce the bluetooth transmit power
bands = bluetooth.bands()
for band in bands:
    band.set_band_power_level(-20)


def get_radio_node(radio_name):
    """Get the radio node that matches the
    given radio name.

    Arguments:
       radio_name: String name of the radio.

    Returns: Instance of the radio.
    """
    if gps.name == radio_name:
        radio = gps
    elif bluetooth.name == radio_name:
        radio = bluetooth
    else:
        radio = wifi
    return radio


bands = gps.bands()
for band in bands:
    for child in band.children:
        if "L2 P(Y)" in band.node_name:
            band.enabled = True
        else:
            band.enabled = False
# -

# ## Load the results set
#
# Create a results revision and load it for analysis.

rev = emitapp.results.analyze()


# ## Create a legend
#
# Create a legend, defining the thresholds and colors used to display the results of
# the protection level analysis.


def create_legend_table():
    """Create a table showing the defined protection levels."""
    protectionLevels = [
        ">{} dBm".format(damage_threshold),
        ">{} dBm".format(overload_threshold),
        ">{} dBm".format(intermod_threshold),
        ">{} dBm".format(desense_threshold),
    ]
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=["<b>Interference</b>", "<b>Power Level Threshold</b>"],
                    line_color="darkslategray",
                    fill_color=header_color,
                    align=["left", "center"],
                    font=dict(color="white", size=16),
                ),
                cells=dict(
                    values=[
                        ["Damage", "Overload", "Intermodulation", "Clear"],
                        protectionLevels,
                    ],
                    line_color="darkslategray",
                    fill_color=["white", ["red", "orange", "yellow", "green"]],
                    align=["left", "center"],
                    font=dict(color=["darkslategray", "black"], size=15),
                ),
            )
        ]
    )
    fig.update_layout(
        title=dict(
            text="Protection Levels (dBm)",
            font=dict(color="darkslategray", size=20),
            x=0.5,
        ),
        width=600,
    )
    fig.show()


# ## Create a scenario matrix view
#
# Create a scenario matrix view with the transmitters defined across the top
# and receivers down the left-most column. The power at the input to each
# receiver is shown in each cell of the matrix and color-coded based on the
# protection level thresholds defined.


def create_scenario_view(emis, colors, tx_radios, rx_radios):
    """Create a scenario matrix-like table with the higher received
    power for each Tx-Rx radio combination. The colors
    used for the scenario matrix view are based on the highest
    protection level that the received power exceeds."""
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=[
                        "<b>Tx/Rx</b>",
                        "<b>{}</b>".format(tx_radios[0]),
                        "<b>{}</b>".format(tx_radios[1]),
                    ],
                    line_color="darkslategray",
                    fill_color=header_color,
                    align=["left", "center"],
                    font=dict(color="white", size=16),
                ),
                cells=dict(
                    values=[rx_radios, emis[0], emis[1]],
                    line_color="darkslategray",
                    fill_color=["white", colors[0], colors[1]],
                    align=["left", "center"],
                    font=dict(color=["darkslategray", "black"], size=15),
                ),
            )
        ]
    )
    fig.update_layout(
        title=dict(
            text="Protection Levels (dBm)",
            font=dict(color="darkslategray", size=20),
            x=0.5,
        ),
        width=600,
    )
    fig.show()


# ## Get all the radios in the project
#
# Get lists of all transmitters and receivers in the project.

# > **Note:** You can uncomment the following code.
#
# rev = emitapp.results.current_revision
# rx_radios = rev.get_receiver_names()
# tx_radios = rev.get_interferer_names(InterfererType.TRANSMITTERS)
# domain = emitapp.results.interaction_domain()

# ## Classify the results
#
# Iterate over all the transmitters and receivers and compute the power
# at the input to each receiver due to each of the transmitters. Computes
# which protection levels are exceeded by these power levels, if any.

# > **Note:** Your ability to uncomment the following code depends on whether you uncommented the earlier code.
#
# power_matrix = []
# all_colors = []

# all_colors, power_matrix = rev.protection_level_classification(
#     domain, global_levels=protection_levels
# )

# ## Create a scenario matrix-like view for the protection levels
# create_scenario_view(power_matrix, all_colors, tx_radios, rx_radios)

# ## Create a legend for the protection levels
# create_legend_table()

# ## Release AEDT
#
# Release AEDT and close the example.

emitapp.save_project()
emitapp.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``. If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
