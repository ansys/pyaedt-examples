# # Thermal analysis with 3D components

# This example shows how to create a thermal analysis of an electronic package by
# taking advantage of 3D components with advanced features added by PyAEDT.
#
# Keywords: **Icepak**, **3D components**, **mesh regions**, **monitor objects**.

# ## Perform imports and define constants
#
# Perform required imports.

import os
import tempfile
import time

from ansys.aedt.core import Icepak
from ansys.aedt.core.examples.downloads import download_icepak_3d_component

# Define constants.

AEDT_VERSION = "2025.1"
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory and download files
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
package_temp_name, qfp_temp_name = download_icepak_3d_component(
    local_path=temp_folder.name
)

# ## Create heatsink
# Create an empty project in non-graphical mode.

ipk = Icepak(
    project=os.path.join(temp_folder.name, "Heatsink.aedt"),
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    close_on_exit=True,
    new_desktop=True,
)

# Remove the air region, which is present by default. An air region is not needed as the heatsink
# is to be exported as a 3D component.

ipk.modeler["Region"].delete()

# Define the heatsink using multiple boxes.

hs_base = ipk.modeler.create_box(
    origin=[0, 0, 0], sizes=[37.5, 37.5, 2], name="HS_Base"
)
hs_base.material_name = "Al-Extruded"
hs_fin = ipk.modeler.create_box(origin=[0, 0, 2], sizes=[37.5, 1, 18], name="HS_Fin1")
hs_fin.material_name = "Al-Extruded"
n_fins = 11
hs_fins = hs_fin.duplicate_along_line(vector=[0, 3.65, 0], clones=n_fins)

ipk.plot(show=False, output_file=os.path.join(temp_folder.name, "Heatsink.jpg"))

# Define a mesh region around the heatsink.

mesh_region = ipk.mesh.assign_mesh_region(
    assignment=[hs_base.name, hs_fin.name] + hs_fins
)
mesh_region.manual_settings = True
mesh_region.settings["MaxElementSizeX"] = "5mm"
mesh_region.settings["MaxElementSizeY"] = "5mm"
mesh_region.settings["MaxElementSizeZ"] = "1mm"
mesh_region.settings["MinElementsInGap"] = 4
mesh_region.settings["MaxLevels"] = 2
mesh_region.settings["BufferLayers"] = 2
mesh_region.settings["EnableMLM"] = True
mesh_region.settings["UniformMeshParametersType"] = "Average"
mesh_region.update()

# Assign monitor objects.

