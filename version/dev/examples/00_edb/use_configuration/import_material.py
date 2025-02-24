# # Import Materials
# This example shows how to import materials.

# ### Import the required packages

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

# ## Review materials from layout

# Get materials from layout in a dictionary. Materials are exported together with stadckup.

data_cfg = edbapp.configuration.get_data_from_db(stackup=True)


df = pd.DataFrame(data=data_cfg["stackup"]["materials"])
display(df)

# ## Add a new material

data_cfg["stackup"]["materials"].append(
    {"name": "soldermask", "permittivity": 3.3, "dielectric_loss_tangent": 0.02},
)

# ## Edit existing material properties

data_cfg["stackup"]["materials"][1]["name"] = "fr4_epoxy"
data_cfg["stackup"]["materials"][1]["dielectric_loss_tangent"] = 0.015

# ## Review modified materials

df = pd.DataFrame(data=data_cfg["stackup"]["materials"])
display(df)

# ## Write material definition into a json file

file_cfg = Path(temp_folder.name) / "edb_configuration.json"
with open(file_cfg, "w") as f:
    json.dump(data_cfg, f, indent=4, ensure_ascii=False)


# ## Load materials from json configuration file

edbapp.configuration.load(str(file_cfg), apply_file=True)

# ## Review materials from layout

edbapp.materials.materials

# ## Check modified material properties

edbapp.materials["fr4_epoxy"].loss_tangent

# ## Save and close Edb
# The temporary folder will be deleted once the execution of this script is finished. Replace **edbapp.save()** with
# **edbapp.save_as("C:/example.aedb")** to keep the example project.

edbapp.save()
edbapp.close()
