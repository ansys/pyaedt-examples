# Todo

# # HFSS 3D Layout: Electrothermal Analysis
# This example shows how to configure EDB for DC IR analysis.
# - Set up EDB
# Todo
# - Import EDB into HFSS 3D Layout
# Todo


# # Preparation
# Import required packages

# +
import os
import json
import tempfile
# from pyaedt import Edb
# from pyaedt import Hfss3dLayout
from pyedb import Edb
from pyedb import Siwave
from pyedb.misc.downloads import download_file

NG_MODE = False
VERSION = "2024.1"
temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
# -

# Download example board.

aedb = download_file(
    directory="edb/ANSYS-HSD_V1.aedb", destination=temp_folder.name
)
download_file(
    directory="spice", filename="ferrite_bead_BLM15BX750SZ1.mod", destination=temp_folder.name
)

# # Create a configuration file
# In this example, we are going to use a configure file to set up layout for analysis.
# ## Initialize a dictionary

cfg = dict()

# ## Add component thermal information and heatsink definition

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
            "fin_thickness": "1mm"
        },
        "apply_to_all": False,
        "components": ["J5"]
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

i_src =     {
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
v_src =     {
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
cfg["sources"] = [i_src, v_src]

# ## Do cutout

cfg["operations"] = {
    "cutout": {
        "signal_list": ["SFPA_VCCR", "SFPA_VCCT", "5V"],
        "reference_list": ["GND"],
        "extent_type": "Bounding",
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

# ## Create SIwave DC analysis

cfg["setups"] = [
    {
        "name": "siwave_dc",
        "type": "siwave_dc",
        "dc_slider_position": 0,
        "dc_ir_settings": {
            "export_dc_thermal_data": True
        }
    }
]

# ## Save configuration as a JSON file

pi_json = os.path.join(temp_folder.name, "pi.json")
with open(pi_json, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

# # Load configuration into EDB

# Load configuration from JSON

edbapp = Edb(aedb, edbversion=VERSION)
edbapp.configuration.load(config_file=pi_json)
edbapp.configuration.run()
edbapp.save()
edbapp.close()

# The configured EDB file is saved in a temp folder.

print(temp_folder.name)

# # Analyze in SIwave

siwave = Siwave(specified_version=VERSION)

siwave.open_project(proj_path=aedb)
siwave.save_project(projectpath=temp_folder.name, projectName="ansys")
siwave.run_dc_simulation()
siwave.export_icepak_project(os.path.join(temp_folder.name, "from_siwave.aedt"), "siwave_dc")

siwave.close_project()

siwave.quit_application()
