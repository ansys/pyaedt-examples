# # Icepak: Creating blocks and assigning materials and power

# This example shows how to create different types of blocks and assign power
# and material to them using
# a *.csv input file

# ## Perform required imports
#
# Perform required imports including the operating system, regular expression, csv, Ansys PyAEDT
# and its boundary objects.

import csv
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

ipk = pyaedt.Icepak(
    projectname=os.path.join(temp_folder, "Icepak_CSV_Import.aedt"),
    specified_version=AEDT_VERSION,
    new_desktop_session=True,
    non_graphical=non_graphical,
)
# -

# Create the PCB as a simple block.

board = ipk.modeler.create_box(
    origin=[-30.48, -27.305, 0], sizes=[146.685, 71.755, 0.4064], name="board_outline", material="FR-4_Ref"
)

# ## Blocks creation with a CSV file
#
# The CSV file lists the name of blocks, their type and material properties.
# Block types (solid, network, hollow), block name, block starting and end points,
# solid material, and power are listed.
# Hollow and network blocks do not need the material name.
# Network blocks must have Rjb and Rjc values.
# Monitor points can be created for any types of block if the last column is assigned
# to be 1 (0 and 1 are the only options).
#
# The following table does not show the entire rows and data and only serves as a sample.
#
#+------------+------+--------+---------+--------+-------+-------+--------+------------------+-------+-----+-----+---------------+
#| block_type | name | xs     | ys      | zs     | xd    | yd    | zd     | matname          | power | Rjb | Rjc | Monitor_point |
#+============+======+========+=========+========+=======+=======+========+==================+=======+=====+=====+===============+
#| hollow     | R8   | 31.75  | -20.32  | 0.4064 | 15.24 | 2.54  | 2.54   |                  | 1     |     |     | 0             |
#| solid      | U1   | 16.551 | 10.2035 | 0.4064 | 10.16 | 20.32 | 5.08   | Ceramic_material | 0.2   |     |     | 1             |
#| solid      | U2   | -16.51 | 10.16   | 0.4064 | 10.16 | 27.94 | 5.08   | Ceramic_material | 0.1   |     |     | 1             |
#| network    | C180 | 47.625 | 19.05   | 0.4064 | 3.81  | 2.54  | 2.4384 |                  | 1.13  | 2   | 3   | 0             |
#| network    | C10  | 65.405 | -1.27   | 0.4064 | 3.81  | 2.54  | 2.4384 |                  | 0.562 | 2   | 3   | 0             |
#| network    | C20  | 113.03 | -0.635  | 0.4064 | 2.54  | 3.81  | 2.4384 |                  | 0.445 | 2   | 3   | 0             |
#+------------+------+--------+---------+--------+-------+-------+--------+------------------+-------+-----+-----+---------------+
#
#
#
#
# In this step the code will loop over the csv file lines and creates the blocks.
# It will create solid blocks and assign BCs.
# Every row of the csv has information of a particular block.

# +
filename = pyaedt.downloads.download_file("icepak", "blocks-list.csv", destination=temp_folder)

with open(filename, "r") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        origin = [float(row["xs"]), float(row["ys"]), float(row["zs"])]  # block starting point
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

        # creates the block with the given name, coordinates, material, and type
        block = ipk.modeler.create_box(origin=origin, sizes=dimensions, name=block_name, material=material_name)

        # Assign boundary conditions
        if row["block_type"] == "solid":
            ipk.assign_solid_block(object_name=block_name, power_assignment=row["power"] + "W", boundary_name=block_name)
        elif row["block_type"] == "network":
            ipk.create_two_resistor_network_block(
                object_name=block_name, pcb=board.name, power=row["power"] + "W", rjb=row["Rjb"], rjc=row["Rjc"]
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
        # column of the csv file
        if row["Monitor_point"] == "1":
            ipk.monitor.assign_point_monitor_in_object(
                name=row["name"], monitor_quantity="Temperature", monitor_name=row["name"]
            )

# ## Release AEDT
#
# Release AEDT.

ipk.release_desktop(True, True)
