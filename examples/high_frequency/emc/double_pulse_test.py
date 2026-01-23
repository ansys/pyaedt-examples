# # Double Pulse Test
#
# Description: build the equivalent circuit of a DPT
#
# In this example the steps to build up the circuit schematic are shown.
# 1. Insert Circuit Components
# 3. Create the Wiring
# 4. Insert simulation set up
# 3. View the results.
#
# Keywords: **Power Electronics**, **Double Pulse Testing**

# ## Prerequisites
#
# ### Perform imports

# +
import os
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.generic.constants import Setups
# -

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ### Launch Circuit

project_name = os.path.join(temp_folder.name, "my_project.aedt")
circuit = ansys.aedt.core.Circuit(
    project=project_name,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)
circuit.modeler.schematic_units = "mil"

# ## Variable initialization to create a parametric design
#
# Initialize dictionary that contain all the definitions for the design variables.

design_properties = {
    "VoltageDCbus": "400V",
    "r_g1": "2.2",
    "r_g2": "2.2",
    "c_dc_link": "0.0005farad",
    "l_load": "7.7e-5",
    "Vgate_top": "-5V",
    "r_load": "0.1",
    "r_dc_link": "1e6",
    "v_pwl_high": "18.0V",
    "v_pwl_low": "-5.0V",
}

# Define design variables from the created dictionaries.

for k, v in design_properties.items():
    circuit[k] = v

# ## Insert Circuit Elements into the Schematic
#
# Define starting position for component placement.

y_upper_pin = 5200
y_lower_pin = 2000

# Define parametrically high and low voltage level for pwl voltage source.

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
    "v_pwl_low",
    "v_pwl_low",
    "v_pwl_high",
    "v_pwl_high",
    "v_pwl_low",
    "v_pwl_low",
    "v_pwl_high",
    "v_pwl_high",
    "v_pwl_low",
]

# Add circuit components to the schematic.

v_pwl = circuit.modeler.schematic.create_voltage_pwl(
    name="v_pwl",
    time_list=time_list_pwl,
    voltage_list=volt_list_pwl,
    location=[600, 2800],
)
v_gate_top = circuit.modeler.schematic.create_voltage_dc(
    name="Vgate_top", value="Vgate_top", location=[600, 4500]
)
v_dc_bus = circuit.modeler.schematic.create_voltage_dc(
    name="v_dc_bus", value="VoltageDCbus", location=[-1800, 3800]
)
c_dc_link = circuit.modeler.schematic.create_capacitor(
    name="c_dc_link", value="c_dc_link", location=[-1300, 3800], angle=90
)
r_dc_link = circuit.modeler.schematic.create_resistor(
    name="r_dc_link", value="r_dc_link", location=[-700, 3800], angle=90
)
l_load = circuit.modeler.schematic.create_inductor(
    name="l_load", value="l_load", location=[3000, 4800], angle=-90
)
r_load = circuit.modeler.schematic.create_resistor(
    name="r_load", value="r_load", location=[3000, 4300], angle=90
)
r_g1 = circuit.modeler.schematic.create_resistor(
    name="r_g1", value="r_g1", location=[1400, 4700], angle=180
)
r_g2 = circuit.modeler.schematic.create_resistor(
    name="r_g2", value="r_g2", location=[1400, 3100], angle=180
)
voltm_g = circuit.modeler.schematic.components_catalog["Probes:VPROBE_DIFF"].place(
    assignment="voltage_g", location=[100, 2900], angle=270
)
voltm_g.parameters["Name"] = "voltage_g"
voltm_ds = circuit.modeler.schematic.components_catalog["Probes:VPROBE_DIFF"].place(
    assignment="voltage_ds", location=[2500, 3300], angle=0
)
voltm_ds.parameters["Name"] = "voltage_ds"
amm_top = circuit.modeler.schematic.components_catalog["Probes:IPROBE"].place(
    assignment="Itop", location=[1100, 5200], angle=0
)
amm_top.parameters["Name"] = "Itop"
amm_ind = circuit.modeler.schematic.components_catalog["Probes:IPROBE"].place(
    assignment="Iinductor", location=[2500, 4000], angle=0
)
amm_ind.parameters["Name"] = "Iinductor"
amm_bot = circuit.modeler.schematic.components_catalog["Probes:IPROBE"].place(
    assignment="Ibottom", location=[2000, 3600], angle=270
)
amm_bot.parameters["Name"] = "Ibottom"

# ## Add nMOS components from Component Library.
#
# Please check that chosen component can access the method place()
# If you need to insert a component from a spice model,
# please use the method: circuit.modeler.components.create_component_from_spicemodel

nmos_h = circuit.modeler.schematic.components_catalog[
    "Power Electronics Tools\\Power Semiconductors\\MOSFET\\STMicroelectronics:SCT040H65G3AG_V2"
].place(assignment="NMOS_HS", location=[1500, 4700], angle=0)
nmos_l = circuit.modeler.schematic.components_catalog[
    "Power Electronics Tools\\Power Semiconductors\\MOSFET\\STMicroelectronics:SCT040H65G3AG_V2"
].place("NMOS_LS", location=[1500, 3100], angle=0)

# ## Create wiring to complete the schematic.

