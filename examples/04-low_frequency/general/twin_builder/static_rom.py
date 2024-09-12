# # Static ROM
#
# This example shows how to create a static reduced order model (ROM)
# in Twin Builder and run a transient simulation.
#
# **Note:** This example uses functionality only available in Twin Builder 2024 R2 and later.
#
# Keywords: **Twin Builder**, **Static ROM**.

# ## Perform imports and define constants
#
# Perform required imports.

import os
import shutil
import tempfile
import time

from ansys.aedt.core import TwinBuilder, downloads

# Define constants.

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Set up input data
#
# The following files are downloaded along with the
# other project data used to run this example.

source_snapshot_data_zipfilename = "Ex1_Fluent_StaticRom.zip"
source_build_conf_file = "SROMbuild.conf"
source_props_conf_file = "SROM_props.conf"

# ## Download example data
#
# The following cell downloads the required files needed to run this example and
# extracts them in a local folder named ``"Ex04"``.

# +
_ = downloads.download_twin_builder_data(
    file_name=source_snapshot_data_zipfilename,
    force_download=True,
    destination=temp_folder.name,
)

_ = downloads.download_twin_builder_data(source_build_conf_file, True, temp_folder.name)
source_data_folder = downloads.download_twin_builder_data(
    source_props_conf_file, True, temp_folder.name
)

# Target folder to extract project files.
data_folder = os.path.join(source_data_folder, "Ex04")

# Unzip training data and config file
downloads.unzip(
    os.path.join(source_data_folder, source_snapshot_data_zipfilename), data_folder
)
shutil.copyfile(
    os.path.join(source_data_folder, source_build_conf_file),
    os.path.join(data_folder, source_build_conf_file),
)
shutil.copyfile(
    os.path.join(source_data_folder, source_props_conf_file),
    os.path.join(data_folder, source_props_conf_file),
)
# -

# ## Launch Twin Builder and build ROM component
#
# Launch Twin Builder using an implicit declaration and add a new design with
# the default setup for building the static ROM component.

project_name = os.path.join(temp_folder.name, "static_rom.aedt")
tb = TwinBuilder(
    project=project_name,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Configure AEDT
#
# **Note:** Only run the following cell if AEDT is not configured to run Twin Builder.
# 
# The following cell configures AEDT and the schematic editor
# to use the ``Twin Builder`` configuration.
# The Static ROM feature is only available with a Twin Builder license.
# A cell at the end of this example restores the AEDT configuration. If your
# environment is set up to use the ``Twin Builder`` configuration, you do not
# need to run these sections.

current_desktop_config = tb._odesktop.GetDesktopConfiguration()
current_schematic_environment = tb._odesktop.GetSchematicEnvironment()
tb._odesktop.SetDesktopConfiguration("Twin Builder")
tb._odesktop.SetSchematicEnvironment(1)

# +
# Get the static ROM builder object.
rom_manager = tb._odesign.GetROMManager()
static_rom_builder = rom_manager.GetStaticROMBuilder()

# Build the static ROM with the specified configuration file
confpath = os.path.join(data_folder, source_build_conf_file)
static_rom_builder.Build(confpath.replace("\\", "/"))

# Test if the ROM was created successfully.
static_rom_path = os.path.join(data_folder, "StaticRom.rom")
if os.path.exists(static_rom_path):
    tb.logger.info("Built intermediate rom file successfully at: %s", static_rom_path)
else:
    tb.logger.error("Intermediate rom file not found at: %s", static_rom_path)

# Create the ROM component definition in Twin Builder.
rom_manager.CreateROMComponent(static_rom_path.replace("\\", "/"), "staticrom")
# -

# ## Create schematic
#
# Place components to create the schematic.

# +
# Define the grid distance for ease in calculations.
G = 0.00254

# Place a dynamic ROM component.
rom1 = tb.modeler.schematic.create_component("ROM1", "", "staticrom", [40 * G, 25 * G])

# Place two excitation sources.
source1 = tb.modeler.schematic.create_periodic_waveform_source(
    None, "SINE", 2.5, 0.01, 0, 7.5, 0, [20 * G, 29 * G]
)
source2 = tb.modeler.schematic.create_periodic_waveform_source(
    None, "SINE", 50, 0.02, 0, 450, 0, [20 * G, 25 * G]
)
# -

# Connect components with wires.

tb.modeler.schematic.create_wire([[22 * G, 29 * G], [33 * G, 29 * G]])
tb.modeler.schematic.create_wire(
    [[22 * G, 25 * G], [30 * G, 25 * G], [30 * G, 28 * G], [33 * G, 28 * G]]
)

# Enable storage of views.

rom1.set_property("store_snapshots", 1)
rom1.set_property("view1_storage_period", "10s")
rom1.set_property("view2_storage_period", "10s")

# Zoom to fit the schematic
tb.modeler.zoom_to_fit()

# ## Parametrize transient setup
#
# Parametrize the default transient setup by setting the end time.

tb.set_end_time("300s")
tb.set_hmin("1s")
tb.set_hmax("1s")

# ## Solve transient setup
#
# Solve the transient setup. Skipping this step in case the documentation is being built.

# **Note:** The following code can be uncommented.
#
# tb.analyze_setup("TR")

# ## Get report data and plot using Matplotlib
#
# Get report data and plot it using Matplotlib. The following code gets and plots
# the values for the voltage on the pulse voltage source and the values for the
# output of the dynamic ROM.

# **Note:** The following code can be uncommented, but it depends on the previous commented code.
#
# e_value = "ROM1.outfield_mode_1"
# x = tb.post.get_solution_data(e_value, "TR", "Time")
# x.plot()
# e_value = "ROM1.outfield_mode_2"
# x = tb.post.get_solution_data(e_value, "TR", "Time")
# x.plot()
# e_value = "SINE1.VAL"
# x = tb.post.get_solution_data(e_value, "TR", "Time")
# x.plot()
# e_value = "SINE2.VAL"
# x = tb.post.get_solution_data(e_value, "TR", "Time")
# x.plot()


# ## Close Twin Builder
#
# After the simulation is completed, either close Twin Builder or release it.
# All methods provide for saving the project before closing.

# Clean up the downloaded data.
shutil.rmtree(source_data_folder)

# Restore earlier desktop configuration and schematic environment.
tb._odesktop.SetDesktopConfiguration(current_desktop_config)
tb._odesktop.SetSchematicEnvironment(current_schematic_environment)

# ## Release AEDT
#
# Release AEDT and close the example.

tb.save_project()
tb.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``. If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
