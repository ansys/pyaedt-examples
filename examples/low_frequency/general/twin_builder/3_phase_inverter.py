# # Q3D Dynamic link to Twin Builder for the DC-Link bus bars of a drive inverter
#
# This example demonstrates how to link an existing Q3D Extractor Design of the inverter DC-Link bus bars
# with a frequency sweep to a Twin Builder design using Q3D Dynamic Component - State Space link.
# This will integrate the broadband parasitic model of the bus bars into the Twin Builder schematic.
#
# Keywords: **DCLink**, **Twinbuilder**, **Q3D**.

# ## Perform imports and define constants
#
# Perform required imports.

import tempfile
import time
from pathlib import Path

import ansys.aedt.core
import pandas as pd
from ansys.aedt.core import get_pyaedt_app
from ansys.aedt.core.examples.downloads import download_file

# ## Define constants
#
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.
TB_DESIGN_NAME = "3ph_circuit"
Q3D_DESIGN_NAME = "q3d_3ph"

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
    design=TB_DESIGN_NAME,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Add Q3D component to Twinbuilder schematic
#
# Add a Q3D dynamic link to the Twinbuilder schematic.

comp = tb.add_q3d_dynamic_component(
    source_project=tb.project_name, source_design_name=Q3D_DESIGN_NAME, setup="Setup1", sweep_name="Sweep1", coupling_matrix_name="Original", state_space_dynamic_link_type="RLGC"
)

tb.set_active_design(TB_DESIGN_NAME)

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

# ## Twinbuilder Post-processing : Time domain
#
# Create reports for capacitor currents, load currents, DC current and voltage.

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

# ## Twinbuilder Post-processing : Frequency domain
#
# Create spectral reports for all sources in the whole spectral domain.

q3d = get_pyaedt_app(tb.project_name, Q3D_DESIGN_NAME)
sources = [source.name for source in q3d.boundaries_by_type["Source"]]
tb = get_pyaedt_app(tb.project_name, TB_DESIGN_NAME)

expressions = []
for source in sources:
    expressions.append(f"re({source}.I)")
    expressions.append(f"im({source}.I)")

# Create the spectral report for real and imaginary parts of source currents

new_report = tb.post.reports_by_category.spectral(expressions, "TR")
new_report.algorithm = "FFT"
new_report.window = "Rectangular"
new_report.max_frequency = "100kHz"
new_report.time_start = "20ms"
new_report.time_stop = "30ms"
new_report.variations = {"Spectrum": "All"}
new_report.create("Q3D_sources")

# Export report in a CSV file

report_path = tb.post.export_report_to_csv(temp_folder.name, "Q3D_sources")

# ## Filter data
#
#

q3d_sources_unfiltered = pd.read_csv(report_path, sep=",")
threshold = 0.01

# Identify rows below threshold
# If at least one between real and imaginary are below threshold, mark for deletion the entire row

for source in sources:
    mask = (q3d_sources_unfiltered[f"re({source}.I) [A]"].abs() < threshold) | (q3d_sources_unfiltered[f"im({source}.I) [A]"].abs() < threshold)

# Drop those rows

q3d_sources_filtered = q3d_sources_unfiltered[~mask]

# Save filtered data back to a new CSV file

q3d_sources_filtered_path = Path(tb.working_directory) / "Q3D_sources_filtered.csv"
q3d_sources_filtered.to_csv(q3d_sources_filtered_path, sep=",", index=False)

# Save real and imaginary part in separate tab-separated files
# Each .tab file will contain two columns: frequency and the corresponding part (real or imaginary)
# After exporting, import each .tab file as a dataset 1D in Q3D

freq_column = q3d_sources_filtered.columns[0]

for col in q3d_sources_filtered.columns[1:]:
    # Save the DataFrame as a tab-separated file
    new_file_name = Path(tb.working_directory) / f"{col}.tab"
    q3d_sources_filtered[[freq_column, col]].to_csv(new_file_name, sep="\t", index=False)

    # Determine dataset name and import it
    if col.split("(")[0] == "re":
        dataset_name = f"re_{col.split('(')[1].split('.')[0]}"
    elif col.split("(")[0] == "im":
        dataset_name = f"im_{col.split('(')[1].split('.')[0]}"
    q3d.import_dataset1d(str(new_file_name), name=dataset_name, is_project_dataset=False)

# ## Q3D: Harmonic loss setup
#
# Specify real and imaginary currents for each source to compute harmonic loss.

harmonic_loss = {}
for source in sources:
    re_dataset_name = next(d for d in list(q3d.design_datasets.keys()) if source in d and "re" in d.lower())
    im_dataset_name = next(d for d in list(q3d.design_datasets.keys()) if source in d and "im" in d.lower())
    harmonic_loss[source] = (re_dataset_name, im_dataset_name)
q3d.edit_sources(harmonic_loss=harmonic_loss)

# ## Q3D Post-processing
#
# Plot the harmonic loss density on the surface of the objects

plot = q3d.post.create_fieldplot_surface(["dc_terminal", "dc_terminal_1_2"], "Harmonic_Loss_Density", intrinsics={"Freq": "0.5GHz", "Phase": "0deg"})
plot.change_plot_scale(minimum_value="0", maximum_value="1040000", is_log=True)

# ## Create Icepak Target Design
#
# Create an EM Target Design to link the results to Icepak to run a thermal simulation

q3d.create_em_target_design("Icepak", design_setup="Natural")
ipk = get_pyaedt_app(tb.project_name, "IcepakDesign1")

# ## Icepak setup
#
# Set "TemperatureOnly" as problem type in the Icepak setup

setup = ipk.setups[0]
setup.properties["Problem Type"] = "TemperatureOnly"

# ## Create a subregion
#
# Create subregion to enclose the objects imported from Q3D

subregion = ipk.modeler.create_subregion(padding_values=[10, 10, 10, 10, 50, 50], padding_types="Percentage Offset", assignment=["dc_terminal", "dc_terminal_1_2"], name="Subregion")

# ## Icepak boundaries
#
# When creating an Icepak target design the setup problem type is set by default to both "Temperature" and "Flow".
# When "Flow" is enabled by default, two "Opening" boundary conditions are set automatically at the extremities
# of the region.
# Since we change the problem type to "TemperatureOnly", we need to delete those boundary conditions.

[bound.delete() for bound in ipk.boundaries_by_type["Opening"]]

# Assign stationary wall boundary condition with temperature

ipk.assign_stationary_wall_with_temperature(
    ["module_a_minus", "module_a_plus", "module_b_minus", "module_b_plus", "module_c_minus", "module_c_plus"],
    name="StationaryWall",
    temperature=80,
    thickness="10mm",
    material="Al-Extruded",
    radiate=False,
    radiate_surf_mat="Steel-oxidised-surface",
    shell_conduction=True,
)

# ## Mesh region
#
# Assign mesh region to the subregion

mesh_subregion = ipk.mesh.assign_mesh_region(assignment=[subregion.name], level=5, name="MeshSubregion")

# ## Analysis
#
# Analyze the Icepak design

ipk.analyze_setup(ipk.setups[0].name)

# ## Icepak Post-processing
#
# Post-processing: plot temperature distribution and volumetric heat loss on the surface of the objects

temp = ipk.post.create_fieldplot_surface(assignment=["dc_terminal", "dc_terminal_1_2"], quantity="Temperature", plot_name="Temperature")
vol_heat_loss = ipk.post.create_fieldplot_volume(assignment=["dc_terminal", "dc_terminal_1_2"], quantity="VolumeHeatLoss", plot_name="VolumeHeatLoss")

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
