# # Double Pulse Test
#
# Description: build the equivalent circuit of a DPT
#
# Most examples can be described as a series of steps that comprise a workflow.
# 1. Import packages and instantiate the application.
# 2. Insert Circuit Components
# 3. Create the Wiring
# 4. Insert simulation set up
# 3. View the results.
#
# Keywords: **Power Electronics**, **Double Pulse Testing**

# ## Perform imports and define constants
#
# Perform required imports.

import os
import tempfile
import time

import ansys.aedt.core

# Define constants.

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT and application
#
# Create an instance of the application (such as ``Maxwell3d`` or``Hfss``)
# with a class (such as ``aedt_app`` or``hfss``) by providing
# the project and design names, the solver, and the version.

project_name = os.path.join(temp_folder.name, "my_project.aedt")
setup_name = "MyTransient"

aedt_app = ansys.aedt.core.Circuit(
    project=ansys.aedt.core.generate_unique_project_name(),
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)
aedt_app.modeler.schematic.schematic_units = "mil"

# ## Preprocess
#
# Initialize dictionaries that contain all the definitions for the design variables.

des_properties = {
    "VoltageDCbus": "400V",
    "Rg1": "2.2",
    "Rg2": "2.2",
    "Cdclink": "0.0005farad",
    "lload": "7.7e-5",
    "Vgate_top": "-5V",
    "rload": "0.1",
    "Rdclink": "1e6",
    "Vpwl_high": "18.0V",
    "Vpwl_low": "-5.0V",
}

# Define design variables from the created dictionaries.
for k, v in des_properties.items():
    aedt_app[k] = v

# Insert circuit elements.
y_upper_pin = 5200
y_lower_pin = 2000

time_list_pwl = [
    0.0,
    5.0e-6,
    5.001e-6,
    9.825e-06,
    9.826e-06,
    1.1e-05,
    1.1001e-05,
    1.3e-05,
    1.3001e-05,
]
volt_list_pwl = [
    "Vpwl_low",
    "Vpwl_low",
    "Vpwl_high",
    "Vpwl_high",
    "Vpwl_low",
    "Vpwl_low",
    "Vpwl_high",
    "Vpwl_high",
    "Vpwl_low",
]
vpwl = aedt_app.modeler.components.create_voltage_pwl(
    name="Vpwl",
    time_list=time_list_pwl,
    voltage_list=volt_list_pwl,
    location=[600, 2800],
)
vgatetop = aedt_app.modeler.components.create_voltage_dc(
    name="Vgate_top", value="Vgate_top", location=[600, 4500]
)
vdcbus = aedt_app.modeler.components.create_voltage_dc(
    name="Vdcbus", value="VoltageDCbus", location=[-1800, 3800]
)

cdclink = aedt_app.modeler.schematic.create_capacitor(
    name="C_DClink", value="Cdclink", location=[-1300, 3800], angle=90
)
rdclink = aedt_app.modeler.schematic.create_resistor(
    name="R_DClink", value="Rdclink", location=[-700, 3800], angle=90
)
lload = aedt_app.modeler.schematic.create_inductor(
    name="Lload", value="lload", location=[3000, 4800], angle=-90
)
rload = aedt_app.modeler.schematic.create_resistor(
    name="Rload", value="rload", location=[3000, 4300], angle=90
)
rg1 = aedt_app.modeler.schematic.create_resistor(
    name="Rg1", value="Rg1", location=[1400, 4700], angle=180
)
rg2 = aedt_app.modeler.schematic.create_resistor(
    name="Rg2", value="Rg2", location=[1400, 3100], angle=180
)

voltm_g = aedt_app.modeler.components.components_catalog["Probes:VPROBE_DIFF"].place(
    "voltage_g"
)
voltm_g.parameters["Name"] = "voltage_g"  # does not work with amm.top.name = 'Itop'
voltm_g.location = [100, 2900]
voltm_g.angle = 270

