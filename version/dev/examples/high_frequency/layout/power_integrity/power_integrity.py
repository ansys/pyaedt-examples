# # Power integrity analysis
# This example shows how to use the Ansys Electronics Database (EDB) for power integrity analysis. The
# EDB is loaded into HFSS 3D Layout for analysis and postprocessing.
#
# - Set up EDB consists of these steps:
#
#     - Assign S-parameter model to components.
#     - Create pin groups.
#     - Create ports.
#     - Create SIwave SYZ analysis.
#     - Create cutout.
#
# - Import EDB into HFSS 3D Layout:
#
#     - Analyze.
#     - Plot ``$Z_{11}$``.
#
# Keywords: **HFSS 3D Layout**, **power integrity**.

# ## Perform imports and define constants
# Import the required packages

# +
import json
import os
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_file
# -

# Define constants.

AEDT_VERSION = "2025.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# Download the example PCB data.

aedb = download_file(source="edb/ANSYS-HSD_V1.aedb", local_path=temp_folder.name)
_ = download_file(
    source="touchstone",
    name="GRM32_DC0V_25degC_series.s2p",
    local_path=temp_folder.name,
)

# ## Create configuration file
# This example uses a configuration file to set up the layout for analysis.
# Initialize and create an empty dictionary to host all configurations.

cfg = dict()

# Assigns S-parameter models to capacitors.
# The first step is to use the "general" key to specify where the S-parameter files can be found.

cfg["general"] = {"s_parameter_library": os.path.join(temp_folder.name, "touchstone")}

# ## Assign model to capactitors
# The model ``GRM32_DC0V_25degC_series.s2p`` is assigned to capacitors C3 and C4, which share the same component part number.
# When "apply_to_all" is ``True``, all components having the part number "CAPC3216X180X20ML20" are assigned the S-parameter model.

cfg["s_parameters"] = [
    {
        "name": "GRM32_DC0V_25degC_series",
        "component_definition": "CAPC0603X33X15LL03T05",
        "file_path": "GRM32_DC0V_25degC_series.s2p",
        "apply_to_all": False,
        "components": ["C110", "C206"],
        "reference_net": "GND",
        "reference_net_per_component": {"C110": "GND"},
    }
]

# ## Create pin groups
# Pins can be grouped explicitly by the pin name, or pin groups can be assigned by net name using the ''net'' key.
# The following code combine the listed pins on component U2 into two pin groups using the ``net`` key.


cfg["pin_groups"] = [
    {
        "name": "PIN_GROUP_1",
        "reference_designator": "U1",
        "pins": ["AD14", "AD15", "AD16", "AD17"],
    },
    {"name": "PIN_GROUP_2", "reference_designator": "U1", "net": "GND"},
]

# ## Create ports
# Create a circuit port between the two pin groups just created.

cfg["ports"] = [
    {
        "name": "port1",
        "reference_designator": "U1",
        "type": "circuit",
        "positive_terminal": {"pin_group": "PIN_GROUP_1"},
        "negative_terminal": {"pin_group": "PIN_GROUP_2"},
    }
]

# ## Create SIwave SYZ analysis setup
# Both SIwave and HFSS can be used to run an analysis in the 3D Layout user interface.

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
                        "samples": 20,
                    }
                ],
            }
        ],
    }
]

# ## Define cutout
# Define the region of the PCB to be cut out for analysis.

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
        "keep_lines_as_path": False,
    }
}

# ## Save configuration
#
# Save the configuration file to a JSON file and apply it to layout data using the EDB.

pi_json = os.path.join(temp_folder.name, "pi.json")
with open(pi_json, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

# ## Load configuration into EDB

# Load the configuration into EDB from the JSON file.

edbapp = ansys.aedt.core.Edb(aedb, edbversion=AEDT_VERSION)
edbapp.configuration.load(config_file=pi_json)
edbapp.configuration.run()
edbapp.save()
edbapp.close()

# The configured EDB file is saved in the temporary folder.

print(temp_folder.name)

# ## Analyze in HFSS 3D Layout

# ### Load EDB into HFSS 3D Layout

h3d = ansys.aedt.core.Hfss3dLayout(
    aedb, version=AEDT_VERSION, non_graphical=NG_MODE, new_desktop=True
)

# ### Analyze

h3d.analyze(cores=NUM_CORES)

# ### Plot impedance

solutions = h3d.post.get_solution_data(expressions="Z(port1,port1)")
solutions.plot()

# ## Release AEDT

h3d.save_project()
h3d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
