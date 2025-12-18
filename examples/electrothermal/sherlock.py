# # Setup from Sherlock inputs

# This example shows how to create an Icepak project from Sherlock
# files (STEP and CSV) and an AEDB board.
#
# Keywords: **Icepak**, **Sherlock**.

# ## Perform imports and define constants
#
# Perform required imports.

# +
import os
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_sherlock
# -

# Define constants

AEDT_VERSION = "2025.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Set paths and define input files and variables
#
# Set paths.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
input_dir = download_sherlock(local_path=temp_folder.name)

# Define input files.

material_name = "MaterialExport.csv"
component_properties = "TutorialBoardPartsList.csv"
component_step = "TutorialBoard.stp"
aedt_odb_project = "SherlockTutorial.aedt"

# Define variables that are needed later.

aedt_odb_design_name = "PCB"
outline_polygon_name = "poly_14188"

# Define input files with paths.

material_list = os.path.join(input_dir, material_name)
component_list = os.path.join(input_dir, component_properties)
validation = os.path.join(temp_folder.name, "validation.log")
file_path = os.path.join(input_dir, component_step)
project_name = os.path.join(temp_folder.name, component_step[:-3] + "aedt")

# ## Create Icepak model

ipk = ansys.aedt.core.Icepak(
    project=project_name, version=AEDT_VERSION, non_graphical=NG_MODE
)

# Disable autosave to speed up the import.

ipk.autosave_disable()

# Import a PCB from an AEDB file.

odb_path = os.path.join(input_dir, aedt_odb_project)
ipk.create_pcb_from_3dlayout(
    component_name="Board", project_name=odb_path, design_name=aedt_odb_design_name
)

# Create an offset coordinate system to match ODB++ with the Sherlock STEP file.
# The thickness is computed from the ``"Board"`` component. (``"Board1"`` is the
# instance name of the ``"Board"`` native component and is used to offset the coordinate system.)

bb = ipk.modeler.user_defined_components["Board1"].bounding_box
stackup_thickness = bb[-1] - bb[2]
ipk.modeler.create_coordinate_system(
    origin=[0, 0, stackup_thickness / 2], mode="view", view="XY"
)

# Import the board components from an MCAD file and remove the PCB object as it is already
# imported with the ECAD.

ipk.modeler.import_3d_cad(file_path, refresh_all_ids=False)
ipk.modeler.delete_objects_containing("pcb", False)

# Modify the air region. Padding values are passed in this order: [+X, -X, +Y, -Y, +Z, -Z]

ipk.mesh.global_mesh_region.global_region.padding_values = [20, 20, 20, 20, 300, 300]

# ## Assign materials and power dissipation conditions from Sherlock
#
# Use the Sherlock file to assign materials.

ipk.assignmaterial_from_sherlock_files(
    component_file=component_list, material_file=material_list
)

# Delete objects with no material assignments.

no_material_objs = ipk.modeler.get_objects_by_material(material="")
ipk.modeler.delete(assignment=no_material_objs)
ipk.save_project()

# Assign power blocks from the Sherlock file.

total_power = ipk.assign_block_from_sherlock_file(csv_name=component_list)

# ## Assign openings
#
# Assign opening boundary condition to all the faces of the region.
ipk.assign_openings(ipk.modeler.get_object_faces("Region"))

# ## Create simulation setup
# ### Set global mesh settings

ipk.globalMeshSettings(
    3,
    gap_min_elements="1",
    noOgrids=True,
    MLM_en=True,
    MLM_Type="2D",
    edge_min_elements="2",
    object="Region",
)


# ### Add postprocessing object
# Create the point monitor.

point1 = ipk.monitor.assign_point_monitor(
    point_position=ipk.modeler["COMP_U10"].top_face_z.center, monitor_name="Point1"
)

# Create a line for reporting after the simulation.

line = ipk.modeler.create_polyline(
    points=[
        ipk.modeler["COMP_U10"].top_face_z.vertices[0].position,
        ipk.modeler["COMP_U10"].top_face_z.vertices[2].position,
    ],
    non_model=True,
)

# ### Solve
# To solve quickly, the maximum iterations are set to 20. For better accuracy, you
# can increase the maximum to at least 100.

setup1 = ipk.create_setup()
setup1.props["Solution Initialization - Y Velocity"] = "1m_per_sec"
setup1.props["Radiation Model"] = "Discrete Ordinates Model"
setup1.props["Include Gravity"] = True
setup1.props["Secondary Gradient"] = True
setup1.props["Convergence Criteria - Max Iterations"] = 100

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
