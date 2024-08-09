# # Q3D Extractor: PCB analysis

# This example shows how you can use PyAEDT to create a design in
# Q3D Extractor and run a simulation starting from an EDB Project.

# ## Perform required imports
#
# Perform required imports.

import os
import tempfile
import pyaedt
import pyedb

# Set constant values

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory
#
# Create temporary directory.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Setup project files and path
#
# Download of needed project file and setup of temporary project directory.

# +
project_dir = os.path.join(temp_dir.name, "edb")
aedb_project = pyaedt.downloads.download_file(
    source="edb/ANSYS-HSD_V1.aedb", destination=project_dir
)

project_name = os.path.join(temp_dir.name, "HSD")
output_edb = os.path.join(project_dir, project_name + ".aedb")
output_q3d = os.path.join(project_dir, project_name + "_q3d.aedt")
# -

# ## Open EDB
#
# Open the edb project and created a cutout on the selected nets
# before exporting to Q3D.

edb = pyedb.Edb(aedb_project, edbversion=AEDT_VERSION)
cutout_points = edb.cutout(
                ["CLOCK_I2C_SCL", "CLOCK_I2C_SDA"],
                ["GND"],
                output_aedb_path=output_edb,
                use_pyaedt_extent_computing=True,
            )


# ## Identify the position of pins
#
# Identify $(x,y)$ pin locations on the components to define where to assign sources
# and sinks for Q3D and append Z elevation.

pin_u13_scl = [i for i in edb.components["U13"].pins.values() if i.net_name == "CLOCK_I2C_SCL"]
pin_u1_scl = [i for i in edb.components["U1"].pins.values() if i.net_name == "CLOCK_I2C_SCL"]
pin_u13_sda = [i for i in edb.components["U13"].pins.values() if i.net_name == "CLOCK_I2C_SDA"]
pin_u1_sda = [i for i in edb.components["U1"].pins.values() if i.net_name == "CLOCK_I2C_SDA"]

# ## Append Z Positions
#
# Note: The factor 1000 converts from "meters" to "mm"

# +
location_u13_scl = [i * 1000 for i in pin_u13_scl[0].position]
location_u13_scl.append(edb.components["U13"].upper_elevation * 1000)

location_u1_scl = [i * 1000 for i in pin_u1_scl[0].position]
location_u1_scl.append(edb.components["U1"].upper_elevation * 1000)

location_u13_sda = [i * 1000 for i in pin_u13_sda[0].position]
location_u13_sda.append(edb.components["U13"].upper_elevation * 1000)

location_u1_sda = [i * 1000 for i in pin_u1_sda[0].position]
location_u1_sda.append(edb.components["U1"].upper_elevation * 1000)
# -

# ## Save and close the EDB
#
# Save, close Edb and open it in Hfss 3D Layout to generate the 3D model.

# +
edb.save_edb()
edb.close_edb()

h3d = pyaedt.Hfss3dLayout(
    output_edb, version=AEDT_VERSION, non_graphical=NG_MODE, new_desktop=True
)
# -

# ## Set up the Q3D Project
#
# Use HFSS 3D Layout to export the model to Q3D Extractor. The named parameter
# ``keep_net_name=True`` ensures that net names are retained when the model is exported from Hfss 3D Layout.

setup = h3d.create_setup()
setup.export_to_q3d(output_q3d, keep_net_name=True)
h3d.close_project()

# Open the newly created Q3D project and display the layout.

q3d = pyaedt.Q3d(output_q3d)
q3d.plot(
    show=False,
    objects=["CLOCK_I2C_SCL", "CLOCK_I2C_SDA"],
    export_path=os.path.join(temp_dir.name, "Q3D.jpg"),
    plot_air_objects=False,
)

# Use previously calculated position to identify faces and
# assign sources and sinks on nets.

f1 = q3d.modeler.get_faceid_from_position(location_u13_scl, obj_name="CLOCK_I2C_SCL")
q3d.source(f1, net_name="CLOCK_I2C_SCL")
f1 = q3d.modeler.get_faceid_from_position(location_u13_sda, obj_name="CLOCK_I2C_SDA")
q3d.source(f1, net_name="CLOCK_I2C_SDA")
f1 = q3d.modeler.get_faceid_from_position(location_u1_scl, obj_name="CLOCK_I2C_SCL")
q3d.sink(f1, net_name="CLOCK_I2C_SCL")
f1 = q3d.modeler.get_faceid_from_position(location_u1_sda, obj_name="CLOCK_I2C_SDA")
q3d.sink(f1, net_name="CLOCK_I2C_SDA")

# Define the solution setup and the frequency sweep ranging from DC to 2GHz.

setup = q3d.create_setup()
setup.dc_enabled = True
setup.capacitance_enabled = False
sweep = setup.add_sweep()
sweep.add_subrange(
    "LinearStep", 0, end=2, count=0.05, unit="GHz", save_single_fields=False, clear=True
)
setup.analyze(num_cores=NUM_CORES)

# ### Solve
#
# Compute AC inductance and resistance.

traces_acl = q3d.post.available_report_quantities(quantities_category="ACL Matrix")
solution = q3d.post.get_solution_data(traces_acl)

# ## Post-Processing
#
# Plot AC inductance and resistance.

solution.plot()
traces_acr = q3d.post.available_report_quantities(quantities_category="ACR Matrix")
solution2 = q3d.post.get_solution_data(traces_acr)
solution2.plot()

# ## Close AEDT
#
# After the simulation completes, you can close AEDT or release it using the
# ``release_desktop`` method. All methods provide for saving projects before closing.

q3d.save_project()
q3d.release_desktop()

# ## Cleanup
#
# All project files are saved in the folder ``temp_dir.name``. If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_dir.cleanup()
