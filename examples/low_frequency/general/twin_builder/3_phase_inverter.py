# # Title
#
# Description
#
# Keywords: **DCLink**, **Twinbuilder**, **Q3D**.

# ## Perform imports and define constants
#
# Perform required imports.

import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
from ansys.aedt.core.examples.downloads import download_file

# ## Define constants
#
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download AEDT file
#
# Set the local temporary folder to export the AEDT file to.

project_path = download_file(
    source="q3d_dynamic_link",
    name="busbar_q3d_tb.aedt",
    local_path=temp_folder.name,
)

# ## Launch Maxwell AEDT
#
# Create an instance of the ``Twinbuilder`` class.
# The Ansys Electronics Desktop will be launched with the active Twinbuilder design.
# The ``tb`` object is subsequently used to create and simulate the model.

tb = ansys.aedt.core.TwinBuilder(
    project=project_path,
    design="3ph_circuit",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Add Q3D component to Twinbuilder schematic
#
# Add a Q3D dynamic link to the Twinbuilder schematic.

comp = tb.add_q3d_dynamic_component(
    source_project=tb.project_name, source_design_name="q3d_3ph", setup="Setup1", sweep_name="Sweep1", coupling_matrix_name="Original", state_space_dynamic_link_type="RLGC"
)

tb = get_pyaedt_app(tb.project_name, "3ph_circuit")

# ## Place component on schematic
#
# Place the dynamic component on the schematic at the desired location (expressed in mm).
# Add page ports and ammeters to each terminal of the component.

x_position = 0.05
y_position = 0.05
comp.location = [x_position, y_position]

ammeter_x_factor = 0
previous_value = 0
reset = False
for pin in comp.pins:
    current_value = pin.angle
    if current_value != previous_value:
        if not reset:
            ammeter_x_factor = 0
            reset = True
        angle_page_port = 180
        angle_ammeter = 270
        ammeter_x_factor += 0.015
        label_position = "Right"
        ammeter_y_factor = -0.002
    else:
        angle_page_port = 0
        angle_ammeter = 90
        ammeter_x_factor -= 0.015
        label_position = "Left"
        ammeter_y_factor = 0.002

    prefix_1 = "dc_plus"
    prefix_2 = "dc_minus"
    prefix = prefix_1 if pin.name.startswith(prefix_1) else prefix_2
    terminal = pin.name.split(prefix, 1)[1].lstrip("_")
    ammeter = tb.modeler.schematic.create_component(
        name=terminal,
        component_library="Basic Elements\\Measurement\\Electrical",
        component_name="AM",
        location=[pin.location[0] + ammeter_x_factor, pin.location[1] - ammeter_y_factor],
        angle=angle_ammeter,
    )
    comp_page_port = tb.modeler.components.create_page_port(name=terminal, location=ammeter.pins[0].location, label_position=label_position, angle=angle_page_port)
    tb.modeler.schematic.create_wire([ammeter.pins[1].location, pin.location])

# ## Solve transient setup
#
# Solve the transient setup.

tb.analyze_setup("TR")

# Post-processing
#
# Create reports for the results of interest.

cap_currents = tb.post.create_report(
    expressions=["Ca.I", "Cb.I", "Cc.I"],
    primary_sweep_variable="Time",
    plot_name="Capacitor Currents",
)
# add markers at 10ms and 20ms
cap_currents.add_cartesian_x_marker("10ms")
cap_currents.add_cartesian_x_marker("20ms")

# Plot only between 10ms and 20ms
cap_currents_range = tb.post.create_report(
    expressions=["Ca.I", "Cb.I", "Cc.I"],
    primary_sweep_variable="Time",
    plot_name="Capacitor Currents - [10ms-20ms]",
)
cap_currents_range.edit_x_axis_scaling(min_scale="10ms", max_scale="20ms")

i_load = tb.post.create_report(
    expressions=["L4.I", "L5.I", "L6.I"],
    primary_sweep_variable="Time",
    plot_name="Load Currents",
)
i_dc = tb.post.create_report(
    expressions=["dc_ground.I"],
    primary_sweep_variable="Time",
    plot_name="Idc",
)
v_dc = tb.post.create_report(
    expressions=["Vdc_minus.V", "Vdc_plus.V"],
    primary_sweep_variable="Time",
    plot_name="Vdc",
)

# ## Release AEDT

tb.save_project()
tb.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
