# # HFSS 3D Layout: Pre-layout Signal Integrity
# This example shows how to create a parameterized layout design, and load the layout into HFSS 3D Layout for analysis and
# post-processing.
# - Create EDB
#     - Add material
#     - Create stackup
#     - Create a parameterized via padstack definition
#     - Create ground planes
#     - Create a component
#     - Create signal vias and traces
#     - Create ground stitching vias
#     - Create HFSS analysis setup and frequency sweep
# - Import EDB into HFSS 3D Layout
#     - Place SMA connector
#     - Analysis
#     - Plot return loss

# +
import os
import tempfile
from pyaedt import Edb
from pyaedt import Hfss3dLayout
from pyaedt.downloads import download_file
from ansys.pyaedt.examples.constants import AEDT_VERSION

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
# -

# Download example board.

sma_rf_connector = download_file(source="component_3d", name="SMA_RF_SURFACE_MOUNT.a3dcomp", destination=temp_folder.name
)

# Set ``NG_MODE`` to ``True`` in order to run in non-graphical mode. The example is currently set up to run in graphical mode.

NG_MODE = False

# # Create a layout design

# ## Import example design

aedb = os.path.join(temp_folder.name, "new_layout.aedb")
edbapp = Edb(edbpath=aedb, edbversion=AEDT_VERSION)

# ## Add material definitions

edbapp.materials.add_conductor_material(name="copper", conductivity=58000000)
edbapp.materials.add_dielectric_material(name="fr4_epoxy", permittivity=4, dielectric_loss_tangent=0.02)
edbapp.materials.add_dielectric_material(name="solder_mask", permittivity=3.1, dielectric_loss_tangent=0.035)

# ## Create stackup

edbapp.stackup.create_symmetric_stackup(
    layer_count=4,
    inner_layer_thickness="18um",
    outer_layer_thickness="50um",
    dielectric_thickness="100um",
    dielectric_material="fr4_epoxy",
    soldermask=True,
    soldermask_thickness="20um",
)

# ## Create parameterized padstack definition

# Create signal via padstack definition

edbapp["$antipad"] = "0.7mm"
edbapp.padstacks.create(
    padstackname="svia", holediam="0.3mm", antipaddiam="$antipad", paddiam="0.5mm"
)

# Create component pin padstack definition

edbapp.padstacks.create(
    padstackname="comp_pin",
    paddiam="400um",
    antipaddiam="600um",
    start_layer="TOP",
    stop_layer="TOP",
    antipad_shape="Circle",
    has_hole=False,
)

# ## Review stackup

edbapp.stackup.plot(plot_definitions="svia")

# ## Create ground planes

# +
board_width = "22mm"
board_length = "18mm"
board_center_point = [0, "5mm"]

gnd_l2 = edbapp.modeler.create_rectangle(
    layer_name="L2",
    center_point=board_center_point,
    width=board_width,
    height=board_length,
    representation_type="CenterWidthHeight",
    corner_radius="0mm",
    rotation="0deg",
)

gnd_l3 = edbapp.modeler.create_rectangle(
    layer_name="L3",
    center_point=board_center_point,
    width=board_width,
    height=board_length,
    representation_type="CenterWidthHeight",
    corner_radius="0mm",
    rotation="0deg",
)

gnd_bottom = edbapp.modeler.create_rectangle(
    layer_name="BOT",
    center_point=board_center_point,
    width=board_width,
    height=board_length,
    representation_type="CenterWidthHeight",
    corner_radius="0mm",
    rotation="0deg",
)
# -

# ## Create a component

edbapp.padstacks.place(position=[0, 0], definition_name="comp_pin", net_name="SIG", is_pin=True, via_name="1")

comp_pins = [
    edbapp.padstacks.place(position=["-6mm", 0], definition_name="comp_pin", net_name="GND", is_pin=True, via_name="2"),
    edbapp.padstacks.place(position=["6mm", 0], definition_name="comp_pin", net_name="GND", is_pin=True, via_name="3"),
]

comp_u1 = edbapp.components.create(pins=comp_pins, component_name="U1", component_part_name="BGA", placement_layer="TOP")
comp_u1.create_clearance_on_component(extra_soldermask_clearance=3.5e-3)


# ## Place vias

# Place a signal via

edbapp.padstacks.place(position=[0, 0], definition_name="svia", net_name="SIG", is_pin=False)

# Place ground stitching vias

