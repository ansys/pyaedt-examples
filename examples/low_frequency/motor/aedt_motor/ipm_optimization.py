# # IPM geometry optimization
#
# This example shows how to use PyAEDT to find the best machine 2D geometry
# to achieve high torque and low losses.
# The example shows how to setup an optimetrics analysis to sweep geometries
# for a single value of stator current angle.
# The torque and losses results are then exported in a .csv file.
#
# Keywords: **Maxwell 2D**, **transient**, **motor**, **optimization**.

# ## Prerequisites
#
# ### Perform imports

# +
import csv
import os
import tempfile
import time

import ansys.aedt.core
# -

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.1"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ### Retrieve the Maxwell project file
#
# This examples starts 

aedt_file = ansys.aedt.core.downloads.download_file(
    source="maxwell_motor_optimization",
    name="IPM_optimization.aedt",
    destination=temp_folder.name,
)

# ## Launch Maxwell 2D
#
# Launch AEDT and Maxwell 2D after first setting up the project, the version and the graphical mode.

m2d = ansys.aedt.core.Maxwell2d(
    project=aedt_file,
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
)

# ## Add parametric setup
#
# Add a parametric setup made up of geometry variable sweep definitions and single value for the stator current angle.
# Note: Step variations have been minimized to reduce the analysis time. If needed they can be increased by changing
# the ``step`` argument.

param_sweep = m2d.parametrics.add(
    variable="bridge",
    start_point="0.5mm",
    variation_type="SingleValue",
)
param_sweep.add_variation(
    sweep_variable="din",
    start_point=70,
    end_point=80,
    step=10,
    units="mm",
    variation_type="LinearStep",
)
param_sweep.add_variation(
    sweep_variable="phase_advance",
    start_point=45,
    units="deg",
    variation_type="SingleValue",
)
param_sweep.add_variation(
    sweep_variable="Ipeak", start_point=200, units="A", variation_type="SingleValue"
)

# ## Analyze parametric sweep

param_sweep.analyze(cores=NUM_CORES)

# ## Post-processing
#
# Create reports to get torque and loss results for all variations.

report_torque = m2d.post.create_report(
    expressions="Moving1.Torque",
    domain="Sweep",
    variations={"bridge": "All", "din": "All", "Ipeak": "All", "phase_advance": "All"},
    primary_sweep_variable="Time",
    plot_type="Rectangular Plot",
    plot_name="TorqueAllVariations",
)

report_solid_loss = m2d.post.create_report(
    expressions="SolidLoss",
    domain="Sweep",
    variations={"bridge": "All", "din": "All", "Ipeak": "All", "phase_advance": "All"},
    primary_sweep_variable="Time",
    plot_type="Rectangular Plot",
    plot_name="SolidLossAllVariations",
)

report_core_loss = m2d.post.create_report(
    expressions="CoreLoss",
    domain="Sweep",
    variations={"bridge": "All", "din": "All", "Ipeak": "All", "phase_advance": "All"},
    primary_sweep_variable="Time",
    plot_type="Rectangular Plot",
    plot_name="CoreLossAllVariations",
)

# Get torque and loss solution data for all available variations.

torque_data = m2d.post.get_solution_data(
    expressions=["Moving1.Torque"],
    setup_sweep_name=m2d.nominal_sweep,
    domain="Sweep",
    variations={"bridge": "All", "din": "All", "Ipeak": "All", "phase_advance": "All"},
    primary_sweep_variable="Time",
    report_category="Standard",
)

solid_loss_data = m2d.post.get_solution_data(
    expressions=["CoreLoss"],
    setup_sweep_name=m2d.nominal_sweep,
    domain="Sweep",
    variations={"bridge": "All", "din": "All", "Ipeak": "All", "phase_advance": "All"},
    primary_sweep_variable="Time",
    report_category="Standard",
)

core_loss_data = m2d.post.get_solution_data(
    expressions=["SolidLoss"],
    setup_sweep_name=m2d.nominal_sweep,
    domain="Sweep",
    variations={"bridge": "All", "din": "All", "Ipeak": "All", "phase_advance": "All"},
    primary_sweep_variable="Time",
    report_category="Standard",
)

# Calculate torque and loss average values for each variation and write data in a .csv file.

csv_data = []
for var in core_loss_data.variations:
    torque_data.active_variation = var
    core_loss_data.active_variation = var
    solid_loss_data.active_variation = var

    torque_values = torque_data.data_magnitude()
    core_loss_values = core_loss_data.data_magnitude()
    solid_loss_values = solid_loss_data.data_magnitude()

    torque_data_average = sum(torque_values) / len(torque_values)
    core_loss_average = sum(core_loss_values) / len(core_loss_values)
    solid_loss_average = sum(solid_loss_values) / len(solid_loss_values)

    csv_data.append(
        {
            "active_variation": str(torque_data.active_variation),
            "average_torque": str(torque_data_average),
            "average_core_loss": str(core_loss_average),
            "average_solid_loss": str(solid_loss_average),
        }
    )

    with open(
        os.path.join(temp_folder.name, "motor_optimization.csv"), "w", newline=""
    ) as csvfile:
        fields = [
            "active_variation",
            "average_torque",
            "average_core_loss",
            "average_solid_loss",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(csv_data)

# ## Release AEDT

m2d.save_project()
m2d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
