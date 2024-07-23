# # Twin Builder: Dynamic ROM
#
# This example shows how you can use PyAEDT to create a dynamic ROM in Twin Builder
# and run a Twin Builder time-domain simulation.
#
# > **Note:** This example uses functionality only available in Twin
# > Builder 2023 R2 and later.


# ## Setup project and environment
#
# Perform required imports.

import os
import shutil
import matplotlib.pyplot as plt
from pyaedt import TwinBuilder, downloads
import tempfile

# Set constant values

AEDT_VERSION = "2024.1"
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary folder
#
# Simulation data will be saved in the temporary folder. 
# If you run this example as a Jupyter Notebook,
# the results and project data can be retrieved before executing the
# final cell of the notebook.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")

# Specify the file names to be dowloaded for this example.

source_snapshot_data_zipfilename = "Ex1_Mechanical_DynamicRom.zip"
source_build_conf_file = "dynarom_build.conf"

# Download data from example_data repository

source_data_folder = downloads.download_twin_builder_data(
    source_snapshot_data_zipfilename, True, temp_dir.name
)

source_data_folder = downloads.download_twin_builder_data(source_build_conf_file, True, temp_dir.name)

# Toggle these for local testing
# source_data_folder = "D:\\Scratch\\TempDyn"

data_folder = os.path.join(source_data_folder, "Ex03")

# Unzip training data and config file
downloads.unzip(os.path.join(source_data_folder, source_snapshot_data_zipfilename), data_folder)
shutil.copyfile(
    os.path.join(source_data_folder, source_build_conf_file),
    os.path.join(data_folder, source_build_conf_file),
)


# ## Launch Twin Builder and build ROM component
#
# Launch Twin Builder using an implicit declaration and add a new design with
# a default setup for building the dynamic ROM component.

tb = TwinBuilder(
    project=os.path.join(temp_dir.name, "DynaROM.aedt"),
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Desktop Configuration
#
# > **Note:** Only run following cell if AEDT is not configured to run _"Twin Builder"_.
# >
# > The following cell configures Electronics Desktop (AEDT) and the schematic editor
# > to use the _"Twin Builder"_ configuration.
# > The dynamic ROM feature is only available with a Twin Builder license.
# > A cell at the end of this example restores the AEDT configuration. If your
# > environment is set up
# > to use the _"Twin Builder"_ configuration, you do not need to run these sections.
# >

current_desktop_config = tb._odesktop.GetDesktopConfiguration()
current_schematic_environment = tb._odesktop.GetSchematicEnvironment()
tb._odesktop.SetDesktopConfiguration("Twin Builder")
tb._odesktop.SetSchematicEnvironment(1)

# Get the dynamic ROM builder object

rom_manager = tb._odesign.GetROMManager()
dynamic_rom_builder = rom_manager.GetDynamicROMBuilder()

# Build the dynamic ROM with specified configuration file

conf_file_path = os.path.join(data_folder, source_build_conf_file)
dynamic_rom_builder.Build(conf_file_path.replace("\\", "/"))

# Test if ROM was created successfully

dynamic_rom_path = os.path.join(data_folder, "DynamicRom.dyn")
if os.path.exists(dynamic_rom_path):
    tb._odesign.AddMessage(
        "Info", "path exists: {}".format(dynamic_rom_path.replace("\\", "/")), ""
    )
else:
    tb._odesign.AddMessage("Info", "path does not exist: {}".format(dynamic_rom_path), "")

# Create the ROM component definition in Twin Builder


rom_manager.CreateROMComponent(dynamic_rom_path.replace("\\", "/"), "dynarom")


# Define the grid spacing in the schematic editor.

G = 0.00254

# Place a dynamic ROM component

rom1 = tb.modeler.schematic.create_component("ROM1", "", "dynarom", [36 * G, 28 * G])

# Place two excitation sources

source1 = tb.modeler.schematic.create_periodic_waveform_source(
    None, "PULSE", 190, 0.002, "300deg", 210, 0, [20 * G, 29 * G]
)
source2 = tb.modeler.schematic.create_periodic_waveform_source(
    None, "PULSE", 190, 0.002, "300deg", 210, 0, [20 * G, 25 * G]
)

# Connect components with wires

tb.modeler.schematic.create_wire([[22 * G, 29 * G], [33 * G, 29 * G]])
tb.modeler.schematic.create_wire(
    [[22 * G, 25 * G], [30 * G, 25 * G], [30 * G, 28 * G], [33 * G, 28 * G]]
)

tb.modeler.zoom_to_fit()  # Zoom to fit the schematic

# ## Run simulation
#
# Parametrize the default transient setup by setting the end time.

tb.set_end_time("1000s")
tb.set_hmin("1s")
tb.set_hmax("1s")

# Solve the transient setup.

tb.analyze_setup("TR")


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

shutil.rmtree(source_data_folder)  # Clean up the downloaded data

# Restore earlier desktop configuration and schematic environment

tb._odesktop.SetDesktopConfiguration(current_desktop_config)
tb._odesktop.SetSchematicEnvironment(current_schematic_environment)
tb.release_desktop()

# ## Cleanup
#
# All project files are saved in the folder ``temp_dir.name``. If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_dir.cleanup()
