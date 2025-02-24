# # Import Ports
# This example shows how to import ports. In this example, we are going to
#
# - Download an example board
# - Create a configuration file
#   - Add a circuit port between two nets
#   - Add a circuit port between two pins
#   - Add a circuit port between two pin groups
#   - Add a circuit port between two coordinates
#   - Add a coax port
#   - Add a port reference to the nearest pin
#   - Add distributed ports
# - Import the configuration file

# ## Import the required packages

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

# ## Load example layout

edbapp = Edb(file_edb, edbversion=AEDT_VERSION)

# ## Create an empty dictionary to host all configurations

cfg = dict()

# ## Add a circuit port between two nets

# Keywords
#
# - **name**. Name of the port.
# - **Reference_designator**. Reference designator of the component.
# - **type**. Type of the port. Supported types are 'circuit', 'coax'
# - **positive_terminal**. Positive terminal of the port. Supported types are 'net', 'pin', 'pin_group', 'coordinates'
# - **negative_terminal**. Negative terminal of the port. Supported types are 'net', 'pin', 'pin_group', 'coordinates',
# 'nearest_pin'

port_1 = {
    "name": "port_1",
    "reference_designator": "X1",
    "type": "circuit",
    "positive_terminal": {"net": "PCIe_Gen4_TX2_N"},
    "negative_terminal": {"net": "GND"},
}

# ## Add a circuit port between two pins

port_2 = {
    "name": "port_2",
    "reference_designator": "C375",
    "type": "circuit",
    "positive_terminal": {"pin": "1"},
    "negative_terminal": {"pin": "2"},
}

# ## Add a circuit port between two pin groups

pin_groups = [
    {"name": "U9_5V_1", "reference_designator": "U9", "pins": ["32", "33"]},
    {"name": "U9_GND", "reference_designator": "U9", "net": "GND"},
]

port_3 = {
    "name": "port_3",
    "type": "circuit",
    "positive_terminal": {"pin_group": "U9_5V_1"},
    "negative_terminal": {"pin_group": "U9_GND"},
}

# ## Add a circuit port between two coordinates

# Keywords
#
# - **layer**. Layer on which the terminal is placed
# - **point**. XY coordinate the terminal is placed
# - **net**. Name of the net the terminal is placed on

port_4 = {
    "name": "port_4",
    "type": "circuit",
    "positive_terminal": {"coordinates": {"layer": "1_Top", "point": ["104mm", "37mm"], "net": "AVCC_1V3"}},
    "negative_terminal": {"coordinates": {"layer": "Inner6(GND2)", "point": ["104mm", "37mm"], "net": "GND"}},
}

# ## Add a coax port

port_5 = {"name": "port_5", "reference_designator": "U1", "type": "coax", "positive_terminal": {"pin": "AM17"}}

# ## Add a port reference to the nearest pin

# Keywords
#
# - **reference_net**. Name of the reference net
# - **search_radius**. Reference pin search radius in meter

port_6 = {
    "name": "port_6",
    "reference_designator": "U15",
    "type": "circuit",
    "positive_terminal": {"pin": "D7"},
    "negative_terminal": {"nearest_pin": {"reference_net": "GND", "search_radius": 5e-3}},
}

# ## Add distributed ports

# Keywords
#
# - **distributed**. Whether to create distributed ports. When set to True, ports are created per pin

ports_distributed = {
    "name": "ports_d",
    "reference_designator": "U7",
    "type": "circuit",
    "distributed": True,
    "positive_terminal": {"net": "VDD_DDR"},
    "negative_terminal": {"net": "GND"},
}

# ## Add setups in configuration

cfg["pin_groups"] = pin_groups
cfg["ports"] = [port_1, port_2, port_3, port_4, port_5, port_6, ports_distributed]

# ## Write configuration into as json file

file_json = Path(temp_folder.name) / "edb_configuration.json"
with open(file_json, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

# ## Import configuration into example layout

edbapp.configuration.load(config_file=file_json)
edbapp.configuration.run()

# ## Review

edbapp.ports

# ## Save and close Edb
# The temporary folder will be deleted once the execution of this script is finished. Replace **edbapp.save()** with
# **edbapp.save_as("C:/example.aedb")** to keep the example project.

edbapp.save()
edbapp.close()
