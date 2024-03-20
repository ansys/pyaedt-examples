# # Channel Operating Margin (COM)
# This example shows how you can pyaedt for COM analysis.
# <img src="_static\com_report.png" width="500">

# # What is COM
# - COM was developed as part of IEEE 802.3bj, 100GBASE Ethernet.
# - COM is a figure of merit for an S-parameter representing a high speed SerDes channel.
# - COM is the ratio between eye height and noise

# ```math
# COM = 20 * log10 (A_signal / A_noise)
# ```

# # Preparation
# Import required packages
import tempfile
import shutil
from pathlib import Path

from pyaedt.generic.spisim import SpiSim

# Copy project files into temporary folder
temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
source_folder = Path(__file__).parent / "_static" / "00"

thru = shutil.copy2(source_folder / "SerDes_Demo_02_Thru.s4p", temp_folder.name)
fext_2_9 = shutil.copy2(source_folder / "FCI_CC_Long_Link_Pair_2_to_Pair_9_FEXT.s4p", temp_folder.name)
fext_5_9 = shutil.copy2(source_folder / "FCI_CC_Long_Link_Pair_5_to_Pair_9_FEXT.s4p", temp_folder.name)
next_11_9 = shutil.copy2(source_folder / "FCI_CC_Long_Link_Pair_11_to_Pair_9_NEXT.s4p", temp_folder.name)

# # COM analysis
# ## Run COM analysis
# PyAEDT calls SPISim for COM analysis. Please check PyAEDT documentation for supported standards.
# Set port_order="EvenOdd" when S-parameter has below port order.
# 1 - 2
# 3 - 4
# Set port_order="Incremental" when S-parameter has below port order.
# 1 - 3
# 2 - 4

spisim = SpiSim(thru)
com_results = spisim.compute_com(
    standard="50GAUI-1-C2C",
    port_order="EvenOdd",
    fext_s4p=[fext_5_9, fext_5_9],
    next_s4p=next_11_9
)

# # COM analysis results
# ## COM values
# There are two COM values reported by the definition of the standard.
# - Case 0. COM value in dB when big package is used.
# - Case 1. COM value in dB when small package is used.
print(*com_results)

# ## COM report
# A complete COM report is generate in temporary folder in html format.
print(temp_folder.name)
# <img src="_static\com_report.png" width="500">

# # Run COM analysis on custom configuration file
# ## Export template configuration file in JSON format.
custom_json = Path(temp_folder.name) / "custom.json"
spisim.export_com_configure_file(custom_json, standard="50GAUI-1-C2C")
# Modify the custom JSON file as needed.

# ## Import configuration file and run
com_results = spisim.compute_com(
    standard="custom",
    config_file=custom_json,
    port_order="EvenOdd",
    fext_s4p=[fext_5_9, fext_5_9],
    next_s4p=next_11_9
)
print(*com_results)

# # Export SPISim supported configuration file
# The exported configuration file can be used in SPISim GUI.
custom_cfg = Path(temp_folder.name) / "custom.cfg"
spisim.export_com_configure_file(custom_cfg, standard="50GAUI-1-C2C")
