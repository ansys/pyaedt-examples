# # Power Integrity Analysis
# This example shows how to configure EDB for power integrity analysis, and load EDB into HFSS 3D Layout for analysis and post-processing.

# todo remove below lines after pyedb new release.
import sys
sys.path.append(r"C:\ansysdev\pycharm_projects\pyansys-edb\src")
sys.path.append(r"D:\_pycharm_project\pyaedt")

# # Preparation
# Import required packages

import os
import json
import tempfile
from pyedb import Edb
from pyaedt import Hfss3dLayout
from pyedb.misc.downloads import download_file

# Download example board.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

aedb = download_file(
    directory="edb/ANSYS-HSD_V1.aedb", destination=temp_folder.name
)

download_file(
    directory="touchstone", filename="GRM32_DC0V_25degC_series.s2p", destination=temp_folder.name
)

# # Create a configuration file
# ## Initialize a dictionary

cfg = dict()

# In this example, we are going to assign S-parameters to capacitors. Create a "general" section, and specify where the S-parameter files are located.

cfg["general"] = {
    "s_parameter_library": os.path.join(temp_folder.name, "touchstone")
}

# ## Assign S-parameter to capactitors. 
# In this example, "GRM32_DC0V_25degC_series.s2p" is assigned to C3 and C4, which share the same component part number.
# When "apply_to_all": True, all components share part number "CAPC3216X180X20ML20" will be assigned the S-parameter. In this case, "components" becomes exceptional li

cfg["s_parameters"] = [
    {
        "name": "GRM32_DC0V_25degC_series",
        "component_definition": "CAPC3216X180X20ML20",
        "file_path": "GRM32_DC0V_25degC_series.s2p",
        "apply_to_all": False,
        "components": ["C3", "C4"]
    }
]

# ## Create pin groups.
# In this example, the listed pins on component U2 are groups in two pin groups. Alternatively, use "net": "GND" to group all pins connected to net "GND".

cfg["pin_groups"] = [
    {
        "name": "PIN_GROUP_1",
        "reference_designator": "U1",
        "pins": ["AD14", "AD15", "AD16", "AD17"]
    },
    {
        "name": "PIN_GROUP_2",
        "reference_designator": "U1",
        "net": "GND"
    }
]

# ## Create ports
# Create a circuit port between the two pin groups just created.

cfg["ports"] = [
    {
        "name": "port1",
        "reference_designator": "U1",
        "type": "circuit",
        "positive_terminal": {
            "pin_group": "PIN_GROUP_1"
        },
        "negative_terminal": {
            "pin_group": "PIN_GROUP_2"
        }
    }
]

# ## Create SIwave DC analysis

cfg["setups"] = [
    {
        "name": "siwave_syz",
        "type": "siwave_syz",
        "pi_slider_position": 1,
        "freq_sweep": [
            {
                "name": "Sweep1",
                "type": "Interpolation",
                "frequencies": [
                    {
                        "distribution": "log scale",
                        "start": 1e6,
                        "stop": 1e9,
                        "samples": 20
                    }
                ]
            }
        ]
    }
]

# ## Do cutout

cfg["operations"] = {
        "cutout": {
            "signal_list": ["1V0"],
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

edbapp = Edb(aedb)
edbapp.configuration.load(config_file=pi_json)
edbapp.configuration.run()
edbapp.save()
edbapp.close()

# The configured EDB file is saved in a temp folder.

print(temp_folder.name)

# # Analyze in HFSS 3D Layout

# ## Load edb into HFSS 3D Layout.

h3d = Hfss3dLayout(
    aedb, 
    non_graphical=False,  # Set to true for non-graphical mode.
    new_desktop_session=True
)

# ## Analyze

h3d.analyze()

# ## Plot impedance

solutions = h3d.post.get_solution_data(expressions='Z(port1,port1)')

solutions.plot()
