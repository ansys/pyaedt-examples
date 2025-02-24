# # Import Setup AC
# This example shows how to import SIwave, HFSS setups for AC analysis. In this example, we are going to
#
# - Download an example board
# - Create a configuration file
#   - add setups
# - Import the configuration file

# ### Import the required packages

# +
import json
from pathlib import Path
import tempfile

from ansys.aedt.core.downloads import download_file

from pyedb import Edb

AEDT_VERSION = "2024.2"
NG_MODE = False

# -

# Download the example PCB data.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
file_edb = download_file(source="edb/ANSYS-HSD_V1.aedb", destination=temp_folder.name)

# ## Load example layout.

edbapp = Edb(file_edb, edbversion=AEDT_VERSION)

# ## Create an empty dictionary to host all configurations.

cfg = dict()

# ## Create an SIwave SYZ setup

# Keywords
#
# - **name**. Name of the setup.
# - **type**. Type of the analysis setup. Supported types are 'siwave_ac', 'siwave_dc', 'hfss'.
# - **pi_slider_position**. PI slider position. Supported values are from '0', '1', '2'. 0:speed, 1:balanced,
# 2:accuracy.
# - **freq_sweep**. List of frequency sweeps.
#   - **name**. Name of the sweep.
#   - **type**. Type of the sweep. Supported types are 'interpolation', 'discrete', 'broadband'.
#   - **frequencies**. Frequency distribution.
#     - **distribution**. Supported distributions are 'linear_count', 'linear_scale', 'log_scale'.
#     - **start**. Start frequency. Example, 1e6, "1MHz".
#     - **stop**. Stop frequency. Example, 1e9, "1GHz".
#     - **increment**.

siwave_setup = {
    "name": "siwave_1",
    "type": "siwave_ac",
    "pi_slider_position": 1,
    "freq_sweep": [
        {
            "name": "Sweep1",
            "type": "interpolation",
            "frequencies": [{"distribution": "log_scale", "start": 1e6, "stop": 1e9, "increment": 20}],
        }
    ],
}

# ## Create a HFSS setup

# Keywords
#
# - **name**. Name of the setup.
# - **type**. Type of the analysis setup. Supported types are 'siwave_ac', 'siwave_dc', 'hfss'.
# - **f_adapt**. Adaptive frequency.
# - **max_num_passes**. Maximum number of passes.
# - **max_mag_delta_s**. Convergence criteria delta S.
# - **mesh_operations**. Mesh operations.
#     - **name**. Name of the mesh operation.
#     - **type**. Type of the mesh operation. The supported types are 'base', 'length', 'skin_depth'.
#     - **max_length**. Maximum length of elements.
#     - **restrict_length**. Whether to restrict length of elements.
#     - **refine_inside**. Whether to turn on refine inside objects.
#     - **nets_layers_list**. {'layer_name':['net_name_1', 'net_name_2']}
# - **freq_sweep**. List of frequency sweeps.
#   - **name**. Name of the sweep.
#   - **type**. Type of the sweep. Supported types are 'interpolation', 'discrete', 'broadband'.
#   - **frequencies**. Frequency distribution.
#     - **distribution**. Supported distributions are 'linear_count', 'linear_scale', 'log_scale'.
#     - **start**. Start frequency. Example, 1e6, "1MHz".
#     - **stop**. Stop frequency. Example, 1e9, "1GHz".
#     - **increment**.

hfss_setup = {
    "name": "hfss_1",
    "type": "hfss",
    "f_adapt": "5GHz",
    "max_num_passes": 10,
    "max_mag_delta_s": 0.02,
    "mesh_operations": [
        {
            "name": "mop_1",
            "type": "length",
            "max_length": "3mm",
            "restrict_length": True,
            "refine_inside": False,
            "nets_layers_list": {"GND": ["1_Top", "16_Bottom"]},
        }
    ],
    "freq_sweep": [
        {
            "name": "Sweep1",
            "type": "interpolation",
            "frequencies": [{"distribution": "log_scale", "start": 1e6, "stop": 1e9, "increment": 20}],
        }
    ],
}

# ## Add setups in configuration

cfg["setups"] = [siwave_setup, hfss_setup]

# ## Write configuration into as json file

file_json = Path(temp_folder.name) / "edb_configuration.json"
with open(file_json, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

# ## Import configuration into example layout

edbapp.configuration.load(config_file=file_json)
edbapp.configuration.run()

# ## Review

edbapp.setups

# ## Save and close Edb
# The temporary folder will be deleted once the execution of this script is finished. Replace **edbapp.save()** with
# **edbapp.save_as("C:/example.aedb")** to keep the example project.

edbapp.save()
edbapp.close()
