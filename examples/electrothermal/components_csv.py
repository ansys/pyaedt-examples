# # PCB component definition from CSV file and model image exports

# This example shows how to create different types of blocks and assign power
# and material to them using a CSV input file
#
# Keywords: **Icepak**, **boundaries**, **PyVista**, **CSV**, **PCB**, **components**.

# ## Perform imports and define constants

# +
import csv
import os
import tempfile
import time
from pathlib import Path

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_file
import matplotlib as mpl
import numpy as np
import pyvista as pv
from IPython.display import Image
from matplotlib import cm
from matplotlib import pyplot as plt
# -

# Define constants.

AEDT_VERSION = "2025.2"
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Download and open project
#
# Download the project and open it in non-graphical mode, using a temporary folder.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
project_name = os.path.join(temp_folder.name, "Icepak_CSV_Import.aedt")
ipk = ansys.aedt.core.Icepak(
    project=project_name,
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
)

# Create the PCB as a simple block with lumped material properties.

board = ipk.modeler.create_box(
    origin=[-30.48, -27.305, 0],
    sizes=[146.685, 71.755, 0.4064],
    name="board_outline",
    material="FR-4_Ref",
)

# ## Create components from CSV file
#
# Components are represented as simple cubes with dimensions and properties specified in a CSV file.

filename = download_file(
    "icepak", "blocks-list.csv", local_path=temp_folder.name
)

# The CSV file lists block properties:
#
# - Type (solid, network, hollow)
# - Name
# - Dtart point (xs, ys, zs) and end point (xd, yd, zd)
# - Material properties (for solid blocks)
# - Power assignment
# - Resistances to the board and to the case (for network blocks)
# - Whether to add a monitor point to the block (0 or 1)
#
# The following table does not show entire rows and dat. It provides only a sample.
#
#
# | block_type | name | xs     | ys     | zs   | xd    | yd    | zd   | matname          | power | Rjb | Rjc | Monitor_point |
# |------------|------|--------|--------|------|-------|-------|------|------------------|-------|-----|-----|---------------|
# | hollow     | R8   | 31.75  | -20.32 | 0.40 | 15.24 | 2.54  | 2.54 |                  | 1     |     |     | 0             |
# | solid      | U1   | 16.55  | 10.20  | 0.40 | 10.16 | 20.32 | 5.08 | Ceramic_material | 0.2   |     |     | 1             |
# | solid      | U2   | -51    | 10.16  | 0.40 | 10.16 | 27.94 | 5.08 | Ceramic_material | 0.1   |     |     | 1             |
# | network    | C180 | 47.62  | 19.05  | 0.40 | 3.81  | 2.54  | 2.43 |                  | 1.13  | 2   | 3   | 0             |
# | network    | C10  | 65.40  | -1.27  | 0.40 | 3.81  | 2.54  | 2.43 |                  | 0.562 | 2   | 3   | 0             |
# | network    | C20  | 113.03 | -0.63  | 0.40 | 2.54  | 3.81  | 2.43 |                  | 0.445 | 2   | 3   | 0             |
#
# The following code loops over each line of the CSV file, creating solid blocks
# and assigning boundary conditions.
#
# Every row of the CSV file has information on a particular block.

# +
with open(filename, "r") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        origin = [
            float(row["xs"]),
            float(row["ys"]),
            float(row["zs"]),
        ]  # block starting point
        dimensions = [
            float(row["xd"]),
            float(row["yd"]),
            float(row["zd"]),
        ]  # block lengths in 3 dimensions
        block_name = row["name"]  # block name

        # Define material name
        if row["matname"]:
            material_name = row["matname"]
        else:
            material_name = "copper"

        # Creates the block with the given name, coordinates, material, and type
        block = ipk.modeler.create_box(
            origin=origin, sizes=dimensions, name=block_name, material=material_name
        )

        # Assign boundary conditions
        if row["block_type"] == "solid":
            ipk.assign_solid_block(
                object_name=block_name,
                power_assignment=row["power"] + "W",
                boundary_name=block_name,
            )
        elif row["block_type"] == "network":
            ipk.create_two_resistor_network_block(
                object_name=block_name,
                pcb=board.name,
                power=row["power"] + "W",
                rjb=row["Rjb"],
                rjc=row["Rjc"],
            )
        else:
            ipk.modeler[block.name].solve_inside = False
            ipk.assign_hollow_block(
                object_name=block_name,
                assignment_type="Total Power",
                assignment_value=row["power"] + "W",
                boundary_name=block_name,
            )

        # Create temperature monitor points if assigned value is 1 in the last
        # column of the CSV file
        if row["Monitor_point"] == "1":
            ipk.monitor.assign_point_monitor_in_object(
                name=row["name"],
                monitor_quantity="Temperature",
                monitor_name=row["name"],
            )
# -


# ## Calculate the power assigned to all components

power_budget, total_power = ipk.post.power_budget(units="W")

# ## Plot model using AEDT
#
# Set the colormap to use. You can use the previously computed power budget to set the minimum and maximum values.

cmap = plt.get_cmap("plasma")
norm = mpl.colors.Normalize(
    vmin=min(power_budget.values()), vmax=max(power_budget.values())
)
scalarMap = cm.ScalarMappable(norm=norm, cmap=cmap)

# Color the objects depending
for obj in ipk.modeler.objects.values():
    if obj.name in power_budget:
        obj.color = [
            int(i * 255) for i in scalarMap.to_rgba(power_budget[obj.name])[0:3]
        ]
        obj.transparency = 0
    else:
        obj.color = [0, 0, 0]
        obj.transparency = 0.9

# Export the model image by creating a list of all objects that excludes ``Region``.
# This list is then passed to the `export_model_picture()` function.
# This approach ensures that the exported image is fitted to the PCB and its components.

obj_list_noregion = list(ipk.modeler.object_names)
obj_list_noregion.remove("Region")
export_file = os.path.join(temp_folder.name, "object_power_AEDTExport.jpg")
ipk.post.export_model_picture(
    export_file, selections=obj_list_noregion, width=1920, height=1080
)
Image(export_file)

# ### Plot model using PyAEDT
#
# Initialize a PyVista plotter
plotter = pv.Plotter(off_screen=True, window_size=[2048, 1536])

# Export all models objects to OBJ files.

f = ipk.post.export_model_obj(
    export_path=temp_folder.name, export_as_multiple_objects=True, air_objects=False
)

# Add objects to the PyVista plotter. These objects are either set to a black color or assigned scalar values,
# allowing them to be visualized with a colormap.

for file, color, opacity in f:
    if color == (0, 0, 0):
        plotter.add_mesh(mesh=pv.read(file), color="black", opacity=opacity)
    else:
        mesh = pv.read(filename=file)
        mesh["Power"] = np.full(
            shape=mesh.n_points, fill_value=power_budget[Path(file).stem]
        )
        plotter.add_mesh(mesh=mesh, scalars="Power", cmap="viridis", opacity=opacity)

# Add a label to the object with the maximum temperature.

max_pow_obj = "MP1"
plotter.add_point_labels(
    points=[ipk.modeler[max_pow_obj].top_face_z.center],
    labels=[f"{max_pow_obj}, {power_budget[max_pow_obj]}W"],
    point_size=20,
    font_size=30,
    text_color="red",
)

# Export the file.

export_file = os.path.join(temp_folder.name, "object_power_pyVista.png")
plotter.screenshot(filename=export_file, scale=1)
Image(export_file)

# ## Release AEDT

ipk.save_project()
ipk.release_desktop()
time.sleep(
    3
)  # Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
