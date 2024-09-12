# # Electrothermal Analysis
#
# This example shows how to use the electronics database (EDB) for DC IR analysis and
# electrothermal analysis. The EDB will be loaded into SIwave for analysis and post-processing.
# In the end, an Icepak project is exported from SIwave.
# - Set up EDB
#   - Assign package and heatsink model to components
#   - Create voltage and current sources
#   - Create SIwave DC analysis
#   - Define cutout
# - Import EDB into SIwave
#   - Analyze DC IR
#   - Export Icepak project


# ## Perform required imports
#
# Perform required imports.

import json
import os
import sys
import tempfile
import time

from ansys.aedt.core.downloads import download_file
from pyedb import Edb, Siwave

# ## Define constants

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = True  # Open AEDT UI when it is launched.

# Check if AEDT is launched in graphical mode.

if not NG_MODE:
    print("Warning: this example requires graphical mode enabled.")
    sys.exit()

# ## Create temporary directory
#
# Create a temporary directory where we store downloaded data or
# dumped data.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# Download the example PCB data.

aedb = download_file(source="edb/ANSYS-HSD_V1.aedb", destination=temp_folder.name)

# ## Create a configuration file
#
# In this example, we are going to use a configuration file to set up layout for analysis.
# Create an empty dictionary to host all configurations.

cfg = dict()

# ## Add component thermal information and heats-ink definition

cfg["package_definitions"] = [
    {
        "name": "package_1",
        "component_definition": "SMTC-MECT-110-01-M-D-RA1_V",
        "maximum_power": 1,
        "therm_cond": 1,
        "theta_jb": 1,
        "theta_jc": 1,
        "height": "2mm",
        "heatsink": {
            "fin_base_height": "2mm",
            "fin_height": "4mm",
            "fin_orientation": "x_oriented",
            "fin_spacing": "1mm",
            "fin_thickness": "1mm",
        },
        "apply_to_all": False,
        "components": ["J5"],
    }
]

# ## Create pin groups.
#
# In this example, all pins on net "GND" on component J5 are grouped into one group.
# Pin groups can be assigned by net name using the "net" key as shown here:

cfg["pin_groups"] = [{"name": "J5_GND", "reference_designator": "J5", "net": "GND"}]

# ## Create Current Sources
#
# In this example, two current sources are created on component J5.
# A current source is placed between positive and negative terminals.
# When keyword "net" is used, all pins on the specified net are grouped into a
# new pin group which is assigned as the positive terminal.
# Negative terminal can be assigned by pin group name by using the keyword "pin_group".
# The two current sources share the same pin group "J5_GND" as the negative terminal.

i_src_1 = {
    "name": "J5_VCCR",
    "reference_designator": "J5",
    "type": "current",
    "magnitude": 0.5,
    "positive_terminal": {"net": "SFPA_VCCR"},
    "negative_terminal": {"pin_group": "J5_GND"},  # Defined in "pin_groups" section.
}
i_src_2 = {
    "name": "J5_VCCT",
    "reference_designator": "J5",
    "type": "current",
    "magnitude": 0.5,
    "positive_terminal": {"net": "SFPA_VCCT"},
    "negative_terminal": {"pin_group": "J5_GND"},  # Defined in "pin_groups" section.
}

# ## Create a Voltage Source
#
# Create a voltage source on component U4 between two nets using keyword "net".

# +
v_src = {
    "name": "VSOURCE_5V",
    "reference_designator": "U4",
    "type": "voltage",
    "magnitude": 5,
    "positive_terminal": {"net": "5V"},
    "negative_terminal": {"net": "GND"},
}

cfg["sources"] = [v_src, i_src_1, i_src_2]
# -

# ## Cutout
#
# The following assignments will define the region of the PCB to be cut out for analysis.

cfg["operations"] = {
    "cutout": {
        "signal_list": ["SFPA_VCCR", "SFPA_VCCT", "5V"],
        "reference_list": ["GND"],
        "extent_type": "Bounding",
    }
}

# ## Create SIwave DC analysis

cfg["setups"] = [
    {
        "name": "siwave_dc",
        "type": "siwave_dc",
        "dc_slider_position": 0,
        "dc_ir_settings": {"export_dc_thermal_data": True},
    }
]

# ## Save configuration as a JSON file
#
# The configuration file can be saved in JSON format and applied to layout data using the EDB.

# +
pi_json = os.path.join(temp_folder.name, "pi.json")

with open(pi_json, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)
# -

# ## Load configuration into EDB
#
# Load configuration from JSON

edbapp = Edb(aedb, edbversion=AEDT_VERSION)
edbapp.configuration.load(config_file=pi_json)
edbapp.configuration.run()
edbapp.save()
edbapp.close()
time.sleep(3)

# The configured EDB file is saved in a temp folder.

print(temp_folder.name)

# ## Analyze in SIwave
#
# Load edb into SIwave.

siwave = Siwave(specified_version=AEDT_VERSION)
time.sleep(10)
siwave.open_project(proj_path=aedb)
siwave.save_project(projectpath=temp_folder.name, projectName="ansys")

# ## Analyze

siwave.run_dc_simulation()

# ## Export Icepak project

siwave.export_icepak_project(
    os.path.join(temp_folder.name, "from_siwave.aedt"), "siwave_dc"
)

# ## Close SIWave project

siwave.close_project()

# ## Shut Down SIwave

siwave.quit_application()

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.dir``. If you've run this example as a Jupyter notbook you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

time.sleep(3)
temp_folder.cleanup()
