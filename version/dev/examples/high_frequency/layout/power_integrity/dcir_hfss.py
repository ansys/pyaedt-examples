# # DC IR analysis
#
# This example shows how to configure EDB for DC IR analysis and load EDB into the HFSS 3D Layout UI for analysis and
# postprocessing.
#
# - Set up EDB:
#
#     - Edit via padstack.
#     - Assign SPICE model to components.
#     - Create pin groups.
#     - Create voltage and current sources.
#     - Create SIwave DC analysis.
#     - Create cutout.
#
# - Import EDB into HFSS 3D Layout:
#
#     - Analyze.
#     - Get DC IR analysis results.
#
# Keywords: **HFSS 3D Layout**, **DC IR**.

# ## Perform imports and define constants
# Perform required imports.

import json
import os
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_file
from pyedb import Edb

# Define constants.

AEDT_VERSION = "2025.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# Download example board.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
aedb = download_file(source="edb/ANSYS-HSD_V1.aedb", local_path=temp_folder.name)
_ = download_file(source="spice", name="ferrite_bead_BLM15BX750SZ1.mod", local_path=temp_folder.name)

# ## Create configuration file
# This example uses a configuration file to set up the layout for analysis.
# Initialize and create an empty dictionary to host all configurations.

cfg = dict()

# Define model library paths.

cfg["general"] = {
    "s_parameter_library": os.path.join(temp_folder.name, "touchstone"),
    "spice_model_library": os.path.join(temp_folder.name, "spice"),
}

# ### Assign SPICE models

cfg["spice_models"] = [
    {
        "name": "ferrite_bead_BLM15BX750SZ1",  # Give a name to the SPICE Mode.
        "component_definition": "COIL-1008CS_V",  # Part name of the components
        "file_path": "ferrite_bead_BLM15BX750SZ1.mod",  # File name or full file path to the SPICE file.
        "sub_circuit_name": "BLM15BX750SZ1",
        "apply_to_all": True,  # If True, SPICE model is to be assigned to all components share the same part name.
        # If False, only assign SPICE model to components in "components".
        "components": [],
    }
]

# ### Create voltage source
# Create a voltage source from a net.

cfg["sources"] = [
    {
        "name": "VSOURCE_5V",
        "reference_designator": "U4",
        "type": "voltage",
        "magnitude": 5,
        "positive_terminal": {"net": "5V"},
        "negative_terminal": {"net": "GND"},
    }
]

# ### Create current sources
# Create current sources between the net and pin group.

cfg["pin_groups"] = [{"name": "J5_GND", "reference_designator": "J5", "net": "GND"}]

cfg["sources"].append(
    {
        "name": "J5_VCCR",
        "reference_designator": "J5",
        "type": "current",
        "magnitude": 0.5,
        "positive_terminal": {"net": "SFPA_VCCR"},
        "negative_terminal": {"pin_group": "J5_GND"},  # Defined in "pin_groups" section.
    }
)
cfg["sources"].append(
    {
        "name": "J5_VCCT",
        "reference_designator": "J5",
        "type": "current",
        "magnitude": 0.5,
        "positive_terminal": {"net": "SFPA_VCCT"},
        "negative_terminal": {"pin_group": "J5_GND"},  # Defined in "pin_groups" section.
    }
)

# ### Create SIwave DC analysis

cfg["setups"] = [{"name": "siwave_dc", "type": "siwave_dc", "dc_slider_position": 0}]

# ### Define cutout

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
        "keep_lines_as_path": False,
    }
}

# ### Save configuration as a JSON file

pi_json = os.path.join(temp_folder.name, "pi.json")
with open(pi_json, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

# ## Load configuration into EDB

# Load the configuration from the JSON file into EDB.

edbapp = Edb(aedb, version=AEDT_VERSION)
edbapp.configuration.load(config_file=pi_json)
edbapp.configuration.run()

# # Load configuration into EDB
edbapp.nets.plot(None, None, color_by_net=True)

# ## Save and close EDB

edbapp.save()
edbapp.close()

# The configured EDB file is saved in the temporary folder.

print(temp_folder.name)

# ## Analyze DCIR with SIwave
#
# The HFSS 3D Layout interface to SIwave is used to open the EDB and run the DCIR analysis
# using SIwave

# ### Load EDB into HFSS 3D Layout.

siw = ansys.aedt.core.Hfss3dLayout(aedb, version=AEDT_VERSION, non_graphical=NG_MODE, new_desktop=True)

# ### Analyze

siw.analyze(cores=NUM_CORES)

# ### Get DC IR results

siw.get_dcir_element_data_current_source("siwave_dc")

# ## Release AEDT

siw.save_project()
siw.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
