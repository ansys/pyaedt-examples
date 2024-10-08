# # LTI ROM creation and simulation

# This example shows how you can use PyAEDT to create a Linear Time Invariant (LTI) ROM in Twin Builder
# and run a Twin Builder time-domain simulation. Inputs data are defined using Datapairs blocks with CSV files.
#
# Keywords: **Twin Builder**, **LTI**, **ROM**.

# ## Perform imports and define constants
#
# Perform required imports.

import datetime
import os
import subprocess
import tempfile
import time

import matplotlib.pyplot as plt
from ansys.aedt.core import TwinBuilder, downloads
from ansys.aedt.core.application.variables import CSVDataset

# Define constants

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Set paths and define input files and variables
#
# Set paths.

training_data_folder = "LTI_training_data.zip"
temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
input_dir = downloads.download_twin_builder_data(
    training_data_folder, True, temp_folder.name
)

# Download data from example_data repository

data_folder = os.path.join(input_dir, "LTI_training")

# Unzip training data and parse ports names

downloads.unzip(os.path.join(input_dir, training_data_folder), data_folder)
ports_names_file = "Input_PortNames.txt"


# ## Get ports information from file


def get_ports_info(ports_file):
    with open(ports_file, "r") as PortNameFile:
        res = []
        line = PortNameFile.readline()
        line_list = list(line.split())
        for i in range(len(line_list)):
            res.append("Input" + str(i + 1) + "_" + line_list[i])

        line = PortNameFile.readline()
        line_list = list(line.split())
        for i in range(len(line_list)):
            res.append("Output" + str(i + 1) + "_" + line_list[i])
    return res


pin_names = get_ports_info(os.path.join(data_folder, ports_names_file))

# ## Launch Twin Builder
#
# Launch Twin Builder using an implicit declaration and add a new design with
# the default setup.

project_name = os.path.join(temp_folder.name, "LTI_ROM.aedt")
tb = TwinBuilder(
    project=project_name, version=AEDT_VERSION, non_graphical=NG_MODE, new_desktop=True
)

# ## Build the LTI ROM with specified configuration file

install_dir = tb.odesktop.GetRegistryString("Desktop/InstallationDirectory")
fitting_exe = os.path.join(install_dir, "FittingTool.exe")
path = '"' + fitting_exe + '"' + "  " + '"t"' + "  " + '"' + data_folder + '"'
process = subprocess.Popen(
    path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
tb.logger.info("Fitting the LTI ROM training data")
exec = True
startTime = datetime.datetime.now()
execTime = 0.0
while (
    exec and execTime < 60.0
):  # limiting the fitting process execution time to 1 minute
    out, err = process.communicate()
    execTime = (datetime.datetime.now() - startTime).total_seconds()
    if "An LTI ROM has been generated" in str(out):
        process.terminate()
        exec = False

rom_file = ""
model_name_sml = ""

for i in os.listdir(data_folder):
    if i.endswith(".sml"):
        model_name_sml = i.split(".")[0]
        rom_file = os.path.join(data_folder, i)

if os.path.exists(rom_file):
    tb.logger.info("Built intermediate ROM file successfully at: %s", rom_file)
else:
    tb.logger.info("ROM file does not exist at the expected location : %s", rom_file)


# ## Import the ROM component model

is_created = tb.modeler.schematic.create_component_from_sml(
    input_file=rom_file, model=model_name_sml, pins_names=pin_names
)
os.remove(rom_file)
tb.logger.info("LTI ROM model successfully imported.")

# ## Import the ROM component model in Twin Builder
#
# Place components to create a schematic.

# Define the grid distance for ease in calculations

G = 0.00254

# Place the ROM component

rom1 = tb.modeler.schematic.create_component(
    "ROM1", "", model_name_sml, [36 * G, 28 * G]
)

# Place datapairs blocks for inputs definition

source1 = tb.modeler.schematic.create_component(
    "source1",
    "",
    "Simplorer Elements\\Basic Elements\\Tools\\Time Functions:DATAPAIRS",
    [20 * G, 29 * G],
)
source2 = tb.modeler.schematic.create_component(
    "source2",
    "",
    "Simplorer Elements\\Basic Elements\\Tools\\Time Functions:DATAPAIRS",
    [20 * G, 25 * G],
)

# Import Datasets

data1 = CSVDataset(os.path.join(data_folder, "data1.csv"))
data2 = CSVDataset(os.path.join(data_folder, "data2.csv"))
dataset1 = tb.create_dataset("data1", data1.data["time"], data1.data["input1"])
dataset2 = tb.create_dataset("data2", data2.data["time"], data2.data["input2"])

source1.parameters["CH_DATA"] = dataset1.name
source2.parameters["CH_DATA"] = dataset2.name

tb.modeler.schematic.update_quantity_value(source1.composed_name, "PERIO", "0")

tb.modeler.schematic.update_quantity_value(
    source1.composed_name, "TPERIO", "Tend+1", "s"
)

tb.modeler.schematic.update_quantity_value(source2.composed_name, "PERIO", "0")

tb.modeler.schematic.update_quantity_value(
    source2.composed_name, "TPERIO", "Tend+1", "s"
)

# Connect components with wires

tb.modeler.schematic.create_wire(
    points=[source1.pins[0].location, rom1.pins[0].location]
)
tb.modeler.schematic.create_wire(
    points=[source2.pins[0].location, rom1.pins[1].location]
)

# Zoom to fit the schematic

tb.modeler.zoom_to_fit()

# ## Parametrize transient setup
#
# Parametrize the default transient setup by setting the end time and minimum/maximum time steps.

tb.set_end_time("700s")
tb.set_hmin("0.001s")
tb.set_hmax("1s")

# ## Solve transient setup
#
# Solve the transient setup.

tb.analyze_setup("TR")

# ## Get report data and plot using Matplotlib
#
# Get report data and plot it using Matplotlib. The following code gets and plots
# the values for the inputs and outputs of the LTI ROM.

# Units used are based on AEDT default units.

variables_postprocessing = []
pin_names_str = ",".join(pin_names)
rom_pins = pin_names_str.lower().split(",")
fig, ax = plt.subplots(ncols=1, nrows=2, figsize=(18, 7))
fig.subplots_adjust(hspace=0.5)

for i in range(0, 2):
    variable = "ROM1." + rom_pins[i]
    x = tb.post.get_solution_data(variable, "TR", "Time")
    ax[0].plot(
        [el for el in x.intrinsics["Time"]], x.data_real(variable), label=variable
    )

ax[0].set_title("ROM inputs")
ax[0].legend(loc="upper left")

for i in range(2, 4):
    variable = "ROM1." + rom_pins[i]
    x = tb.post.get_solution_data(variable, "TR", "Time")
    ax[1].plot(
        [el for el in x.intrinsics["Time"]], x.data_real(variable), label=variable
    )

ax[1].set_title("ROM outputs")
ax[1].legend(loc="upper left")

# Show plot

plt.show()

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