circuit.modeler.schematic.connect_components_in_series(
    assignment=[l_load, r_load], use_wire=True
)
circuit.modeler.schematic.connect_components_in_series(
    assignment=[v_gate_top, r_g1], use_wire=True
)
circuit.modeler.schematic.connect_components_in_series(
    assignment=[v_pwl, r_g2], use_wire=True
)
circuit.modeler.schematic.create_wire(
    [
        [v_dc_bus.pins[1].location[0], v_dc_bus.pins[1].location[1]],
        [v_dc_bus.pins[1].location[0], y_upper_pin],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [c_dc_link.pins[1].location[0], c_dc_link.pins[1].location[1]],
        [c_dc_link.pins[1].location[0], y_upper_pin],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [r_dc_link.pins[0].location[0], r_dc_link.pins[0].location[1]],
        [r_dc_link.pins[0].location[0], y_upper_pin],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [l_load.pins[0].location[0], l_load.pins[0].location[1]],
        [l_load.pins[0].location[0], y_upper_pin],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [l_load.pins[0].location[0], y_upper_pin],
        [nmos_h.pins[0].location[0], y_upper_pin],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [v_dc_bus.pins[0].location[0], y_upper_pin],
        [amm_top.pins[0].location[0], amm_top.pins[0].location[1]],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [amm_top.pins[1].location[0], amm_top.pins[1].location[1]],
        [nmos_h.pins[0].location[0], y_upper_pin],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [nmos_h.pins[0].location[0], y_upper_pin],
        [nmos_h.pins[0].location[0], nmos_h.pins[0].location[1]],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [voltm_g.pins[1].location[0], voltm_g.pins[1].location[1]],
        [voltm_g.pins[1].location[0], v_pwl.pins[0].location[1]],
        [v_pwl.pins[0].location[0], v_pwl.pins[0].location[1]],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [v_pwl.pins[0].location[0], v_pwl.pins[0].location[1]],
        [nmos_l.pins[3].location[0], v_pwl.pins[0].location[1]],
        [nmos_l.pins[3].location[0], nmos_l.pins[3].location[1]],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [v_gate_top.pins[0].location[0], v_gate_top.pins[0].location[1]],
        [nmos_h.pins[3].location[0], v_gate_top.pins[0].location[1]],
        [nmos_h.pins[3].location[0], nmos_h.pins[3].location[1]],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [nmos_h.pins[0].location[0], y_upper_pin],
        [nmos_h.pins[0].location[0], nmos_h.pins[0].location[1]],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [r_load.pins[1].location[0], r_load.pins[1].location[1]],
        [r_load.pins[1].location[0], amm_ind.pins[1].location[1]],
        [amm_ind.pins[1].location[0], amm_ind.pins[1].location[1]],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [amm_ind.pins[0].location[0], amm_ind.pins[0].location[1]],
        [amm_bot.pins[0].location[0], amm_ind.pins[0].location[1]],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [voltm_g.pins[0].location[0], voltm_g.pins[0].location[1]],
        [v_pwl.pins[0].location[0], voltm_g.pins[0].location[1]],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [v_dc_bus.pins[0].location[0], v_dc_bus.pins[0].location[1]],
        [v_dc_bus.pins[0].location[0], y_lower_pin],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [c_dc_link.pins[0].location[0], c_dc_link.pins[0].location[1]],
        [c_dc_link.pins[0].location[0], y_lower_pin],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [r_dc_link.pins[1].location[0], r_dc_link.pins[1].location[1]],
        [r_dc_link.pins[1].location[0], y_lower_pin],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [nmos_l.pins[2].location[0], nmos_l.pins[2].location[1]],
        [nmos_l.pins[2].location[0], y_lower_pin],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [voltm_ds.pins[1].location[0], voltm_ds.pins[1].location[1]],
        [voltm_ds.pins[1].location[0], y_lower_pin],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [nmos_l.pins[2].location[0], nmos_l.pins[2].location[1]],
        [nmos_l.pins[2].location[0], y_lower_pin],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [nmos_h.pins[2].location[0], nmos_h.pins[2].location[1]],
        [amm_bot.pins[0].location[0], amm_bot.pins[0].location[1]],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [nmos_l.pins[0].location[0], nmos_l.pins[0].location[1]],
        [amm_bot.pins[1].location[0], amm_bot.pins[1].location[1]],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [nmos_l.pins[0].location[0], nmos_l.pins[0].location[1]],
        [voltm_ds.pins[0].location[0], voltm_ds.pins[0].location[1]],
    ]
)
circuit.modeler.schematic.create_wire(
    [
        [v_dc_bus.pins[1].location[0], y_lower_pin],
        [voltm_ds.pins[1].location[0], y_lower_pin],
    ]
)
gnd = circuit.modeler.schematic.create_gnd(
    location=[voltm_ds.pins[1].location[0], y_lower_pin - 100]
)
r_g1.pins[1].connect_to_component(assignment=nmos_h.pins[1], use_wire=True)
r_g2.pins[1].connect_to_component(assignment=nmos_l.pins[1], use_wire=True)

# ## Create a transient setup

setup_name = "MyTransient"
setup1 = circuit.create_setup(
    name=setup_name, setup_type=Setups.NexximTransient
)
setup1.props["TransientData"] = ["0.05ns", "15us"]
circuit.modeler.zoom_to_fit()

# Solve transient setup

circuit.analyze(setup_name, cores=NUM_CORES)

# ## Plot Double Pulse Test results
#
# Create a report

new_report = circuit.post.create_report(
    expressions=[
        "V(voltage_g)",
        "V(voltage_ds)",
        "Ipositive(Ibottom)",
        "Ipositive(Iinductor)",
    ],
    domain="Time",
    plot_name="Plot V,I",
    context={"time_stop": "15us"}
)

# ## Finish
#
# ### Save the project

circuit.save_project()
circuit.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
