# # Import Materials
# This example shows how to import materials.

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

# Define constants

AEDT_VERSION = "2025.1"

# ## Preparation

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
file_edb = Path(temp_folder.name) / "test.aedb"
edbapp = Edb(file_edb, edbversion=AEDT_VERSION)

# ## Create configure file

# ## Add distributed ports

# Keywords
#
# - **name**. Name of the material.
# - **permittivity**.
# - **conductivity**.
# - **dielectric_loss_tangent**.
# - **magnetic_loss_tangent**.
# - **mass_density**.
# - **permeability**.
# - **poisson_ratio**.
# - **specific_heat**.
# - **thermal_conductivity**.
# - **thermal_modifier**.
#   - **property_name**.
#   - **basic_quadratic_c1**. The C1 value in the quadratic model.
#   - **basic_quadratic_c2**. The C2 value in the quadratic model.
#   - **basic_quadratic_temperature_reference**. The TempRef value in the quadratic model.
#   - **advanced_quadratic_lower_limit**. The lower temperature limit where the quadratic model is valid.
#   - **advanced_quadratic_upper_limit**. The upper temperature limit where the quadratic model is valid.
#   - **advanced_quadratic_auto_calculate**. The flag indicating whether or not the LowerConstantThermalModifierVal and UpperConstantThermalModifierVal values should be auto calculated.
#   - **advanced_quadratic_lower_constant**. The constant thermal modifier value for temperatures lower than LowerConstantThermalModifierVal
#   - **advanced_quadratic_upper_constant**. The constant thermal modifier value for temperatures greater than UpperConstantThermalModifierVal.

materials = [
    {
        "name": "copper",
        "conductivity": 570000000,
        "thermal_modifier": [
            {
                "property_name": "conductivity",
                "basic_quadratic_c1": 0,
                "basic_quadratic_c2": 0,
                "basic_quadratic_temperature_reference": 22,
                "advanced_quadratic_lower_limit": -273.15,
                "advanced_quadratic_upper_limit": 1000,
                "advanced_quadratic_auto_calculate": True,
                "advanced_quadratic_lower_constant": 1,
                "advanced_quadratic_upper_constant": 1,
            },
        ],
    },
]
cfg = {"stackup": {"materials": materials}}
file_json = Path(temp_folder.name) / "edb_configuration.json"
with open(file_json, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

# Equivalent toml file looks like below 

toml_string = toml.dumps(cfg)
print(toml_string)

# ## Import configuration into example layout

edbapp.configuration.load(config_file=file_json)
edbapp.configuration.run()

# ## Save and close Edb
# The temporary folder will be deleted once the execution of this script is finished. Replace **edbapp.save()** with
# **edbapp.save_as("C:/example.aedb")** to keep the example project.

edbapp.save()
edbapp.close()
