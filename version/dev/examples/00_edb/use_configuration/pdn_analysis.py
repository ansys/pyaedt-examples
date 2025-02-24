# # Set up EDB for Power Distribution Network Analysis
# This example shows how to set up the electronics database (EDB) for power integrity analysis from a single
# configuration file.

# ## Import the required packages

import json

# +
import os
import tempfile

from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core.downloads import download_file

from pyedb import Edb

AEDT_VERSION = "2024.2"
NG_MODE = False

# -

# Download the example PCB data.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
download_file(source="touchstone", name="GRM32_DC0V_25degC_series.s2p", destination=temp_folder.name)
file_edb = download_file(source="edb/ANSYS-HSD_V1.aedb", destination=temp_folder.name)

# ## Load example layout

edbapp = Edb(file_edb, edbversion=AEDT_VERSION)

# ## Create an empty dictionary to host all configurations

cfg = dict()

# ## Assign S-parameter model to capactitors.

# Set S-parameter library path.

cfg["general"] = {"s_parameter_library": os.path.join(temp_folder.name, "touchstone")}

# Assign the S-parameter model.
#
# Keywords
#
# - **name**. Name of the S-parameter model in AEDT.
# - **component**_definition. Known as component part number of part name.
# - **file_path**. Touchstone file or full path to the touchstone file.
# - **apply_to_all**. When set to True, assign the S-parameter model to all components share the same
# component_definition. When set to False, Only components in "components" are assigned.
# - **components**. when apply_to_all=False, components in the list are assigned an S-parameter model.
# When apply_to_all=False, components in the list are NOT assigned.
# - **reference_net**. Reference net of the S-parameter model.

cfg["s_parameters"] = [
    {
        "name": "GRM32_DC0V_25degC_series",
        "component_definition": "CAPC0603X33X15LL03T05",
        "file_path": "GRM32_DC0V_25degC_series.s2p",
        "apply_to_all": False,
        "components": ["C110", "C206"],
        "reference_net": "GND",
    }
]

# ## Define ports
# Create a circuit port between power and ground nets.
#
# Keywords
#
# - **name**. Name of the port.
# - **reference_desinator**.
# - **type**. Type of the port. Supported types are 'ciruict', 'coax'.
# - **positive_terminal**. Positive terminal of the port. Supported types are 'net', 'pin', 'pin_group', 'coordinates'.
# - **negative_terminal**. Positive terminal of the port. Supported types are 'net', 'pin', 'pin_group', 'coordinates'.

cfg["ports"] = [
    {
        "name": "port1",
        "reference_designator": "U1",
        "type": "circuit",
        "positive_terminal": {"net": "1V0"},
        "negative_terminal": {"net": "GND"},
    }
]

# ## Define SIwave SYZ analysis setup
#
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

cfg["setups"] = [
    {
        "name": "siwave_syz",
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
]

# ## Define Cutout
#
# Keywords
#
# - **signal_list**. List of nets to be kept after cutout.
# - **reference_list**. List of nets as reference planes.
# - **extent_type**. Supported extend types are 'Conforming', 'ConvexHull', 'Bounding'.
# For optional input arguments, refer to method pyedb.Edb.cutout()

cfg["operations"] = {
    "cutout": {
        "signal_list": ["1V0"],
        "reference_list": ["GND"],
        "extent_type": "ConvexHull",
    }
}

# ## Write configuration into as json file

file_json = os.path.join(temp_folder.name, "edb_configuration.json")
with open(file_json, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

# ## Import configuration into example layout

edbapp.configuration.load(config_file=file_json)

# Apply configuration to EDB.

edbapp.configuration.run()

# Save and close EDB.

edbapp.save()
edbapp.close()

# The configured EDB file is saved in a temp folder.

print(temp_folder.name)

# ## Load edb into HFSS 3D Layout.

h3d = Hfss3dLayout(edbapp.edbpath, version=AEDT_VERSION, non_graphical=NG_MODE, new_desktop=True)

# ## Analyze

h3d.analyze()

# ## Plot impedance

solutions = h3d.post.get_solution_data(expressions="Z(port1,port1)")
solutions.plot()

# ## Shut Down Electronics Desktop

h3d.close_desktop()

# All project files are saved in the folder ``temp_file.dir``. If you've run this example as a Jupyter notebook you
# can retrieve those project files.
