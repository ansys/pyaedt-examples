# # Set up EDB for Serdes channel S-parameter extraction

# ## Import the required packages

import json

# +
import os
import tempfile

from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core.downloads import download_file

from pyedb import Edb

AEDT_VERSION = "2024.2"
NG_MODE = False

# -

# Download the example PCB data.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
file_edb = download_file(source="edb/ANSYS-HSD_V1.aedb", destination=temp_folder.name)
download_file(source="touchstone", name="GRM32_DC0V_25degC_series.s2p", destination=os.path.split(file_edb)[0])

# ## Load example layout

edbapp = Edb(file_edb, edbversion=AEDT_VERSION)

# ## Create config file

cfg_general = {"anti_pads_always_on": True, "suppress_pads": True}

# Define dielectric materials, stackup and surface roughness model.

cfg_stackup = {
    "materials": [
        {"name": "copper", "permittivity": 1, "conductivity": 58000000.0},
        {"name": "megtron4", "permittivity": 3.77, "dielectric_loss_tangent": 0.005},
        {"name": "solder_resist", "permittivity": 3.0, "dielectric_loss_tangent": 0.035},
    ],
    "layers": [
        {
            "name": "Top",
            "type": "signal",
            "material": "copper",
            "fill_material": "solder_resist",
            "thickness": "0.035mm",
            "roughness": {
                "top": {"model": "huray", "nodule_radius": "0.5um", "surface_ratio": "5"},
                "bottom": {"model": "huray", "nodule_radius": "0.5um", "surface_ratio": "5"},
                "side": {"model": "huray", "nodule_radius": "0.5um", "surface_ratio": "5"},
                "enabled": True,
            },
        },
        {"name": "DE1", "type": "dielectric", "material": "megtron4", "fill_material": "", "thickness": "0.1mm"},
        {"name": "Inner1", "type": "signal", "material": "copper", "fill_material": "megtron4", "thickness": "0.017mm"},
        {"name": "DE2", "type": "dielectric", "material": "megtron4", "fill_material": "", "thickness": "0.088mm"},
        {"name": "Inner2", "type": "signal", "material": "copper", "fill_material": "megtron4", "thickness": "0.017mm"},
        {"name": "DE3", "type": "dielectric", "material": "megtron4", "fill_material": "", "thickness": "0.1mm"},
        {"name": "Inner3", "type": "signal", "material": "copper", "fill_material": "megtron4", "thickness": "0.017mm"},
        {"name": "Megtron4-1mm", "type": "dielectric", "material": "megtron4", "fill_material": "", "thickness": 0.001},
        {"name": "Inner4", "type": "signal", "material": "copper", "fill_material": "megtron4", "thickness": "0.017mm"},
        {"name": "DE5", "type": "dielectric", "material": "megtron4", "fill_material": "", "thickness": "0.1mm"},
        {"name": "Inner5", "type": "signal", "material": "copper", "fill_material": "megtron4", "thickness": "0.017mm"},
        {"name": "DE6", "type": "dielectric", "material": "megtron4", "fill_material": "", "thickness": "0.088mm"},
        {"name": "Inner6", "type": "signal", "material": "copper", "fill_material": "megtron4", "thickness": "0.017mm"},
        {"name": "DE7", "type": "dielectric", "material": "megtron4", "fill_material": "", "thickness": "0.1mm"},
        {
            "name": "Bottom",
            "type": "signal",
            "material": "copper",
            "fill_material": "solder_resist",
            "thickness": "0.035mm",
        },
    ],
}

# Define Component with solderballs.

cfg_components = [
    {
        "reference_designator": "U1",
        "part_type": "io",
        "solder_ball_properties": {"shape": "cylinder", "diameter": "300um", "height": "300um"},
        "port_properties": {
            "reference_offset": "0",
            "reference_size_auto": True,
            "reference_size_x": 0,
            "reference_size_y": 0,
        },
    }
]

# Edit via padstack definition. Add backdrilling.

