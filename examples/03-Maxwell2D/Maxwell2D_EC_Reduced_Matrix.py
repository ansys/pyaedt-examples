# # Eddy Current analysis and reduced matrix

# This example shows how to leverage PyAEDT to assign matrix
# and perform series or parallel connections in a Maxwell 2D design.
#
# Keywords: **HFSS**, **antenna array**, **far field**.

# ## Perform required imports
#
# Perform required imports.

import os
import tempfile
import time

import ansys.aedt.core

# ## Define constants

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory and download files
#
# Create a temporary directory where we store downloaded data or
# dumped data.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download .aedt file
#
# Set local temporary folder to export the .aedt file to.

project_path = ansys.aedt.core.downloads.download_file(
    source="maxwell_ec_reduced_matrix",
    name="m2d_eddy_current.aedt",
    destination=temp_folder.name,
)

# ## Launch AEDT and Maxwell 2D
#
# Launch AEDT and Maxwell 2D providing the version, path to the project and the graphical mode.

m2d = ansys.aedt.core.Maxwell2d(
    project=project_path,
    version=AEDT_VERSION,
    design="EC_Planar",
    non_graphical=NG_MODE,
)

# ## Assign a matrix
#
# Assign a matrix given the list of sources to assign the matrix to and the return path.

matrix = m2d.assign_matrix(
    assignment=["pri", "sec", "terz"], matrix_name="Matrix1", return_path="infinite"
)

# ## Assign reduced matrices
#
# Assign reduced matrices to the parent matrix previously created.
# For 2D/3D Eddy Current Solvers, two or more excitations can be joined
# either in series or parallel connection. The result is known as reduced matrix.

series = matrix.join_series(sources=["pri", "sec"], matrix_name="ReducedMatrix1")
parallel = matrix.join_parallel(sources=["sec", "terz"], matrix_name="ReducedMatrix2")

# ## Plot model

model = m2d.plot(show=False)
model.plot(os.path.join(temp_folder.name, "Image.jpg"))

# ## Analyze setup
#
# Run the analysis.

m2d.save_project()
m2d.analyze(setup=m2d.setup_names[0], cores=NUM_CORES, use_auto_settings=False)

# ## Get expressions
#
# Get the available report quantities given the context
# and the quantities category ``L``.

expressions = m2d.post.available_report_quantities(
    report_category="EddyCurrent",
    display_type="Data Table",
    context={"Matrix1": "ReducedMatrix1"},
    quantities_category="L",
)

# ## Create report and get solution data
#
# Create a data table report and get report data given the matrix context.

report = m2d.post.create_report(
    expressions=expressions,
    context={"Matrix1": "ReducedMatrix1"},
    plot_type="Data Table",
    setup_sweep_name="Setup1 : LastAdaptive",
    plot_name="reduced_matrix",
)
data = m2d.post.get_solution_data(
    expressions=expressions,
    context={"Matrix1": "ReducedMatrix1"},
    report_category="EddyCurrent",
    setup_sweep_name="Setup1 : LastAdaptive",
)

# ## Get matrix data
#
# Get inductance results for the join connections in ``nH``.

ind = ansys.aedt.core.generic.constants.unit_converter(
    data.data_magnitude()[0],
    unit_system="Inductance",
    input_units=data.units_data[expressions[0]],
    output_units="uH",
)

# ## Release AEDT

m2d.save_project()
m2d.release_desktop()
# Wait 3 seconds to allow Electronics Desktop to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Cleanup
#
# All project files are saved in the folder ``temp_dir.name``.
# If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