voltm_ds = aedt_app.modeler.components.components_catalog["Probes:VPROBE_DIFF"].place(
    "voltage_ds"
)
voltm_ds.parameters["Name"] = "voltage_ds"  # does not work with amm.top.name = 'Itop'
voltm_ds.location = [2500, 3300]
voltm_ds.angle = 0

amm_top = aedt_app.modeler.components.components_catalog["Probes:IPROBE"].place(
    "Itop"
)  # 1100 , 5200, angle=180
amm_top.parameters["Name"] = "Itop"  # does not work with amm.top.name = 'Itop'
amm_top.location = [1100, 5200]
amm_top.angle = 0

amm_ind = aedt_app.modeler.components.components_catalog["Probes:IPROBE"].place(
    "Iload"
)  # 1100 , 4000, angle = 0
amm_ind.parameters["Name"] = "Iinductor"
amm_ind.location = [2500, 4000]
amm_ind.angle = 0

amm_bot = aedt_app.modeler.components.components_catalog["Probes:IPROBE"].place(
    "Ibottom"
)  # 2000 , 3600, angle = 270
amm_bot.parameters["Name"] = "Ibottom"
amm_bot.location = [2000, 3600]
amm_bot.angle = 270

# Add nmos component from Component Library.
# Please check that chosen component has the attribute .place
# If you need to insert a component from a spice model, please use the method: aedt_app.modeler.components.create_component_from_spicemodel

nmos_h = aedt_app.modeler.components.components_catalog[
    "Power Electronics Tools\\Power Semiconductors\\MOSFET\\STMicroelectronics:SCT040H65G3AG_V2"
].place("NMOS_HS")
nmos_h.location = [1500, 4700]
nmos_h.angle = 0

nmos_l = aedt_app.modeler.components.components_catalog[
    "Power Electronics Tools\\Power Semiconductors\\MOSFET\\STMicroelectronics:SCT040H65G3AG_V2"
].place("NMOS_LS")
nmos_l.location = [1500, 3100]
nmos_l.angle = 0

# Create wiring to complete the schematic.

aedt_app.modeler.schematic.connect_components_in_series(
    assignment=[lload, rload], use_wire=True
)
aedt_app.modeler.schematic.connect_components_in_series(
    assignment=[vgatetop, rg1], use_wire=True
)
aedt_app.modeler.schematic.connect_components_in_series(
    assignment=[vpwl, rg2], use_wire=True
)

aedt_app.modeler.schematic.create_wire(
    [
        [vdcbus.pins[1].location[0], vdcbus.pins[1].location[1]],
        [vdcbus.pins[1].location[0], y_upper_pin],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [cdclink.pins[1].location[0], cdclink.pins[1].location[1]],
        [cdclink.pins[1].location[0], y_upper_pin],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [rdclink.pins[0].location[0], rdclink.pins[0].location[1]],
        [rdclink.pins[0].location[0], y_upper_pin],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [lload.pins[0].location[0], lload.pins[0].location[1]],
        [lload.pins[0].location[0], y_upper_pin],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [lload.pins[0].location[0], y_upper_pin],
        [nmos_h.pins[0].location[0], y_upper_pin],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [vdcbus.pins[0].location[0], y_upper_pin],
        [amm_top.pins[0].location[0], amm_top.pins[0].location[1]],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [amm_top.pins[1].location[0], amm_top.pins[1].location[1]],
        [nmos_h.pins[0].location[0], y_upper_pin],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [nmos_h.pins[0].location[0], y_upper_pin],
        [nmos_h.pins[0].location[0], nmos_h.pins[0].location[1]],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [voltm_g.pins[1].location[0], voltm_g.pins[1].location[1]],
        [voltm_g.pins[1].location[0], vpwl.pins[0].location[1]],
        [vpwl.pins[0].location[0], vpwl.pins[0].location[1]],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [vpwl.pins[0].location[0], vpwl.pins[0].location[1]],
        [nmos_l.pins[3].location[0], vpwl.pins[0].location[1]],
        [nmos_l.pins[3].location[0], nmos_l.pins[3].location[1]],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [vgatetop.pins[0].location[0], vgatetop.pins[0].location[1]],
        [nmos_h.pins[3].location[0], vgatetop.pins[0].location[1]],
        [nmos_h.pins[3].location[0], nmos_h.pins[3].location[1]],
    ]
)