cfg_padstacks = {
    "definitions": [
        {
            "name": "v40h15-2",
            "material": "copper",
            "hole_range": "upper_pad_to_lower_pad",
            "hole_parameters": {"shape": "circle", "diameter": "0.2mm"},
        },
        {
            "name": "v35h15-1",
            "material": "copper",
            "hole_range": "upper_pad_to_lower_pad",
            "hole_parameters": {"shape": "circle", "diameter": "0.25mm"},
        },
    ],
    "instances": [
        {
            "name": "Via313",
            "backdrill_parameters": {
                "from_bottom": {"drill_to_layer": "Inner3", "diameter": "1mm", "stub_length": "0.2mm"}
            },
        },
        {
            "name": "Via314",
            "backdrill_parameters": {
                "from_bottom": {"drill_to_layer": "Inner3", "diameter": "1mm", "stub_length": "0.2mm"}
            },
        },
    ],
}

# Define ports.

cfg_ports = [
    {
        "name": "port_1",
        "reference_designator": "U1",
        "type": "coax",
        "positive_terminal": {"net": "PCIe_Gen4_TX2_CAP_P"},
    },
    {
        "name": "port_2",
        "reference_designator": "U1",
        "type": "coax",
        "positive_terminal": {"net": "PCIe_Gen4_TX2_CAP_N"},
    },
    {
        "name": "port_3",
        "reference_designator": "X1",
        "type": "circuit",
        "positive_terminal": {"pin": "B8"},
        "negative_terminal": {"pin": "B7"},
    },
    {
        "name": "port_4",
        "reference_designator": "X1",
        "type": "circuit",
        "positive_terminal": {"pin": "B9"},
        "negative_terminal": {"pin": "B10"},
    },
]

# Define S-parameter assignment

cfg_s_parameters = [
    {
        "name": "cap_10nf",
        "file_path": "$PROJECTDIR\\touchstone\\GRM32_DC0V_25degC_series.s2p",
        "component_definition": "CAPC1005X55X25LL05T10",
        "components": ["C375", "C376"],
        "reference_net": "GND",
    }
]

# Define SIwave setup.

cfg_setups = [
    {
        "name": "siwave_setup",
        "type": "siwave_ac",
        "si_slider_position": 1,
        "freq_sweep": [
            {
                "name": "Sweep1",
                "type": "interpolation",
                "frequencies": [
                    {"distribution": "linear_scale", "start": "50MHz", "stop": "20GHz", "increment": "50MHz"}
                ],
            }
        ],
    }
]

# Define cutout.

cfg_operations = {
    "cutout": {
        "signal_list": ["PCIe_Gen4_TX2_CAP_P", "PCIe_Gen4_TX2_CAP_N", "PCIe_Gen4_TX2_P", "PCIe_Gen4_TX2_N"],
        "reference_list": ["GND"],
        "custom_extent": [
            [0.014, 0.055],
            [0.03674271504652968, 0.05493094625752912],
            [0.07, 0.039],
            [0.07, 0.034],
            [0.05609890516829415, 0.03395233061637539],
            [0.014, 0.044],
        ],
    }
}

# Create final configuration.

cfg = {
    "general": cfg_general,
    "stackup": cfg_stackup,
    "components": cfg_components,
    "padstacks": cfg_padstacks,
    "ports": cfg_ports,
    "s_parameters": cfg_s_parameters,
    "setups": cfg_setups,
    "operations": cfg_operations,
}

# Create the config file.

file_json = os.path.join(temp_folder.name, "edb_configuration.json")
with open(file_json, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

# ## Apply Config file

# Apply configuration to the example layout

edbapp.configuration.load(config_file=file_json)
edbapp.configuration.run()

edbapp.nets.plot(nets=[])

# Save and close EDB.

edbapp.save()
edbapp.close()

# The configured EDB file is saved in a temp folder.

print(temp_folder.name)

# ## Load edb into HFSS 3D Layout.

h3d = Hfss3dLayout(edbapp.edbpath, version=AEDT_VERSION, non_graphical=NG_MODE, new_desktop=True)

# Create differential pair definition.

h3d.set_differential_pair(
    differential_mode="DIFF_BGA",
    assignment="port_1",
    reference="port_2",
)

h3d.set_differential_pair(
    differential_mode="DIFF_CONN",
    assignment="port_3",
    reference="port_4",
)

# Solve.

h3d.analyze(setup="siwave_setup")

# Plot insertion loss.

solutions = h3d.post.get_solution_data(expressions="mag(S(DIFF_CONN,DIFF_BGA))", context="Differential Pairs")
solutions.plot(formula="db20")

# Shut Down Electronics Desktop

h3d.close_desktop()

# All project files are saved in the folder ``temp_file.dir``. If you've run this example as a Jupyter notebook you
# can retrieve those project files.