edbapp.padstacks.place(position=["-1mm", 0], definition_name="svia", net_name="GND", is_pin=False)
edbapp.padstacks.place(position=["1mm", 0], definition_name="svia", net_name="GND", is_pin=False)
edbapp.padstacks.place(position=[0, "-1mm"], definition_name="svia", net_name="GND", is_pin=False)
edbapp.padstacks.place(position=[0, "1mm"], definition_name="svia", net_name="GND", is_pin=False)

# ## Create signal traces

edbapp["width"] = "0.15mm"
edbapp["gap"] = "0.1mm"

# Signal fanout

sig_trace = edbapp.modeler.create_trace(path_list=[[0, 0]],
                                        layer_name="BOT",
                                        width="width",
                                        net_name="SIG",
                                        start_cap_style="Round",
                                        end_cap_style="Round",
                                        corner_style="Round",
                                        )

sig_trace.add_point(x="0.5mm", y="0.5mm", incremental=True)
sig_trace.add_point(x=0, y="1mm", incremental=True)
sig_trace.add_point(x="-0.5mm", y="0.5mm", incremental=True)
sig_trace.add_point(x=0, y="1mm", incremental=True)
sig_path = sig_trace.get_center_line()

# Coplanar waveguide with ground with ground stitching vias

sig2_trace = edbapp.modeler.create_trace(path_list=[sig_path[-1]],
                                         layer_name="BOT",
                                         width="width",
                                         net_name="SIG",
                                         start_cap_style="Round",
                                         end_cap_style="Flat",
                                         corner_style="Round",
                                         )
sig2_trace.add_point(x=0, y="6mm", incremental=True)
sig2_trace.create_via_fence(distance="0.5mm", gap="1mm", padstack_name="svia")
sig2_trace.add_point(x=0, y="1mm", incremental=True)

# Create trace-to-ground clearance

sig2_path = sig_trace.get_center_line()
path_list = [sig_path, sig2_path]
for i in path_list:
    void = edbapp.modeler.create_trace(path_list=i, layer_name="BOT", width="width+gap*2",
                                       start_cap_style="Round",
                                       end_cap_style="Round",
                                       corner_style="Round")
    edbapp.modeler.add_void(shape=gnd_bottom, void_shape=void)

# Review

edbapp.nets.plot()

# ## Create ports

# Create a Wave port

sig2_trace.create_edge_port(name="p1_wave_port",
                            position="End",
                            port_type="Wave",
                            reference_layer=None,
                            horizontal_extent_factor=10,
                            vertical_extent_factor=10,
                            pec_launch_width="0.01mm")

# ## Create HFSS analysis setup

setup = edbapp.create_hfss_setup("Setup1")
setup.set_solution_single_frequency("5GHz", max_num_passes=1, max_delta_s="0.02")
setup.hfss_solver_settings.order_basis = "first"

# Add a frequency sweep to setup.
#
# When the simulation results are to
# be used for transient SPICE analysis, you should
# use the following strategy:
#
# - DC point
# - Logarithmic sweep from 1 kHz to 100 MHz
# - Linear scale for higher frequencies.

setup.add_frequency_sweep(
    "Sweep1",
    frequency_sweep=[
        ["linear count", "0", "1KHz", 1],
        ["log scale", "1KHz", "100MHz", 3],
        ["linear scale", "0.1GHz", "5GHz", "0.2GHz"],
    ],
)

# ## Save and close EDB

edbapp.save()
edbapp.close()

# # Analyze in HFSS 3D Layout

# ## Load edb into HFSS 3D Layout.

NG_MODE = False  # Open the UI to view the layout.
h3d = Hfss3dLayout(
    aedb,
    specified_version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop_session=True
)

# ## Place SMA RF connector

comp = h3d.modeler.place_3d_component(
    component_path=sma_rf_connector,
    number_of_terminals=1,
    placement_layer="TOP",
    component_name="sma_rf",
    pos_x=0,
    pos_y=0,
    create_ports=True,
)
comp.angle = "90deg"

# ## Analyze

h3d.analyze()

# ## Plot results

h3d.post.create_report("dB(S(port_1, port_1))")

traces = h3d.get_traces_for_plot(category="S")
solutions = h3d.post.get_solution_data(traces)
solutions.plot(traces, math_formula="db20")

# ## Close HFSS 3D Layout

h3d.close_desktop()

# ## Cleanup
#
# All project files are saved in the folder ``temp_file.dir``. If you've run this example as a Jupyter notbook you 
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
