# # Create a simple transmission line

# ## Import the required packages

# +
import json
import os
import tempfile

from ansys.aedt.core import Hfss3dLayout

from pyedb import Edb

# -

# +
AEDT_VERSION = "2024.2"
NG_MODE = False
temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
# -

# ## Create an empty design

edb_path = os.path.join(temp_folder.name, "simple_transmission_line.aedb")
edbapp = Edb(edb_path, edbversion=AEDT_VERSION)

# Create a default 2-layer stackup
edbapp.stackup.create_symmetric_stackup(layer_count=2, soldermask=False)

# ## Create config file

# +
cfg = {"stackup": {}, "modeler": {}, "variables": {}}

cfg["variables"] = [{"name": "trace_width", "value": "0.2mm"}]

cfg["stackup"]["materials"] = [
    {"name": "copper", "permittivity": 1, "conductivity": 58000000.0},
    {"name": "fr4", "permittivity": 3.77, "dielectric_loss_tangent": 0.005},
    {"name": "solder_resist", "permittivity": 3.0, "dielectric_loss_tangent": 0.035},
]

cfg["stackup"]["layers"] = [
    {"name": "TOP", "type": "signal", "material": "copper", "fill_material": "solder_resist", "thickness": "0.035mm"},
    {"name": "DE", "type": "dielectric", "material": "fr4", "fill_material": "", "thickness": "0.5mm"},
    {
        "name": "BOTTOM",
        "type": "signal",
        "material": "copper",
        "fill_material": "solder_resist",
        "thickness": "0.035mm",
    },
]

cfg["modeler"]["traces"] = [
    {
        "name": "trace_1",
        "layer": "TOP",
        "width": "trace_width",
        "path": [[0, 0], [0, "3mm"]],
        "net_name": "SIG",
        "start_cap_style": "flat",
        "end_cap_style": "flat",
    },
    {
        "name": "trace_1_void",
        "layer": "TOP",
        "width": "trace_width+0.3mm",
        "path": [[0, 0], [0, "3mm"]],
        "net_name": "GND",
    },
]
cfg["modeler"]["planes"] = [
    {
        "type": "rectangle",
        "name": "GND_TOP",
        "layer": "TOP",
        "net_name": "GND",
        "lower_left_point": ["-2mm", 0],
        "upper_right_point": ["2mm", "3mm"],
        "voids": ["trace_1_void"],
    },
    {
        "type": "rectangle",
        "name": "GND_BOTTOM",
        "layer": "BOTTOM",
        "net_name": "GND",
        "lower_left_point": ["-2mm", 0],
        "upper_right_point": ["2mm", "3mm"],
    },
]

cfg["modeler"]["padstack_definitions"] = [
    {
        "name": "via",
        "hole_plating_thickness": "0.025mm",
        "material": "copper",
        "pad_parameters": {
            "regular_pad": [
                {
                    "layer_name": "TOP",
                    "shape": "circle",
                    "diameter": "0.5mm",
                },
                {
                    "layer_name": "BOTTOM",
                    "shape": "circle",
                    "diameter": "0.5mm",
                },
            ],
        },
        "hole_range": "through",
        "hole_parameters": {
            "shape": "circle",
            "diameter": "0.25mm",
        },
    }
]

cfg["modeler"]["padstack_instances"] = [
    {
        "name": "gvia_l_1",
        "definition": "via",
        "layer_range": ["TOP", "BOTTOM"],
        "position": ["-1mm", "0.5mm"],
        "net_name": "GND",
    },
    {
        "name": "gvia_l_2",
        "definition": "via",
        "layer_range": ["TOP", "BOTTOM"],
        "position": ["-1mm", "1.5mm"],
        "net_name": "GND",
    },
    {
        "name": "gvia_l_3",
        "definition": "via",
        "layer_range": ["TOP", "BOTTOM"],
        "position": ["-1mm", "2.5mm"],
        "net_name": "GND",
    },
    {
        "name": "gvia_r_1",
        "definition": "via",
        "layer_range": ["TOP", "BOTTOM"],
        "position": ["1mm", "0.5mm"],
        "net_name": "GND",
    },
    {
        "name": "gvia_r_2",
        "definition": "via",
        "layer_range": ["TOP", "BOTTOM"],
        "position": ["1mm", "1.5mm"],
        "net_name": "GND",
    },
    {
        "name": "gvia_r_3",
        "definition": "via",
        "layer_range": ["TOP", "BOTTOM"],
        "position": ["1mm", "2.5mm"],
        "net_name": "GND",
    },
]

cfg["ports"] = [
    {
        "name": "wport_1",
        "type": "wave_port",
        "primitive_name": "trace_1",
        "point_on_edge": [0, 0],
        "horizontal_extent_factor": 10,
        "vertical_extent_factor": 2,
        "pec_launch_width": "0,2mm",
    },
    {
        "name": "wport_2",
        "type": "wave_port",
        "primitive_name": "trace_1",
        "point_on_edge": [0, "3mm"],
        "horizontal_extent_factor": 10,
        "vertical_extent_factor": 2,
        "pec_launch_width": "0,2mm",
    },
]
# -

# Create the config file.

file_json = os.path.join(temp_folder.name, "cfg.json")
with open(file_json, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

# Apply configuration to the example layout

edbapp.configuration.load(config_file=file_json)
edbapp.configuration.run()

# Save and close EDB.

edbapp.save()
edbapp.close()

# ## Load edb into HFSS 3D Layout.

h3d = Hfss3dLayout(edbapp.edbpath, version=AEDT_VERSION, non_graphical=NG_MODE, new_desktop=True)

# Shut Down Electronics Desktop

h3d.close_desktop()

# All project files are saved in the folder ``temp_file.dir``. If you've run this example as a Jupyter notebook you
# can retrieve those project files.
