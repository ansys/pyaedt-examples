# # Maxwell 2D Eddy Current analysis - Reduced Matrix

# This example shows how to leverage PyAEDT to assign matrix
# and perform series or parallel connections in a Maxwell 2D design.

# ## Perform required imports
#
# Perform required imports.

import tempfile
import time

import pyaedt

# ## Define constants

AEDT_VERSION = "2024.2"
NG_MODE = False

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

project_path = pyaedt.downloads.download_file(
    source="maxwell_ec_reduced_matrix",
    name="m2d_eddy_current.aedt",
    destination=temp_folder.name,
)

# ## Launch AEDT and Maxwell 2D
#
# Launch AEDT and Maxwell 2D providing the version, path to the project and the graphical mode.

m2d = pyaedt.Maxwell2d(
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

# ## Analyze setup

m2d.analyze()

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

ind = pyaedt.generic.constants.unit_converter(
    data.data_magnitude()[0],
    unit_system="Inductance",
    input_units=data.units_data[expressions[0]],
    output_units="uH",
)

# ## Release AEDT and clean up temporary directory
#
# Release AEDT and remove both the project and temporary directory.

m2d.release_desktop()

time.sleep(3)
temp_folder.cleanup()
