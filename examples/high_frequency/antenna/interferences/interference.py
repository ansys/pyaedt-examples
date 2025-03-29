# # Interference type classification
#
# This example shows how to load an existing AEDT EMIT
# design and analyze the results to classify the
# worst-case interference.
#
# Keywords: **EMIT**, **interference**.

# ## Perform imports and define constants

# +
import sys
import tempfile

import ansys.aedt.core
import plotly.graph_objects as go
from ansys.aedt.core import Emit
from ansys.aedt.core.emit_core.emit_constants import InterfererType

# -

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

# Check that EMIT 2023.2 or later is installed.

if AEDT_VERSION <= "2023.1":
    print("Warning: This example requires AEDT 2023.2 or later.")
    sys.exit()

# Download project

project_name = ansys.aedt.core.downloads.download_file(
    "emit", "interference.aedtz", destination=temp_folder.name
)

# ## Launch EMIT and open project

emitapp = Emit(
    non_graphical=NG_MODE, new_desktop=True, project=project_name, version=AEDT_VERSION
)

# ## Get lists of transmitters and receivers
#
# Get lists of all transmitters and receivers in the project.

# +
rev = emitapp.results.analyze()
tx_interferer = InterfererType().TRANSMITTERS
rx_radios = rev.get_receiver_names()
tx_radios = rev.get_interferer_names(tx_interferer)
domain = emitapp.results.interaction_domain()

if tx_radios is None or rx_radios is None:
    print("No receivers or transmitters are in the design.")
    sys.exit()
# -

# ## Classify the interference
#
# Iterate over all the transmitters and receivers and compute the power
# at the input to each receiver due to each of the transmitters. Compute
# which type of interference occurred, if any.

power_matrix = []
all_colors = []


all_colors, power_matrix = rev.interference_type_classification(
    domain, use_filter=False, filter_list=[]
)

# ## Release AEDT
#
# Release AEDT and close the example.

emitapp.release_desktop()

# ## Create a scenario matrix view
#
# Create a scenario matrix view with the transmitters defined across the top
# and receivers down the left-most column. The power at the input to each
# receiver is shown in each cell of the matrix and color-coded based on the
# interference type.
#
# Set up colors to visualize results in a table.

# +
table_colors = {
    "green": "#7d73ca",
    "yellow": "#d359a2",
    "orange": "#ff6361",
    "red": "#ffa600",
    "white": "#ffffff",
}
header_color = "grey"


def create_scenario_view(emis, colors, tx_radios, rx_radios):
    """Create a scenario matrix-like table with the higher received
    power for each Tx-Rx radio combination. The colors
    used for the scenario matrix view are based on the interference type."""

    all_colors = []
    for color in colors:
        col = []
        for cell in color:
            col.append(table_colors[cell])
        all_colors.append(col)

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
                    fill_color="grey",
                    align=["left", "center"],
                    font=dict(color="white", size=16),
                ),
                cells=dict(
                    values=[rx_radios, emis[0], emis[1]],
                    line_color="darkslategray",
                    fill_color=["white", all_colors[0], all_colors[1]],
                    align=["left", "center"],
                    height=25,
                    font=dict(color=["darkslategray", "black"], size=15),
                ),
            )
        ]
    )
    fig.update_layout(
        title=dict(
            text="Interference Type Classification",
            font=dict(color="darkslategray", size=20),
            x=0.5,
        ),
        width=600,
    )
    fig.show()


# -


# ## Create a legend
#
# Create a legend, defining the interference types and colors used to display the results of
# the analysis.


def create_legend_table():
    """Create a table showing the interference types."""
    classifications = [
        "In-band/In-band",
        "Out-of-band/In-band",
        "In-band/Out-of-band",
        "Out-of-band/Out-of-band",
    ]
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=["<b>Interference Type (Source/Victim)</b>"],
                    line_color="darkslategray",
                    fill_color=header_color,
                    align=["center"],
                    font=dict(color="white", size=16),
                ),
                cells=dict(
                    values=[classifications],
                    line_color="darkslategray",
                    fill_color=[
                        [
                            table_colors["red"],
                            table_colors["orange"],
                            table_colors["yellow"],
                            table_colors["green"],
                        ]
                    ],
                    align=["center"],
                    height=25,
                    font=dict(color=["darkslategray", "black"], size=15),
                ),
            )
        ]
    )
    fig.update_layout(
        title=dict(
            text="Interference Type Classification",
            font=dict(color="darkslategray", size=20),
            x=0.5,
        ),
        width=600,
    )
    fig.show()


# Create a scenario view for all the interference types
create_scenario_view(power_matrix, all_colors, tx_radios, rx_radios)

# Create a legend for the interference types
create_legend_table()

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
