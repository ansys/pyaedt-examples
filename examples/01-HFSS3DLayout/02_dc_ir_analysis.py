# # HFSS 3D Layout: DC IR Analysis
# This example shows how to configure EDB for DC IR analysis, and load EDB into the 3D Layout UI for analysis and
# post-processing.
# - Set up EDB
#     - Edit via padstack
#     - Assign SPICE model to components
#     - Create pin groups
#     - Create voltage and current sources
#     - Create SIwave DC anaylsis
#     - Create cutout
# - Import EDB into HFSS 3D Layout
#     - Analyze
#     - Get DC IR analysis results


# # Preparation
# Import required packages

# +
import os
import json
import tempfile
import time
from pyedb import Edb
from pyaedt import Hfss3dLayout
from pyaedt.downloads import download_file
try:
    from ansys.pyaedt.examples.constants import AEDT_VERSION
except:
    AEDT_VERSION = "2024.1"

NG_MODE = False

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
# -

# Download example board.

aedb = download_file(
    source="edb/ANSYS-HSD_V1.aedb", destination=temp_folder.name
)
download_file(
    source="spice", name="ferrite_bead_BLM15BX750SZ1.mod", destination=temp_folder.name
)

# # Create a configuration file
# In this example, we are going to use a configure file to set up layout for analysis.
# ## Initialize a dictionary

cfg = dict()

# Define model library paths.

cfg["general"] = {
    "s_parameter_library": os.path.join(temp_folder.name, "touchstone"),
    "spice_model_library": os.path.join(temp_folder.name, "spice")
}

# ## Change via hole size and plating thickness

cfg["padstacks"] = {
    "definitions": [
        {
            "name": "v40h15-3",
            "hole_diameter": "0.2mm",
            "hole_plating_thickness": "25um"
        }
    ],
}

# ## Assign SPICE models

cfg["spice_models"] = [
    {
        "name": "ferrite_bead_BLM15BX750SZ1",  # Give a name to the SPICE Mode.
        "component_definition": "COIL-1008CS_V",  # Part name of the components
        "file_path": "ferrite_bead_BLM15BX750SZ1.mod",  # File name or full file path to the SPICE file.
        "sub_circuit_name": "BLM15BX750SZ1",
        "apply_to_all": True,  # If True, SPICE model is to be assigned to all components share the same part name.
        # If False, only assign SPICE model to components in "components".
        "components": []
    }
]

# ## Create a Voltage Source
# Create a voltage source from net.

cfg["sources"] = [
    {
        "name": "VSOURCE_5V",
        "reference_designator": "U4",
        "type": "voltage",
        "magnitude": 5,
        "positive_terminal": {
            "net": "5V"
        },
        "negative_terminal": {
            "net": "GND"
        }
    }
]

# ## Create Current Sources
# Create current sources between net and pin group.

cfg["pin_groups"] = [
    {
        "name": "J5_GND",
        "reference_designator": "J5",
        "net": "GND"
    }
]

cfg["sources"].append(
    {
        "name": "J5_VCCR",
        "reference_designator": "J5",
        "type": "current",
        "magnitude": 0.5,
        "positive_terminal": {
            "net": "SFPA_VCCR"
        },
        "negative_terminal": {
            "pin_group": "J5_GND"  # Defined in "pin_groups" section.
        }
    }
)
cfg["sources"].append(
    {
        "name": "J5_VCCT",
        "reference_designator": "J5",
        "type": "current",
        "magnitude": 0.5,
        "positive_terminal": {
            "net": "SFPA_VCCT"
        },
        "negative_terminal": {
            "pin_group": "J5_GND"  # Defined in "pin_groups" section.
        }
    }
)

# ## Create SIwave DC analysis

cfg["setups"] = [
    {
        "name": "siwave_dc",
        "type": "siwave_dc",
        "dc_slider_position": 0
    }
]

# ## Do cutout

cfg["operations"] = {
    "cutout": {
        "signal_list": ["SFPA_VCCR", "SFPA_VCCT", "5V"],
        "reference_list": ["GND"],
        "extent_type": "ConvexHull",
        "expansion_size": 0.002,
        "use_round_corner": False,
        "output_aedb_path": "",
        "open_cutout_at_end": True,
        "use_pyaedt_cutout": True,
        "number_of_threads": 4,
        "use_pyaedt_extent_computing": True,
        "extent_defeature": 0,
        "remove_single_pin_components": False,
        "custom_extent": "",
        "custom_extent_units": "mm",
        "include_partial_instances": False,
        "keep_voids": True,
        "check_terminals": False,
        "include_pingroups": False,
        "expansion_factor": 0,
        "maximum_iterations": 10,
        "preserve_components_with_model": False,
        "simple_pad_check": True,
        "keep_lines_as_path": False
    }
}

# ## Save configuration as a JSON file

pi_json = os.path.join(temp_folder.name, "pi.json")
with open(pi_json, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

# # Load configuration into EDB

# Load configuration from JSON

edbapp = Edb(aedb, edbversion=AEDT_VERSION)
edbapp.configuration.load(config_file=pi_json)
edbapp.configuration.run()
edbapp.save()
edbapp.close()

# The configured EDB file is saved in a temp folder.

print(temp_folder.name)

# # Analyze DCIR with SIwave
#
# The 3D Layout interface to SIwave is used to open the EDB and run the DCIR analysis
# using SIwave

# ## Load edb into 3D Layout.

siw = Hfss3dLayout(
    aedb,
    specified_version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop_session=True
)

# ## Analyze

siw.analyze()

# ## Get DC IR results

siw.get_dcir_element_data_current_source("siwave_dc")

# ## Shut Down Electronics Desktop

siw.release_desktop()

# ## Cleanup
#
# All project files are saved in the folder ``temp_file.dir``. If you've run this example as a Jupyter notbook you 
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

time.sleep(3)
temp_folder.cleanup()
