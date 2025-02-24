# # Import Stackup
# This example shows how to import stackup file.

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
NG_MODE = False

# -

# Download the example PCB data.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
file_edb = download_file(source="edb/ANSYS-HSD_V1.aedb", destination=temp_folder.name)

# ## Load example layout.

edbapp = Edb(file_edb, edbversion=AEDT_VERSION)

# ## Review original stackup definition

# Get original stackup definition in a dictionary. Alternatively, stackup definition can be exported in a json file by
# edbapp.configuration.export()

data_cfg = edbapp.configuration.get_data_from_db(stackup=True)


df = pd.DataFrame(data=data_cfg["stackup"]["layers"])
display(df)

# ## Modify stackup

# Modify top layer thickness

data_cfg["stackup"]["layers"][0]["thickness"] = 0.00005

# Add a solder mask layer

data_cfg["stackup"]["layers"].insert(
    0, {"name": "soler_mask", "type": "dielectric", "material": "Megtron4", "fill_material": "", "thickness": 0.00002}
)

# Review modified stackup

df = pd.DataFrame(data=data_cfg["stackup"]["layers"])
display(df.head(3))

# Write stackup definition into a json file

file_cfg = Path(temp_folder.name) / "edb_configuration.json"
with open(file_cfg, "w") as f:
    json.dump(data_cfg, f, indent=4, ensure_ascii=False)


# ## Load stackup from json configuration file

edbapp.configuration.load(file_cfg, apply_file=True)

# Plot stackup

edbapp.stackup.plot()

# Check top layer thickness

edbapp.stackup["1_Top"].thickness

# ## Save and close Edb
# The temporary folder will be deleted once the execution of this script is finished. Replace **edbapp.save()** with
# **edbapp.save_as("C:/example.aedb")** to keep the example project.

edbapp.save()
edbapp.close()
