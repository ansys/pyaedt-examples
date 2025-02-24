# # Import Padstack Definitions
# This example shows how to import padstack definitions. This includes
#
# - Download an example board
# - Create a config file with hole information
# - Create a config file with pad and anti-pad information

# ## Import the required packages

# +
import json
from pathlib import Path
import tempfile

from IPython.display import display
from ansys.aedt.core.downloads import download_file
import pandas as pd

from pyedb import Edb

AEDT_VERSION = "2024.2"

# -

# Download the example PCB data.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys").name
file_edb = download_file(source="edb/ANSYS-HSD_V1.aedb", destination=temp_folder)

# ## Load example layout.

edbapp = Edb(file_edb, edbversion=AEDT_VERSION)

# ## Create a config file with hole information

# Keywords
#
# - **name**. Name of the padstack definition.
# - **hole_plating_thickness**. Hole plating thickness.
# - **hole_range**. Supported types are 'through', 'begin_on_upper_pad', 'end_on_lower_pad', 'upper_pad_to_lower_pad'.
# - **hole_parameters**.
#   - **shape**. Supported types are 'circle', 'square', 'rectangle'.
#   - Other parameters are shape dependent.
#     - When shape is 'circle', supported parameter si 'diameter'.
#     - When shape is 'square', supported parameter is 'size'.
#     - When shape is 'rectangle', supported parameters are 'x_size', 'y_size'.

cfg = dict()
cfg["padstacks"] = {}
cfg["padstacks"]["definitions"] = [
    {
        "name": "v35h15",
        "hole_plating_thickness": "25um",
        "material": "copper",
        "hole_range": "through",
        "hole_parameters": {
            "shape": "circle",
            "diameter": "0.15mm",
        },
    }
]

df = pd.DataFrame(data=cfg["padstacks"]["definitions"])
display(df)

cfg_file_path = Path(temp_folder) / "cfg.json"
with open(cfg_file_path, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

# Load config file

edbapp.configuration.load(cfg_file_path, apply_file=True)

# ## Create a config file with pad information

# Keywords
#
# - **name**. Name of the padstack definition.
# - **pad_parameters**.
#   - **regular_pad**. List of pad definition per layer.
#     - **layer_name**. Name of the layer.
#     - **shape**. Supported types are 'circle', 'square', 'rectangle', 'oval', 'bullet'.
#     - Other parameters are shape dependent.
#       - When shape is 'circle', supported parameter si 'diameter'.
#       - When shape is 'square', supported parameter is 'size'.
#       - When shape is 'rectangle', supported parameters are 'x_size', 'y_size'.
#       - When shape is 'oval', supported parameters are 'x_size', 'y_size', 'corner_radius'.
#       - When shape is 'bullet', supported parameters are 'x_size', 'y_size', 'corner_radius'.

cfg = dict()
cfg["padstacks"] = {}
cfg["padstacks"]["definitions"] = [
    {
        "name": "v35h15",
        "pad_parameters": {
            "regular_pad": [
                {
                    "layer_name": "1_Top",
                    "shape": "circle",
                    "offset_x": "0.1mm",
                    "offset_y": "0.1mm",
                    "rotation": "0",
                    "diameter": "0.5mm",
                },
                {
                    "layer_name": "Inner1(GND1)",
                    "shape": "square",
                    "offset_x": "0.1mm",
                    "offset_y": "0.1mm",
                    "rotation": "45deg",
                    "size": "0.5mm",
                },
            ],
            "anti_pad": [{"layer_name": "1_Top", "shape": "circle", "diameter": "1mm"}],
        },
    }
]

df = pd.DataFrame(data=cfg["padstacks"]["definitions"][0]["pad_parameters"]["regular_pad"])
display(df)

df = pd.DataFrame(data=cfg["padstacks"]["definitions"][0]["pad_parameters"]["anti_pad"])
display(df)

cfg_file_path = Path(temp_folder) / "cfg.json"
with open(cfg_file_path, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

# Load config file

edbapp.configuration.load(cfg_file_path, apply_file=True)

# ## Save and close Edb
# The temporary folder will be deleted once the execution of this script is finished. Replace edbapp.save() with
# edbapp.save_as("C:/example.aedb") to keep the example project.

edbapp.save()
edbapp.close()
