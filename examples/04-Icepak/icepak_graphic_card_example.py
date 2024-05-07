# # Icepak: graphic card thermal analysis

# This example shows how you can use pyAEDT to create a graphic card setup in
# Icepak and post-process results.
# The example file is an Icepak project with a model that is already created and
# has materials assigned.
# Keywords: boundary conditions, postprocessing, monitors

# ## Perform required imports
#
# Perform required imports.

# +
import os
import tempfile

from IPython.display import Image
from ansys.pyaedt.examples.constants import AEDT_VERSION
import pandas as pd
import pyaedt

# -

# ## Set non-graphical mode
#


# ## Open project
#
# ### Download model
# Download the project to a temporary folder.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
project_temp_name = pyaedt.downloads.download_icepak(destination=temp_folder.name)

# Open the project in without the GUI.

ipk = pyaedt.Icepak(
    projectname=project_temp_name,
    specified_version=AEDT_VERSION,
    new_desktop_session=True,
    non_graphical=True,
)

# ## Plot model and rotate
#
# Plot the model using the pyAEDT-pyVista integration and save the result to a file.
# Rotate the model and plot again the rotated model.

# +
plot1 = ipk.plot(
    show=False,
    export_path=os.path.join(temp_folder.name, "Graphics_card_1.jpg"),
    plot_air_objects=False,
)

ipk.modeler.rotate(ipk.modeler.object_names, "X")

plot2 = ipk.plot(
    show=False,
    export_path=os.path.join(temp_folder.name, "Graphics_card_2.jpg"),
    plot_air_objects=False,
)
# -

# ## Boundary conditions
#
# Create source blocks on the CPU and memories.

ipk.create_source_block(object_name="CPU", input_power="25W")
ipk.create_source_block(object_name=["MEMORY1", "MEMORY1_1"], input_power="5W")

# The air region object handler is used to specify the inlet (fixed velocity condition) and outlet
# (fixed pressure condition) at x_max and x_min.

region = ipk.modeler["Region"]
ipk.assign_pressure_free_opening(assignment=region.top_face_x.id, boundary_name="Outlet")
ipk.assign_velocity_free_opening(
    assignment=region.bottom_face_x.id,
    boundary_name="Inlet",
    velocity=["1m_per_sec", "0m_per_sec", "0m_per_sec"],
)

# ## Mesh Settings
#
# ### Mesh Region
# Assign a mesh region around the heat sink and CPU.

mesh_region = ipk.mesh.assign_mesh_region(assignment=["HEAT_SINK", "CPU"])

# Print the available settings for the mesh region

mesh_region.settings

# Set the mesh region settings to manual and see new available settings

mesh_region.manual_settings = True
mesh_region.settings

# Modify settings and update

mesh_region.settings["MaxElementSizeX"] = "2mm"
mesh_region.settings["MaxElementSizeY"] = "2mm"
mesh_region.settings["MaxElementSizeZ"] = "2mm"
mesh_region.settings["EnableMLM"] = True
mesh_region.settings["MaxLevels"] = "2"
mesh_region.settings["MinElementsInGap"] = 4
mesh_region.update()

# Modify the slack of the subregion around the objects

subregion = mesh_region.assignment
subregion.positive_x_padding = "20mm"
subregion.positive_y_padding = "5mm"
subregion.positive_z_padding = "5mm"
subregion.negative_x_padding = "5mm"
subregion.negative_y_padding = "5mm"
subregion.negative_z_padding = "10mm"

# ### Global Mesh
# Set global mesh resolution (using automatic settings) to 4.

ipk.mesh.global_mesh_region.settings["MeshRegionResolution"]=4
ipk.mesh.global_mesh_region.update()


# ## Point monitors
#
# Assign a temperature face monitor to the CPU face in contact with the heatsink.

cpu = ipk.modeler["CPU"]
m1 = ipk.monitor.assign_face_monitor(
    face_id=cpu.top_face_z.id, monitor_quantity="Temperature", monitor_name="TemperatureMonitor1"
)

# Assign multiple speed point monitors downstream of the assembly.

speed_monitors = []
for x_pos in range(0, 82, 2):
    m = ipk.monitor.assign_point_monitor(
        point_position=[f"{x_pos}mm", "40mm", "15mm"], monitor_quantity="Speed"
    )
    speed_monitors.append(m)

# ## Solve project
#
# Create a setup, modify solver settings and run the simulation

setup1 = ipk.create_setup()
setup1.props["Flow Regime"] = "Turbulent"
setup1.props["Convergence Criteria - Max Iterations"] = 5
setup1.props["Linear Solver Type - Pressure"] = "flex"
setup1.props["Linear Solver Type - Temperature"] = "flex"
ipk.save_project()
ipk.analyze()

