# # Icepak: graphic card thermal analysis

# This example shows how you can use PyAEDT to create a graphic card setup in
# Icepak and postprocess results.
# The example file is an Icepak project with a model that is already created and
# has materials assigned.
# Keywords: boundary conditions, 3D components

# ## Perform required imports
#
# Perform required imports.
# +
import os

from ansys.pyaedt.examples.constants import AEDT_VERSION
import pyaedt

# ## Set non-graphical mode
#
# Set non-graphical mode.
# You can set ``non_graphical`` either to ``True`` or ``False``.

non_graphical = False

# ## Download and open project
#
# Download the project, open it, and save it to the temporary folder.

# +
temp_folder = pyaedt.generate_unique_folder_name()
project_temp_name = pyaedt.downloads.download_icepak(temp_folder)

ipk = pyaedt.Icepak(
    projectname=project_temp_name,
    specified_version=AEDT_VERSION,
    new_desktop_session=True,
    non_graphical=non_graphical,
)

ipk.autosave_disable()
# -

# ## Plot model
#
# Plot the model.

ipk.plot(
    show=False, export_path=os.path.join(temp_folder, "Graphics_card.jpg"), plot_air_objects=False
)

# ## Create source blocks
#
# Create source blocks on the CPU and memories.

ipk.create_source_block(object_name="CPU", input_power="25W")
ipk.create_source_block(object_name=["MEMORY1", "MEMORY1_1"], input_power="5W")

# ## Assign openings and grille
#
# Assign openings and a grille.

region = ipk.modeler["Region"]
ipk.assign_pressure_free_opening(assignment=region.top_face_x.id, boundary_name="Outlet")
ipk.assign_velocity_free_opening(assignment=region.bottom_face_x.id, boundary_name="Inlet", velocity=["1m_per_sec", "0m_per_sec", "0m_per_sec"],)
ipk.assign_grille(air_faces=region.top_face_x.id, free_area_ratio=0.8)

# ## Assign mesh regions
#
# Assign a mesh region to the heat sink and CPU.

mesh_region = ipk.mesh.assign_mesh_region(objectlist=["HEAT_SINK", "CPU"])
mesh_region.manual_settings = True
mesh_region.settings["MaxElementSizeX"] = "3.35mm"
mesh_region.settings["MaxElementSizeY"] = "1.75mm"
mesh_region.settings["MaxElementSizeZ"] = "2.65mm"
mesh_region.settings["MaxLevels"] = "2"
mesh_region.update()

# ## Assign point monitor
#
# Assign a point monitor.

m1 = ipk.assign_point_monitor(
    point_position=["-35mm", "3.6mm", "-86mm"], monitor_name="TemperatureMonitor1"
)
speed_monitors = []
for x_pos in range(0, 80, 20):
    m = ipk.assign_point_monitor(point_position=[f"{x_pos}mm", "14.243mm", "-55mm"], monitor_type="Speed")
    speed_monitors.append(m)

# ## Solve project
# Create a setup, modify solver settings and run the simulation
setup1 = ipk.create_setup()
setup1.props["Flow Regime"] = "Turbulent"
setup1.props["Convergence Criteria - Max Iterations"] = 5
setup1.props["Linear Solver Type - Pressure"] = "flex"
setup1.props["Linear Solver Type - Temperature"] = "flex"
ipk.save_project()
ipk.analyze()

# ## PostProcess
# Create a temperature plot
surflist = [i.id for i in ipk.modeler["CPU"].faces]
surflist += [i.id for i in ipk.modeler["MEMORY1"].faces]
surflist += [i.id for i in ipk.modeler["MEMORY1_1"].faces]
surflist += [i.id for i in ipk.modeler["ALPHA_MAIN_PCB"].faces]
plot5 = ipk.post.create_fieldplot_surface(objlist=surflist, quantityName="SurfTemperature")
plot5.export_image(full_path=os.path.join(temp_folder, "temperature.png"))

# Get the point monitor data.
temperature_data = ipk.post.evaluate_monitor_quantity(monitor_name=m1, quantity_name="Temperature")
temperature_data

# It is also possible to get the data as pandas dataframe for advanced features.
speed_fs = ipk.post.create_field_summary()
for m_name in speed_monitors:
    speed_fs.add_calculation(
        entity="Monitor",
        geometry="Volume",
        geometry_name=m_name,
        quantity="Speed"
    )
speed_data = speed_fs.get_field_summary_data(pandas_output=True)
speed_data

speed_data["Mean"].astype(float).plot(marker="o", ylabel="Speed", xlabel="Position", grid=True)

# ## Release AEDT
#
# Release AEDT.

ipk.release_desktop(True, True)
