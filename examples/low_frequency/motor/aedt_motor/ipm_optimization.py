# # IPM geometry optimization
#
# This example shows how to use PyAEDT to find the best machine 2D geometry
# to achieve high torque and low losses.
# The example shows how to setup an optimetrics analysis to sweep geometries
# for a single value of stator current angle.
# The torque and losses results are then exported in a .csv file.
#
# Keywords: **Maxwell 2D**, **transient**, **motor**, **optimization**.

# ## Perform imports and define constants
#
# Perform required imports.

# +
import csv
import os
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_file

# -

# Define constants.

AEDT_VERSION = "2025.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory and download files
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download AEDT file example
#
# Set the local temporary folder to export the AEDT file to.

aedt_file = download_file(
    source="maxwell_motor_optimization",
    name="IPM_optimization.aedt",
    local_path=temp_folder.name,
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

# ## Design variables
#
# Define the materials array to be used in the parametric sweep.

m2d["mat_sweep"] = '["XG196/96_2DSF1.000_X", "NdFe30", "NdFe35"]'
m2d["mat_index"] = 0

# ## Assign material array to magnets
#
# Get all magnets in the design that by default have the material ``"XG196/96_2DSF1.000_X"`` assigned.
# Assign the material array defined above to all magnets.

magnets = m2d.modeler.get_objects_by_material("XG196/96_2DSF1.000_X")

for mag in magnets:
    mag.material_name = "mat_sweep[mat_index]"

# Add parametric from file
file_path = r"C:\Test\Volvo_Wenliang\2nd issue\ipm_optimazation.csv"
param_sweep_from_file = m2d.parametrics.add_from_file(file_path)

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
    start_point=78,
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

# Add material variation to the parametric setup and sweep the index of the material array defined above.

param_sweep.add_variation(
    sweep_variable="mat_index",
    start_point=0,
    end_point=2,
    step=1,
    variation_type="LinearCount",
)

# ## Alternative way to add a parametric setup from file
#
# Suppose you have a .csv file with all the parameters to be swept defined in columns, such as:
#
# # <img src="_static/param_sweep.png" alt="" width="400">
#
# You can add a parametric setup from that file using the ``add_from_file`` method:

# +
# param_sweep_from_file = m2d.parametrics.add_from_file(csv_file_path)
# -

# ## Analyze parametric sweep

param_sweep.analyze(cores=NUM_CORES)

# ## Post-processing
#
# Create reports to get torque and loss results for all variations.

report_torque = m2d.post.create_report(
    expressions="Moving1.Torque",
    domain="Sweep",
    variations={
        "bridge": "All",
        "din": "All",
        "Ipeak": "All",
        "phase_advance": "All",
        "mat_index": "All",
    },
    primary_sweep_variable="Time",
    plot_type="Rectangular Plot",
    plot_name="TorqueAllVariations",
)

report_solid_loss = m2d.post.create_report(
    expressions="SolidLoss",
    domain="Sweep",
    variations={
        "bridge": "All",
        "din": "All",
        "Ipeak": "All",
        "phase_advance": "All",
        "mat_index": "All",
    },
    primary_sweep_variable="Time",
    plot_type="Rectangular Plot",
    plot_name="SolidLossAllVariations",
)

report_core_loss = m2d.post.create_report(
    expressions="CoreLoss",
    domain="Sweep",
    variations={
        "bridge": "All",
        "din": "All",
        "Ipeak": "All",
        "phase_advance": "All",
        "mat_index": "All",
    },
    primary_sweep_variable="Time",
    plot_type="Rectangular Plot",
    plot_name="CoreLossAllVariations",
)

# Get torque and loss solution data for all available variations.

torque_data = m2d.post.get_solution_data(
    expressions=["Moving1.Torque"],
    setup_sweep_name=m2d.nominal_sweep,
    domain="Sweep",
    variations={
        "bridge": "All",
        "din": "All",
        "Ipeak": "All",
        "phase_advance": "All",
        "mat_index": "All",
    },
    primary_sweep_variable="Time",
    report_category="Standard",
)

solid_loss_data = m2d.post.get_solution_data(
    expressions=["CoreLoss"],
    setup_sweep_name=m2d.nominal_sweep,
    domain="Sweep",
    variations={
        "bridge": "All",
        "din": "All",
        "Ipeak": "All",
        "phase_advance": "All",
        "mat_index": "All",
    },
    primary_sweep_variable="Time",
    report_category="Standard",
)

core_loss_data = m2d.post.get_solution_data(
    expressions=["SolidLoss"],
    setup_sweep_name=m2d.nominal_sweep,
    domain="Sweep",
    variations={
        "bridge": "All",
        "din": "All",
        "Ipeak": "All",
        "phase_advance": "All",
        "mat_index": "All",
    },
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
