# # Channel Operating Margin (COM)
# This example shows how you can use pyaedt for COM analysis.

# <img src="_static\00\com_eye.png" width="500">

# ## What is COM
# - COM was developed as part of IEEE 802.3bj, 100GBASE Ethernet.
# - COM is a figure of merit for an S-parameter representing a high speed SerDes channel.
# - COM is the ratio between eye height and noise

# ```math
# COM = 20 * log10 (A_signal / A_noise)
# ```

# ## Preparation
# Import required packages

# +
import json
import os
import tempfile

from pyaedt.generic.spisim import SpiSim
from pyedb.misc.downloads import download_file

# -

# Download example files into temporary folder

# +
temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

thru = download_file(
    directory="com_analysis", filename="SerDes_Demo_02_Thru.s4p", destination=temp_folder.name
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