# # Set up EDB for PCB DC IR Analysis
# This example shows how to set up the electronics database (EDB) for DC IR analysis from a single
# configuration file.

# ## Import the required packages

# +
import json
import os
import tempfile

from ansys.aedt.core import Hfss3dLayout, Icepak
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
cfg["sources"] = []

# ## Update stackup

cfg["stackup"] = {
    "layers": [
        {"name": "Top", "type": "signal", "material": "copper", "fill_material": "FR4_epoxy", "thickness": "0.035mm"},
        {"name": "DE1", "type": "dielectric", "material": "FR4_epoxy", "fill_material": "", "thickness": "0.1mm"},
        {
            "name": "Inner1",
            "type": "signal",
            "material": "copper",
            "fill_material": "FR4_epoxy",
            "thickness": "0.017mm",
        },
        {"name": "DE2", "type": "dielectric", "material": "FR4_epoxy", "fill_material": "", "thickness": "0.088mm"},
        {
            "name": "Inner2",
            "type": "signal",
            "material": "copper",
            "fill_material": "FR4_epoxy",
            "thickness": "0.017mm",
        },
        {"name": "DE3", "type": "dielectric", "material": "FR4_epoxy", "fill_material": "", "thickness": "0.1mm"},
        {
            "name": "Inner3",
            "type": "signal",
            "material": "copper",
            "fill_material": "FR4_epoxy",
            "thickness": "0.017mm",
        },
        {
            "name": "FR4_epoxy-1mm",
            "type": "dielectric",
            "material": "FR4_epoxy",
            "fill_material": "",
            "thickness": "1mm",
        },
        {
            "name": "Inner4",
            "type": "signal",
            "material": "copper",
            "fill_material": "FR4_epoxy",
            "thickness": "0.017mm",
        },
        {"name": "DE5", "type": "dielectric", "material": "FR4_epoxy", "fill_material": "", "thickness": "0.1mm"},
        {
            "name": "Inner5",
            "type": "signal",
            "material": "copper",
            "fill_material": "FR4_epoxy",
            "thickness": "0.017mm",
        },
        {"name": "DE6", "type": "dielectric", "material": "FR4_epoxy", "fill_material": "", "thickness": "0.088mm"},
        {
            "name": "Inner6",
            "type": "signal",
            "material": "copper",
            "fill_material": "FR4_epoxy",
            "thickness": "0.017mm",
        },
        {"name": "DE7", "type": "dielectric", "material": "FR4_epoxy", "fill_material": "", "thickness": "0.1mm"},
        {
            "name": "Bottom",
            "type": "signal",
            "material": "copper",
            "fill_material": "FR4_epoxy",
            "thickness": "0.035mm",
        },
    ]
}

# ## Define voltage source

cfg["sources"].append(
    {
        "name": "vrm",
        "reference_designator": "U2",
        "type": "voltage",
        "magnitude": 1,
        "positive_terminal": {"net": "1V0"},
        "negative_terminal": {"net": "GND"},
    }
)

# ## Define current source

cfg["sources"].append(
    {
        "name": "U1_1V0",
        "reference_designator": "U1",
        "type": "current",
        "magnitude": 10,
        "positive_terminal": {"net": "1V0"},
        "negative_terminal": {"net": "GND"},
    }
)

# ## Define SIwave DC IR analysis setup

cfg["setups"] = [
    {
        "name": "siwave_1",
        "type": "siwave_dc",
        "dc_slider_position": 1,
        "dc_ir_settings": {"export_dc_thermal_data": True},
    }
]

# ## Define Cutout

cfg["operations"] = {
    "cutout": {"signal_list": ["1V0"], "reference_list": ["GND"], "extent_type": "ConvexHull", "expansion_size": "20mm"}
}

# ## Define package for thermal analysis (optional)

cfg["package_definitions"] = [
    {
        "name": "package_1",
        "component_definition": "ALTR-FBGA1517-Ansys",
        "maximum_power": 0.5,
        "therm_cond": 2,
        "theta_jb": 3,
        "theta_jc": 4,
        "height": "1mm",
        "apply_to_all": False,
        "components": ["U1"],
    },
]

# ## Write configuration into a JSON file