# ## PostProcess
#
# ### Quantitative post-processing

# Get the point monitor data. A dictionary is returned with 'Min', 'Max' and 'Mean' keys.

temperature_data = ipk.post.evaluate_monitor_quantity(monitor=m1, quantity="Temperature")
temperature_data

# It is also possible to get the data as pandas dataframe for advanced post-processing.

speed_fs = ipk.post.create_field_summary()
for m_name in speed_monitors:
    speed_fs.add_calculation(
        entity="Monitor", geometry="Volume", geometry_name=m_name, quantity="Speed"
    )
speed_data = speed_fs.get_field_summary_data(pandas_output=True)

# All the data is now in a dataframe, easy to visualize and to manipulate.

speed_data.head()

# The ``speed_data`` dataframe contains data from monitors, so it can be expanded with information
# of their position.

for i in range(3):
    direction = ["X", "Y", "Z"][i]
    speed_data["Position" + direction] = [
        ipk.monitor.all_monitors[entity].location[i] for entity in speed_data["Entity"]
    ]

# Plot the velocity profile at different X positions

speed_data.plot(
    x="PositionX",
    y="Mean",
    kind="line",
    marker="o",
    ylabel=speed_data.at[0, "Quantity"],
    xlabel=f"x [{ipk.modeler.model_units}]",
    grid=True,
)

# Extract temperature data at those same locations (so the ``speed_monitors`` list is used).

temperature_fs = ipk.post.create_field_summary()
for m_name in speed_monitors:
    temperature_fs.add_calculation(
        entity="Monitor", geometry="Volume", geometry_name=m_name, quantity="Temperature"
    )
temperature_fs = temperature_fs.get_field_summary_data(pandas_output=True)
temperature_fs.head()

# The two DataFrames can be merged using the `pd.merge()` function. With the merge, suffixes are
# added to the column names to differentiate between the columns from each original DataFrame.

merged_df = pd.merge(temperature_fs, speed_data, on="Entity", suffixes=("_temperature", "_speed"))
merged_df.head()

# The column names are renamed based on the 'Quantity' column of the original DataFrames.
# Finally, only the 'Entity', mean temperature, and mean speed columns are selected and
# assigned to the merged DataFrame.

temperature_quantity = temperature_fs["Quantity"].iloc[0]
velocity_quantity = speed_data["Quantity"].iloc[0]
merged_df.rename(
    columns={"Mean_temperature": temperature_quantity, "Mean_speed": velocity_quantity},
    inplace=True,
)
merged_df = merged_df[
    ["Entity", temperature_quantity, velocity_quantity, "PositionX", "PositionY", "PositionZ"]
]
merged_df.head()

# Compute the correlation coefficient between velocity and temperature from the merged DataFrame
# and plot a scatter plot to visualize their relationship.

correlation = merged_df[velocity_quantity].corr(merged_df[temperature_quantity])
ax = merged_df.plot.scatter(x=velocity_quantity, y=temperature_quantity)
ax.set_xlabel(velocity_quantity)
ax.set_ylabel(temperature_quantity)
ax.set_title(f"Correlation between Temperature and Velocity: {correlation:.2f}")

# The further away from the assembly, the faster and colder the air due to mixing.
# Despite being extremely simple, this example should demonstrate the potential of importing field
# summary data into pandas.

# ### Qualitative Post-Processing
# Create a temperature plot on main components and export it to a png file.

surflist = [i.id for i in ipk.modeler["CPU"].faces]
surflist += [i.id for i in ipk.modeler["MEMORY1"].faces]
surflist += [i.id for i in ipk.modeler["MEMORY1_1"].faces]
plot3 = ipk.post.create_fieldplot_surface(assignment=surflist, quantity="SurfTemperature")
path = plot3.export_image(
    full_path=os.path.join(temp_folder.name, "temperature.png"), orientation="top", show_region=False
)
Image(filename=path)  # Display the image

# pyVista can be used too.

plot4=ipk.post.plot_field(
    quantity="Temperature",
    assignment=[
        "SERIAL_PORT",
        "MEMORY1",
        "MEMORY1_1",
        "CAPACITOR",
        "CAPACITOR_1",
        "KB",
        "HEAT_SINK",
        "CPU",
        "ALPHA_MAIN_PCB",
    ],
    plot_cad_objs=False,
    show=False,
    export_path=temp_folder.name
)

# ## Release AEDT

ipk.release_desktop(True, True)
temp_folder.cleanup()
