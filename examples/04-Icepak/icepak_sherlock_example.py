# # Icepak: setup from Sherlock inputs

# This example shows how you can create an Icepak project from Sherlock
# files (STEP and CSV) and an AEDB board.

# ## Perform required imports
#
# Perform required imports and set paths.

import os
import tempfile

from IPython.display import Image
import pyaedt

# Set paths

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
input_dir = pyaedt.downloads.download_sherlock(destination=temp_folder.name)

# ## Set non-graphical mode
#
# Set non-graphical mode.
# You can set ``non_graphical`` value either to ``True`` or ``False``.

non_graphical = False

# ## Define input files and variables.

material_name = "MaterialExport.csv"
component_properties = "TutorialBoardPartsList.csv"
component_step = "TutorialBoard.stp"
aedt_odb_project = "SherlockTutorial.aedt"
aedt_odb_design_name = "PCB"
outline_polygon_name = "poly_14188"

material_list = os.path.join(input_dir, material_name)
component_list = os.path.join(input_dir, component_properties)
validation = os.path.join(temp_folder.name, "validation.log")
file_path = os.path.join(input_dir, component_step)
project_name = os.path.join(temp_folder.name, component_step[:-3] + "aedt")

# ## Create Icepak project

ipk = pyaedt.Icepak(projectname=project_name)

# Delete the region and disable autosave to speed up the import.

ipk.autosave_disable()
ipk.modeler["Region"].delete()

# ## Import PCB from AEDB file
#
# Import a PCB from an AEDB file.
odb_path = os.path.join(input_dir, aedt_odb_project)
ipk.create_pcb_from_3dlayout(
    component_name="Board", project_name=odb_path, design_name=aedt_odb_design_name
)

# ## Create offset coordinate system
#
# Create an offset coordinate system to match ODB++ with the
# Sherlock STEP file.

bb = ipk.modeler.user_defined_components["Board1"].bounding_box
stackup_thickness = bb[-1] - bb[2]
ipk.modeler.create_coordinate_system(origin=[0, 0, stackup_thickness / 2], mode="view", view="XY")

# ## Import CAD file
#
# Import a CAD file.

ipk.modeler.import_3d_cad(file_path, refresh_all_ids=False)

# ## Save CAD file
#
# Save the CAD file and refresh the properties from the parsing of the AEDT file.

ipk.save_project(refresh_obj_ids_after_save=True)

# ## Plot model
#
# Plot the model.

ipk.plot(
    show=False,
    export_path=os.path.join(temp_folder.name, "Sherlock_Example.jpg"),
    plot_air_objects=False,
)

# ## Delete PCB objects
#
# Delete the PCB objects.

ipk.modeler.delete_objects_containing("pcb", False)

# ## Create region
#
# Create an air region.

x_pos, y_pos, z_pos, x_neg, y_neg, z_neg = [20, 20, 300, 20, 20, 300]
ipk.modeler.create_air_region(
    x_pos=x_pos, y_pos=y_pos, z_pos=z_pos, x_neg=x_neg, y_neg=y_neg, z_neg=z_neg
)

# ## Assign materials
#
# Use Sherlock file to assign materials.

ipk.assignmaterial_from_sherlock_files(csv_component=component_list, csv_material=material_list)

# ## Delete objects with no material assignments
#
# Delete objects with no materials assignments.

no_material_objs = ipk.modeler.get_objects_by_material(material="")
ipk.modeler.delete(assignment=no_material_objs)
ipk.save_project()

# ## Assign power to component blocks
#
# Assign power blocks from the Sherlock file.

total_power = ipk.assign_block_from_sherlock_file(csv_name=component_list)

# ## Plot model
#
# Plot the model again now that materials are assigned.

ipk.plot(
    show=False,
    export_path=os.path.join(temp_folder.name, "Sherlock_Example.jpg"),
    plot_air_objects=False,
)

# ## Set global mesh settings
ipk.mesh.global_mesh_region.manual_settings = True
ipk.mesh.global_mesh_region.settings["EnableMLM"] = True
ipk.mesh.global_mesh_region.settings["EnforeMLMType"] = "2D"
ipk.mesh.global_mesh_region.settings["2DMLMType"] = "2DMLM_Auto"
ipk.mesh.global_mesh_region.settings["NoOGrids"] = True
ipk.mesh.global_mesh_region.update()

# ## Set Boundary Conditions
# Assign free opening at all the region faces
ipk.assign_pressure_free_opening(assignment=ipk.modeler.get_object_faces("Region"))

# ## Solve setup
# Max iterations is set to 20 for quick demonstration, please increase to at
# least 100 for better accuracy.
setup1 = ipk.create_setup()
setup1.props["Solution Initialization - Y Velocity"] = "1m_per_sec"
setup1.props["Radiation Model"] = "Discrete Ordinates Model"
setup1.props["Include Gravity"] = True
setup1.props["Secondary Gradient"] = True
setup1.props["Convergence Criteria - Max Iterations"] = 10

# ## Create Post-processing objects
# Create point monitor

point1 = ipk.monitor.assign_point_monitor(
    point_position=ipk.modeler["COMP_U10"].top_face_z.center, monitor_name="Point1"
)

# Create line for report

line = ipk.modeler.create_polyline(
    points=[
        ipk.modeler["COMP_U10"].top_face_z.vertices[0].position,
        ipk.modeler["COMP_U10"].top_face_z.vertices[2].position,
    ],
    non_model=True,
)
ipk.post.create_report(expressions="Point1.Temperature", primary_sweep_variable="X")

# ## Check for intersections
#
# Check for intersections using validation and fix them by
# assigning priorities.

ipk.assign_priority_on_intersections()

# ## Analyze the model
#

ipk.analyze(num_cores=4, num_tasks=4)
ipk.save_project()

# ## Get solution data and plots
# The plot can be performed within AEDT...

plot1 = ipk.post.create_fieldplot_surface(
    assignment=ipk.modeler["COMP_U10"].faces, quantity="SurfTemperature"
)
path = plot1.export_image(full_path=os.path.join(temp_folder.name, "temperature.png"))
Image(filename=path)  # Display the image

# ... or using pyvista integration

ipk.post.plot_field(
    quantity="SurfPressure",
    assignment=ipk.modeler["COMP_U10"].faces,
    export_path=ipk.working_directory,
    show=False,
)

# ## Save project and release AEDT

# +
ipk.save_project()
ipk.release_desktop()

temp_folder.cleanup()
# -