hs_middle_fin = ipk.modeler.get_object_from_name(assignment=hs_fins[n_fins // 2])
point_monitor_position = [
    0.5 * (hs_base.bounding_box[i] + hs_base.bounding_box[i + 3]) for i in range(2)
] + [
    hs_middle_fin.bounding_box[-1]
]  # average x,y, top z
ipk.monitor.assign_point_monitor(
    point_position=point_monitor_position,
    monitor_quantity=["Temperature", "HeatFlux"],
    monitor_name="TopPoint",
)
ipk.monitor.assign_face_monitor(
    face_id=hs_base.bottom_face_z.id,
    monitor_quantity="Temperature",
    monitor_name="Bottom",
)
ipk.monitor.assign_point_monitor_in_object(
    name=hs_middle_fin.name,
    monitor_quantity="Temperature",
    monitor_name="MiddleFinCenter",
)

# Export the heatsink 3D component to a ``"componentLibrary"`` folder.
# The ``auxiliary_dict`` parameter is set to ``True`` to export the monitor objects
# along with the A3DCOMP file.

os.mkdir(os.path.join(temp_folder.name, "componentLibrary"))
ipk.modeler.create_3dcomponent(
    input_file=os.path.join(temp_folder.name, "componentLibrary", "Heatsink.a3dcomp"),
    name="Heatsink",
    export_auxiliary=True,
)
ipk.close_project(save=False)

# ## Create QFP
# Open the previously downloaded project containing a QPF.

ipk = Icepak(project=qfp_temp_name, version=AEDT_VERSION)
ipk.plot(show=False, output_file=os.path.join(temp_folder.name, "QFP2.jpg"))

# Create a dataset for power dissipation.

x_datalist = [45, 53, 60, 70]
y_datalist = [0.5, 3, 6, 9]
ipk.create_dataset(
    name="PowerDissipationDataset",
    x=x_datalist,
    y=y_datalist,
    is_project_dataset=False,
    x_unit="cel",
    y_unit="W",
)

# Assign a source power condition to the die.

ipk.create_source_power(
    face_id="DieSource",
    thermal_dependent_dataset="PowerDissipationDataset",
    source_name="DieSource",
)

# Assign thickness to the die attach surface.

ipk.assign_conducting_plate_with_thickness(
    obj_plate="Die_Attach",
    shell_conduction=True,
    thickness="0.05mm",
    solid_material="Epoxy Resin-Typical",
    boundary_name="Die_Attach",
)

# Assign monitor objects.

ipk.monitor.assign_point_monitor_in_object(
    name="QFP2_die", monitor_quantity="Temperature", monitor_name="DieCenter"
)
ipk.monitor.assign_surface_monitor(
    surface_name="Die_Attach", monitor_quantity="Temperature", monitor_name="DieAttach"
)

# Export the QFP 3D component in the ``"componentLibrary"`` folder and close the project.
# Here the auxiliary dictionary allows exporting not only the monitor objects but also the dataset
# used for the power source assignment.

ipk.modeler.create_3dcomponent(
    input_file=os.path.join(temp_folder.name, "componentLibrary", "QFP.a3dcomp"),
    name="QFP",
    export_auxiliary=True,
    datasets=["PowerDissipationDataset"],
)
ipk.release_desktop(close_projects=False, close_desktop=False)

# ## Create complete electronic package
# Download and open a project containing the electronic package.

ipk = Icepak(
    project=package_temp_name,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
)
ipk.plot(
    assignment=[o for o in ipk.modeler.object_names if not o.startswith("DomainBox")],
    show=False,
    output_file=os.path.join(temp_folder.name, "electronic_package_missing_obj.jpg"),
)

# The heatsink and the QFP are missing. They can be inserted as 3D components.
# The auxiliary files are needed because the goal is to also import monitor objects and datasets.

# Create a coordinate system for the heatsink so that it is placed on top of the AGP.

# +
agp = ipk.modeler.get_object_from_name(assignment="AGP_IDF")
cs = ipk.modeler.create_coordinate_system(
    origin=[agp.bounding_box[0], agp.bounding_box[1], agp.bounding_box[-1]],
    name="HeatsinkCS",
    reference_cs="Global",
    x_pointing=[1, 0, 0],
    y_pointing=[0, 1, 0],
)
heatsink_obj = ipk.modeler.insert_3d_component(
    input_file=os.path.join(temp_folder.name, "componentLibrary", "Heatsink.a3dcomp"),
    coordinate_system="HeatsinkCS",
    auxiliary_parameters=True,
)

QFP2_obj = ipk.modeler.insert_3d_component(
    input_file=os.path.join(temp_folder.name, "componentLibrary", "QFP.a3dcomp"),
    coordinate_system="Global",
    auxiliary_parameters=True,
)

ipk.plot(
    assignment=[o for o in ipk.modeler.object_names if not o.startswith("DomainBox")],
    show=False,
    plot_air_objects=False,
    output_file=os.path.join(temp_folder.name, "electronic_package.jpg"),
    force_opacity_value=0.5,
)
# -

# Create a coordinate system at the xmin, ymin, and zmin of the model.

bounding_box = ipk.modeler.get_model_bounding_box()
cs_pcb_assembly = ipk.modeler.create_coordinate_system(
    origin=[bounding_box[0], bounding_box[1], bounding_box[2]],
    name="PCB_Assembly",
    reference_cs="Global",
    x_pointing=[1, 0, 0],
    y_pointing=[0, 1, 0],
)

# Export the entire assembly as a 3D component and close the project. First, the nested
# hierarchy must be flattened because nested 3D components are currently not supported. Subsequently,
# the whole package can be exported as a 3D component. The auxiliary dictionary is needed
# to export monitor objects, datasets, and native components.

ipk.flatten_3d_components()

# ## Release AEDT

ipk.save_project()
ipk.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
