# # HFSS 3D Layout: Power Integrity Analysis

# This example shows how to use the electronics database (EDB) for power integrity analysis. The 
# EDB will be loaded into HFSS 3D Layout for analysis and post-processing.
# - Set up EDB
#     - Assign S-parameter model to components
#     - Create pin groups
#     - Create ports
#     - Create SIwave SYZ anaylsis
#     - Create cutout
# - Import EDB into HFSS 3D Layout
#     - Analyze
#     - Plot $Z_{11}$

# ## Perform required imports
#
# Perform required imports.

import os
import json
import tempfile
import time
from pyaedt import Edb
from pyaedt import Hfss3dLayout
from pyaedt.downloads import download_file

# ## Define constants
#
# Define constant values used in this example 

AEDT_VERSION = "2024.1"
NG_MODE = True

# ## Create temporary directory and download files
#
# Create a temporary directory where we store downloaded data or
# dumped data.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# Download the example PCB data.

aedb = download_file(
    source="edb/ANSYS-HSD_V1.aedb", destination=temp_folder.name
)
download_file(
    source="touchstone", name="GRM32_DC0V_25degC_series.s2p", destination=temp_folder.name
)

# ## Create a configuration file to set up the layout for analysis
#
# Create an empty dictionary to host all configurations.

cfg = dict()

# > **Note:** In the following, we are going to assign S-parameter
# > models to capacitors. 

# ### Define the S-parameter files
#
# Specify the location of the S-parameter files.

cfg["general"] = {
    "s_parameter_library": os.path.join(temp_folder.name, "touchstone")
}

# ### Assign model to capactitors
#
# Assign the model "GRM32_DC0V_25degC_series.s2p" to capacitors C3 and C4, which share the same component part number.
# When "apply_to_all" is ``True``, all components having the part number "CAPC3216X180X20ML20" will be assigned the S-parameter model. 

cfg["s_parameters"] = [
    {
        "name": "GRM32_DC0V_25degC_series",
        "component_definition": "CAPC0603X33X15LL03T05",
        "file_path": "GRM32_DC0V_25degC_series.s2p",
        "apply_to_all": False,
        "components": ["C110", "C206"],
        "reference_net": "GND",
        "reference_net_per_component": {
            "C110": "GND"
        }
    }
]

# ### Define pin groups
#
# Combine the listed pins on component U1 into pin groups:
# - the first group is defined explicitly by the pins name;
# - the second group is assigned by net name using the "net" key.

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

# ### Create ports
#
# Create a circuit port between the two pin groups previously created.

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

# ### Create SIwave SYZ analysis setup
#
# Create SIwave SYZ analysis setup.
#
# > **Note:** Both SIwave and HFSS can be used to run an analysis in the
# > 3D Layout user interface.

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

# ### Cutout
#
# Define the the region of the PCB to cutout for analysis.

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

# ### Save the configuration
#
# Save the configuration file in JSON format.

pi_json = os.path.join(temp_folder.name, "pi.json")
with open(pi_json, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

# ## Load configuration into EDB
#
# Load configuration from the JSON file.

edbapp = Edb(aedb, edbversion=AEDT_VERSION)
edbapp.configuration.load(config_file=pi_json)
edbapp.configuration.run()
edbapp.save()
edbapp.close()

# The configured EDB file is saved in a temp folder.

print(temp_folder.name)

# ## Analyze in HFSS 3D Layout

# ### Load EDB into HFSS 3D Layout

h3d = Hfss3dLayout(
    aedb,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True
)

# ### Analyze

h3d.analyze()

# ### Plot impedance

solutions = h3d.post.get_solution_data(expressions='Z(port1,port1)')
solutions.plot()

# ## Save project and close AEDT
#
# Save the project, release AEDT and remove both the project and temporary directory.

# > **Note:** All project files are saved in the folder ``temp_file.dir``.
# > If you've run this example as a Jupyter notbook you  can retrieve those project files.
# > The following cell removes all temporary files, including the project folder.

# +
h3d.save_project()
h3d.release_desktop()

time.sleep(3)
temp_folder.cleanup()
