# # Channel Operating Margin (COM)
# This example shows how to use PyAEDT for COM analysis.
# These standards are supported:
#
# - 50GAUI_1_C2C
# - 100GAUI_2_C2C
# - 200GAUI_4
# - 400GAUI_8
# - 100GBASE_KR4
# - 100GBASE_KP4

# <img src="_static\com_eye.png" width="500">

# ## What is COM?
#
# - COM was developed as part of IEEE 802.3bj, 100GBASE Ethernet.
# - COM is a figure of merit for an S-parameter representing a high-speed SerDes channel.
# - COM is the ratio between eye height and noise.
#
# Keywords: **COM**, **signal integrity**, **virtual compliance**.

# ## Perform imports
# Perform required imports.

import os
import tempfile

from ansys.aedt.core.visualization.post.spisim import SpiSim
from ansys.aedt.core.visualization.post.spisim_com_configuration_files import \
    com_parameters
from pyedb.misc.downloads import download_file

# ## Create temporary directory and download example files
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

# +
temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

thru = download_file(
    directory="com_analysis",
    filename="SerDes_Demo_02_Thru.s4p",
    destination=temp_folder.name,
)
fext_2_9 = download_file(
    directory="com_analysis",
    filename="FCI_CC_Long_Link_Pair_2_to_Pair_9_FEXT.s4p",
    destination=temp_folder.name,
)
fext_5_9 = download_file(
    directory="com_analysis",
    filename="FCI_CC_Long_Link_Pair_5_to_Pair_9_FEXT.s4p",
    destination=temp_folder.name,
)
next_11_9 = download_file(
    directory="com_analysis",
    filename="FCI_CC_Long_Link_Pair_11_to_Pair_9_NEXT.s4p",
    destination=temp_folder.name,
)
# -

# ## Run COM analysis
# PyAEDT calls SPISim for COM analysis. For supported standardes, see the PyAEDT documentation.

# Set ``port_order="EvenOdd"`` when the S-parameter has this port order:
#
# 1 - 2
#
# 3 - 4
#
# Set ``port_order="Incremental"`` when the S-parameter has this port order:
#
# 1 - 3
#
# 2 - 4

spi_sim = SpiSim(thru)
com_results = spi_sim.compute_com(
    standard=1,  # 50GAUI-1-C2C
    port_order="EvenOdd",
    fext_s4p=[fext_5_9, fext_5_9],
    next_s4p=next_11_9,
)

# ## Print COM values
# There are two COM values reported by the definition of the standard:
#
# - Case 0: COM value in dB when big package is used.
# - Case 1: COM value in dB when small package is used.

print(*com_results)

# ## View COM report
# A complete COM report is generated in the temporary folder in HTML format.

print(temp_folder.name)

# <img src="_static\com_report.png" width="800">

# ## Run COM analysis on custom configuration file

# ### Export template configuration file in JSON format

custom_json = os.path.join(temp_folder.name, "custom.json")
spi_sim.export_com_configure_file(custom_json, standard=1)

# Modify the custom JSON file as needed.

# ### Import configuration file and run

com_results = spi_sim.compute_com(
    standard=0,  # Custom
    config_file=custom_json,
    port_order="EvenOdd",
    fext_s4p=[fext_5_9, fext_5_9],
    next_s4p=next_11_9,
)
print(*com_results)

# ## Export SPISim supported configuration file
# You can use the exported configuration file in the SPISim GUI.

# +

com_param = com_parameters.COMParametersVer3p4()
com_param.load(custom_json)
custom_cfg = os.path.join(temp_folder.name, "custom.cfg")
com_param.export_spisim_cfg(custom_cfg)
# -

# PyAEDT also supports the SPISim configuration file.

com_results = spi_sim.compute_com(
    standard=0, config_file=custom_cfg, port_order="EvenOdd"
)  # Custom
print(*com_results)
