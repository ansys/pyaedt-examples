# # SBR+: HFSS to SBR+ coupling
#
# This example shows how you can use PyAEDT to create an HFSS SBR+ project from an
# HFSS antenna and run a simulation.
#
# Keywords: **HFSS SBR+**, **Reflector**.

# ## Perform required imports
#
# Perform required imports and set up the local path to the path for the PyAEDT
# directory.

import os
import tempfile
import pyaedt

# Set constant values

AEDT_VERSION = "2024.1"
NUM_CORES = 4
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory

temp_dir = tempfile.TemporaryDirectory(suffix="_ansys")

# ## Download project

project_full_name = pyaedt.downloads.download_sbr(destination=temp_dir.name)

# ## Define designs
#
# Define two designs, one source and one target, with each design connected to
# a different object.

# +
target = pyaedt.Hfss(
    project=project_full_name,
    design="Cassegrain_",
    solution_type="SBR+",
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
)

source = pyaedt.Hfss(
    project=target.project_name,
    design="feeder",
    version=AEDT_VERSION,
)
# -

# ## Define linked antenna
#
# Define a linked antenna. This is HFSS far field applied to HFSS SBR+.

target.create_sbr_linked_antenna(source, target_cs="feederPosition", fieldtype="farfield")

# ## Assign boundaries
#
# Assign boundaries.

target.assign_perfecte_to_sheets(["Reflector", "Subreflector"])
target.mesh.assign_curvilinear_elements(["Reflector", "Subreflector"])

# ## Plot model
#
# Plot the model

source.plot(
    show=False,
    export_path=os.path.join(target.working_directory, "Source.jpg"),
    plot_air_objects=True,
)
target.plot(
    show=False,
    export_path=os.path.join(target.working_directory, "Target.jpg"),
    plot_air_objects=False,
)

# ## Create setup and solve
#
# Create a setup and solve it.

setup1 = target.create_setup()
setup1.props["RadiationSetup"] = "ATK_3D"
setup1.props["ComputeFarFields"] = True
setup1.props["RayDensityPerWavelength"] = 2
setup1.props["MaxNumberOfBounces"] = 3
setup1["RangeType"] = "SinglePoints"
setup1["RangeStart"] = "10GHz"
target.analyze(num_cores=NUM_CORES)

# ## Post-processing
#
# Plot results in Electronics Desktop.

variations = target.available_variations.nominal_w_values_dict
variations["Freq"] = ["10GHz"]
variations["Theta"] = ["All"]
variations["Phi"] = ["All"]
target.post.create_report(
    "db(GainTotal)",
    target.nominal_adaptive,
    variations=variations,
    primary_sweep_variable="Theta",
    context="ATK_3D",
    report_category="Far Fields",
)

# Plot results using Matplotlib.

solution = target.post.get_solution_data(
    "GainTotal",
    target.nominal_adaptive,
    variations=variations,
    primary_sweep_variable="Theta",
    context="ATK_3D",
    report_category="Far Fields",
)
solution.plot()

# ## Release AEDT
#
# Release AEDT and close the example.

target.release_desktop()

# ## Cleanup
#
# All project files are saved in the folder ``temp_dir.name``. If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_dir.cleanup()