aedt_app.modeler.schematic.create_wire(
    [
        [nmos_h.pins[0].location[0], y_upper_pin],
        [nmos_h.pins[0].location[0], nmos_h.pins[0].location[1]],
    ]
)

aedt_app.modeler.schematic.create_wire(
    [
        [rload.pins[1].location[0], rload.pins[1].location[1]],
        [rload.pins[1].location[0], amm_ind.pins[1].location[1]],
        [amm_ind.pins[1].location[0], amm_ind.pins[1].location[1]],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [amm_ind.pins[0].location[0], amm_ind.pins[0].location[1]],
        [amm_bot.pins[0].location[0], amm_ind.pins[0].location[1]],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [voltm_g.pins[0].location[0], voltm_g.pins[0].location[1]],
        [vpwl.pins[0].location[0], voltm_g.pins[0].location[1]],
    ]
)

aedt_app.modeler.schematic.create_wire(
    [
        [vdcbus.pins[0].location[0], vdcbus.pins[0].location[1]],
        [vdcbus.pins[0].location[0], y_lower_pin],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [cdclink.pins[0].location[0], cdclink.pins[0].location[1]],
        [cdclink.pins[0].location[0], y_lower_pin],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [rdclink.pins[1].location[0], rdclink.pins[1].location[1]],
        [rdclink.pins[1].location[0], y_lower_pin],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [nmos_l.pins[2].location[0], nmos_l.pins[2].location[1]],
        [nmos_l.pins[2].location[0], y_lower_pin],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [voltm_ds.pins[1].location[0], voltm_ds.pins[1].location[1]],
        [voltm_ds.pins[1].location[0], y_lower_pin],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [nmos_l.pins[2].location[0], nmos_l.pins[2].location[1]],
        [nmos_l.pins[2].location[0], y_lower_pin],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [nmos_h.pins[2].location[0], nmos_h.pins[2].location[1]],
        [amm_bot.pins[0].location[0], amm_bot.pins[0].location[1]],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [nmos_l.pins[0].location[0], nmos_l.pins[0].location[1]],
        [amm_bot.pins[1].location[0], amm_bot.pins[1].location[1]],
    ]
)
aedt_app.modeler.schematic.create_wire(
    [
        [nmos_l.pins[0].location[0], nmos_l.pins[0].location[1]],
        [voltm_ds.pins[0].location[0], voltm_ds.pins[0].location[1]],
    ]
)

aedt_app.modeler.schematic.create_wire(
    [
        [vdcbus.pins[1].location[0], y_lower_pin],
        [voltm_ds.pins[1].location[0], y_lower_pin],
    ]
)
gnd = aedt_app.modeler.components.create_gnd(
    location=[voltm_ds.pins[1].location[0], y_lower_pin - 100]
)

rg1.pins[1].connect_to_component(assignment=nmos_h.pins[1], use_wire=True)
rg2.pins[1].connect_to_component(assignment=nmos_l.pins[1], use_wire=True)

# Create a transient setup

setup1 = aedt_app.create_setup(
    name=setup_name, setup_type=aedt_app.SETUPS.NexximTransient
)
setup1.props["TransientData"] = ["0.05ns", "15us"]
aedt_app.modeler.zoom_to_fit()

# Solve transient setup

aedt_app.analyze_setup(setup_name)

# ## Postprocess
#
# Create a report

new_report = aedt_app.post.reports_by_category.standard(
    ["V(voltage_g)", "V(voltage_ds)", "Ipositive(Ibottom)", "Ipositive(Iinductor)"]
)
new_report.domain = "Time"
new_report.plot_name = "Plot V,I"
new_report.create()

# ## Release AEDT

aedt_app.save_project()
aedt_app.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