file_json = os.path.join(temp_folder.name, "edb_configuration.json")
with open(file_json, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

# ## Import configuration into example layout

edbapp.configuration.load(config_file=file_json)

# Apply configuration to EDB.

edbapp.configuration.run()

# Save and close EDB.

edbapp.save()
edbapp.close()

# The configured EDB file is saved in a temp folder.

print(temp_folder.name)

# ## Load edb into HFSS 3D Layout.

h3d = Hfss3dLayout(edbapp.edbpath, version=AEDT_VERSION, non_graphical=NG_MODE, new_desktop=True)

# ## Prepare for electro-thermal analysis in Icepak (Optional)

h3d.modeler.set_temperature_dependence(include_temperature_dependence=True, enable_feedback=True, ambient_temp=22)

# ## Analyze

h3d.analyze()

# ## Plot DC voltage

voltage = h3d.post.create_fieldplot_layers_nets(
    layers_nets=[
        ["Inner2", "1V0"],
    ],
    quantity="Voltage",
    setup="siwave_1",
)

file_path_image = os.path.join(temp_folder.name, "voltage.jpg")
voltage.export_image(
    full_path=file_path_image,
    width=640,
    height=480,
    orientation="isometric",
    display_wireframe=True,
    selections=None,
    show_region=True,
    show_axis=True,
    show_grid=True,
    show_ruler=True,
)

# ## Plot power density

power_density = h3d.post.create_fieldplot_layers_nets(
    layers_nets=[
        ["Inner2", "no-net"],
    ],
    quantity="Power Density",
    setup="siwave_1",
)

file_path_image = os.path.join(temp_folder.name, "power_density.jpg")
power_density.export_image(
    full_path=file_path_image,
    width=640,
    height=480,
    orientation="isometric",
    display_wireframe=True,
    selections=None,
    show_region=True,
    show_axis=True,
    show_grid=True,
    show_ruler=True,
)

# ## Save HFSS 3D Layout project

h3d.save_project()

# ## Create an Icepak design

ipk = Icepak(version=AEDT_VERSION, non_graphical=NG_MODE, new_desktop=False)

# ## Create PCB

pcb = ipk.create_ipk_3dcomponent_pcb(
    compName="PCB_pyAEDT",
    setupLinkInfo=[h3d.project_file, h3d.design_name, "siwave_1", True, True],
    solutionFreq=None,
    resolution=0,
    extent_type="Bounding Box",
    powerin="0",
)

# ## Include pckage definition from Edb

pcb.included_parts = "Device"

# ## Adjust air region

region = ipk.modeler["Region"]
faces = [f.id for f in region.faces]
ipk.assign_pressure_free_opening(assignment=faces, boundary_name="Outlet")

# ## Setup mesh

glob_msh = ipk.mesh.global_mesh_region
glob_msh.global_region.positive_z_padding_type = "Absolute Offset"
glob_msh.global_region.positive_z_padding = "50 mm"
glob_msh.global_region.negative_z_padding_type = "Absolute Offset"
glob_msh.global_region.negative_z_padding = "80 mm"

glob_msh = ipk.mesh.global_mesh_region
glob_msh.manual_settings = True
glob_msh.settings["EnableMLM"] = True
glob_msh.settings["EnforeMLMType"] = "2D"
glob_msh.settings["2DMLMType"] = "Auto"
glob_msh.settings["MaxElementSizeY"] = "2mm"
glob_msh.settings["MaxElementSizeX"] = "2mm"
glob_msh.settings["MaxElementSizeZ"] = "3mm"
glob_msh.settings["MaxLevels"] = "2"

glob_msh.update()

# ## Place monitor

cpu = ipk.modeler["PCB_pyAEDT_U1_device"]
m1 = ipk.monitor.assign_face_monitor(
    face_id=cpu.top_face_z.id,
    monitor_quantity="Temperature",
    monitor_name="TemperatureMonitor1",
)

# ## Create Icepak setup

setup1 = ipk.create_setup(MaxIterations=10)

# Add 2-way coupling to the setup

ipk.assign_2way_coupling(number_of_iterations=1)

# ## Save

ipk.save_project()

# ## Shut Down Electronics Desktop

ipk.release_desktop()

# All project files are saved in the folder ``temp_file.dir``. If you've run this example as a Jupyter notebook you
# can retrieve those project files.
