# # Import Component Definitions
# This example shows how to import component definitions. It includes
#
# - Download an example board
# - Create a config file with component RLC and solder ball information
# - Apply the config file to the example board

# ## Perform imports and define constants
#
# Perform required imports.

# +
import json
import toml
from pathlib import Path
import tempfile

from IPython.display import display
from ansys.aedt.core.examples.downloads import download_file
import pandas as pd
from pyedb import Edb
# -

# Define constants.

AEDT_VERSION = "2025.2"

# Download the example PCB data.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys").name
file_edb = download_file(source="edb/ANSYS-HSD_V1.aedb", local_path=temp_folder)

# ## Load example layout.

edbapp = Edb(file_edb, edbversion=AEDT_VERSION)

# ## Create a config file with component information

# Keywords
#
# - **reference_designator**. Reference designator of the component.
# - **part_type**. Part type of the component. Supported types are 'resistor', 'inductor', 'capacitor', 'ic', 'io',
# 'other'.
# - **enabled**. Only available for RLC components.
# - **solder_ball_properties**.
#   - **shape**. Supported types are 'cylinder', 'spheroid', 'none'.
#   - **diameter**.
#   - **mid_diameter**.
#   - **height**.
#   - **material**.
# - **port_properties**.
#   - **reference_offset**.
#   - **reference_size_auto**.
#   - **reference_size_x**.
#   - **reference_size_y**.
# - **pin_pair_model**. RLC network. Multiple pin pairs are supported.
#   - **first_pin**. First pin of the pin pair.
#   - **second_pin**. Second pin of the pin pair.
#   - **is_parallel**.
#   - **resistance**.
#   - **resistance_enabled**.
#   - **inductance**.
#   - **inductance_enabled**.
#   - **capacitance**.
#   - **capacitance_enabled**.

cfg = dict()
cfg["components"] = [
    {
        "reference_designator": "U1",
        "part_type": "io",
        "solder_ball_properties": {
            "shape": "spheroid",
            "diameter": "244um",
            "mid_diameter": "400um",
            "height": "300um",
            "material": "air",
        },
        "port_properties": {
            "reference_offset": "0.1mm",
            "reference_size_auto": True,
            "reference_size_x": 0,
            "reference_size_y": 0,
        },
    },
    {
        "reference_designator": "C375",
        "enabled": False,
        "pin_pair_model": [
            {
                "first_pin": "1",
                "second_pin": "2",
                "is_parallel": False,
                "resistance": "10ohm",
                "resistance_enabled": True,
                "inductance": "1nH",
                "inductance_enabled": False,
                "capacitance": "10nF",
                "capacitance_enabled": True,
            }
        ],
    },
]

cfg_file_path = Path(temp_folder) / "cfg.json"
with open(cfg_file_path, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

# Equivalent toml file looks like below 

toml_string = toml.dumps(cfg)
print(toml_string)

# ## Apply config file

edbapp.configuration.load(cfg_file_path, apply_file=True)

# Save and close Edb
#
# The temporary folder will be deleted once the execution of this script is finished. Replace **edbapp.save()** with
# **edbapp.save_as("C:/example.aedb")** to keep the example project.

edbapp.save()
edbapp.close()
