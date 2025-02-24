# # Import Sources
# This example shows how to import voltage and current sources. In this example, we are going to
#
# - Download an example board
# - Create a configuration file
#   - Add a voltage source between two nets
#   - Add a current source between two pins
#   - Add a current source between two pin groups
#   - Add a current source between two coordinates
#   - Add a current source to the nearest pin
#   - Add distributed sources
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

# ## Add a voltage source between two nets

# Keywords
#
# - **name**. Name of the voltage source.
# - **Reference_designator**. Reference designator of the component.
# - **type**. Type of the source. Supported types are 'voltage', 'current'
# - **positive_terminal**. Supported types are 'net', 'pin', 'pin_group', 'coordinates'
#   - **contact_radius**. Optional. Set circular equipotential region.
#   - **inline**. Optional. When True, contact points are place in a row.
#   - **num_of_contact**. Optional. Number of contact points. Default is 1. Applicable only when inline is True.
# - **negative_terminal**. Supported types are 'net', 'pin', 'pin_group', 'coordinates'
# - **equipotential**. Set equipotential region on pins when True.

voltage_source = {
    "name": "V_SOURCE_5V",
    "reference_designator": "U4",
    "type": "voltage",
    "magnitude": 1,
    "positive_terminal": {"net": "5V", "contact_radius": "1mm"},
    "negative_terminal": {"net": "GND", "contact_radius": "1mm"},
    "equipotential": True,
}

# ## Add a current source between two pins

current_source_1 = {
    "name": "I_CURRENT_1A",
    "reference_designator": "J5",
    "type": "current",
    "magnitude": 10,
    "positive_terminal": {"pin": "15"},
    "negative_terminal": {"pin": "14"},
}

# ## Add a current source between two pin groups

pin_groups = [
    {"name": "IC2_5V", "reference_designator": "IC2", "pins": ["8"]},
    {"name": "IC2_GND", "reference_designator": "IC2", "net": "GND"},
]

current_source_2 = {
    "name": "CURRENT_SOURCE_2",
    "type": "current",
    "positive_terminal": {"pin_group": "IC2_5V"},
    "negative_terminal": {"pin_group": "IC2_GND"},
}

# ## Add a current source between two coordinates

# Keywords
#
# - **layer**. Layer on which the terminal is placed
# - **point**. XY coordinate the terminal is placed
# - **net**. Name of the net the terminal is placed on

current_source_3 = {
    "name": "CURRENT_SOURCE_3",
    "type": "current",
    "equipotential": True,
    "positive_terminal": {"coordinates": {"layer": "1_Top", "point": ["116mm", "41mm"], "net": "5V"}},
    "negative_terminal": {"coordinates": {"layer": "Inner1(GND1)", "point": ["116mm", "41mm"], "net": "GND"}},
}

# ## Add a current source reference to the nearest pin

# Keywords
#
# - **reference_net**. Name of the reference net
# - **search_radius**. Reference pin search radius in meter

current_source_4 = {
    "name": "CURRENT_SOURCE_4",
    "reference_designator": "J5",
    "type": "current",
    "positive_terminal": {"pin": "16"},
    "negative_terminal": {"nearest_pin": {"reference_net": "GND", "search_radius": 5e-3}},
}

# ## Add distributed current sources

# Keywords
#
# - **distributed**. Whether to create distributed sources. When set to True, ports are created per pin

sources_distributed = {
    "name": "DISTRIBUTED",
    "reference_designator": "U2",
    "type": "current",
    "distributed": True,
    "positive_terminal": {"net": "5V"},
    "negative_terminal": {"net": "GND"},
}

# ## Add setups in configuration

cfg["pin_groups"] = pin_groups
cfg["sources"] = [
    voltage_source,
    current_source_1,
    current_source_2,
    current_source_3,
    current_source_4,
    sources_distributed,
]

# ## Write configuration into as json file

file_json = Path(temp_folder.name) / "edb_configuration.json"
with open(file_json, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

# ## Import configuration into example layout

edbapp.configuration.load(config_file=file_json)
edbapp.configuration.run()

# ## Review

edbapp.siwave.sources

# ## Save and close Edb
# The temporary folder will be deleted once the execution of this script is finished. Replace **edbapp.save()** with
# **edbapp.save_as("C:/example.aedb")** to keep the example project.

edbapp.save()
edbapp.close()
