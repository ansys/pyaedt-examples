# # Dynamic ROM
#
# This example shows how to use PyAEDT to create a dynamic reduced order model (ROM)
# in Twin Builder and run a Twin Builder time-domain simulation.
#
# > **Note:** This example uses functionality only available in Twin
# > Builder 2023 R2 and later.
#
# Keywords: **Twin Builder**, **Dynamic ROM**.

# ## Perform imports and define constants
#
# Perform required imports.

# +
import os
import shutil
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.examples import downloads
import matplotlib.pyplot as plt
# -

# Define constants.

AEDT_VERSION = "2025.1"
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
# Define the file name.

source_snapshot_data_zipfilename = "Ex1_Mechanical_DynamicRom.zip"
source_build_conf_file = "dynarom_build.conf"

# Download data from the ``example_data`` repository.

_ = downloads.download_twin_builder_data(
    file_name=source_snapshot_data_zipfilename,
    force_download=True,
    destination=temp_folder.name,
)
source_data_folder = downloads.download_twin_builder_data(
    source_build_conf_file, True, temp_folder.name
)

# Toggle these for local testing.

data_folder = os.path.join(source_data_folder, "Ex03")

# Unzip training data and config file
ansys.aedt.core.downloads.unzip(
    os.path.join(source_data_folder, source_snapshot_data_zipfilename), data_folder
)
shutil.copyfile(
    os.path.join(source_data_folder, source_build_conf_file),
    os.path.join(data_folder, source_build_conf_file),
)


# ## Launch Twin Builder and build ROM component
#
# Launch Twin Builder using an implicit declaration and add a new design with
# the default setup for building the dynamic ROM component.

project_name = os.path.join(temp_folder.name, "dynamic_rom.aedt")
tb = ansys.aedt.core.TwinBuilder(
    project=project_name,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Configure AEDT
#
# > **Note:** Only run the following cell if AEDT is not configured to run Twin Builder.
# >
# > The following cell configures AEDT and the schematic editor
# > to use the ``Twin Builder`` configuration.
# > The dynamic ROM feature is only available with a Twin Builder license.
# > A cell at the end of this example restores the AEDT configuration. If your
# > environment is set up to use the ``Twin Builder`` configuration, you do not
# > need to run these code blocks.

current_desktop_config = tb._odesktop.GetDesktopConfiguration()
current_schematic_environment = tb._odesktop.GetSchematicEnvironment()
tb._odesktop.SetDesktopConfiguration("Twin Builder")
tb._odesktop.SetSchematicEnvironment(1)

# Get the dynamic ROM builder object.
rom_manager = tb._odesign.GetROMManager()
dynamic_rom_builder = rom_manager.GetDynamicROMBuilder()

# Build the dynamic ROM with the specified configuration file.
conf_file_path = os.path.join(data_folder, source_build_conf_file)
dynamic_rom_builder.Build(conf_file_path.replace("\\", "/"))

# Test if the ROM was created successfully
dynamic_rom_path = os.path.join(data_folder, "DynamicRom.dyn")
if os.path.exists(dynamic_rom_path):
    tb._odesign.AddMessage(
        "Info", "path exists: {}".format(dynamic_rom_path.replace("\\", "/")), ""
    )
else:
    tb._odesign.AddMessage(
        "Info", "path does not exist: {}".format(dynamic_rom_path), ""
    )

# Create the ROM component definition in Twin Builder.
rom_manager.CreateROMComponent(dynamic_rom_path.replace("\\", "/"), "dynarom")


# ## Create schematic
#
# Place components to create a schematic.

# Define the grid distance for ease in calculations.

G = 0.00254

# Place a dynamic ROM component.

rom1 = tb.modeler.schematic.create_component("ROM1", "", "dynarom", [36 * G, 28 * G])

# Place two excitation sources.

source1 = tb.modeler.schematic.create_periodic_waveform_source(
    None, "PULSE", 190, 0.002, "300deg", 210, 0, [20 * G, 29 * G]
)
source2 = tb.modeler.schematic.create_periodic_waveform_source(
    None, "PULSE", 190, 0.002, "300deg", 210, 0, [20 * G, 25 * G]
)

# Connect components with wires.

tb.modeler.schematic.create_wire([[22 * G, 29 * G], [33 * G, 29 * G]])
tb.modeler.schematic.create_wire(
    [[22 * G, 25 * G], [30 * G, 25 * G], [30 * G, 28 * G], [33 * G, 28 * G]]
)

# Zoom to fit the schematic.
tb.modeler.zoom_to_fit()

# ## Parametrize transient setup
#
# Parametrize the default transient setup by setting the end time.

tb.set_end_time("1000s")
tb.set_hmin("1s")
tb.set_hmax("1s")

# ## Solve transient setup

tb.analyze_setup("TR", cores=NUM_CORES)


# ## Get report data and plot using Matplotlib
#
# Get report data and plot it using Matplotlib. The following code gets and plots
# the values for the voltage on the pulse voltage source and the values for the
# output of the dynamic ROM.

input_excitation = "PULSE1.VAL"
x = tb.post.get_solution_data(input_excitation, "TR", "Time")
plt.plot(x.intrinsics["Time"], x.data_real(input_excitation))

output_temperature = "ROM1.Temperature_history"
x = tb.post.get_solution_data(output_temperature, "TR", "Time")
plt.plot(x.intrinsics["Time"], x.data_real(output_temperature))

plt.grid()
plt.xlabel("Time")
plt.ylabel("Temperature History Variation with Input Temperature Pulse")
plt.show()


# ## Close Twin Builder
#
# After the simulation is completed, you can close Twin Builder or release it.
# All methods provide for saving the project before closing.

# Clean up the downloaded data.
shutil.rmtree(source_data_folder)

# Restore the earlier AEDT configuration and schematic environment.
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
