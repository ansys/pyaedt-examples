# # Magnetomotive force along a line
#
# This example shows how to use PyAEDT to calculate
# the magnetomotive force along a line that changes position.
# It shows how to leverage the PyAEDT advanced fields calculator
# to insert a custom formula, which in this case is the integral
# of the H field along a line. It computes the field for each position
# with a parametric sweep.
#
# Keywords: **Maxwell 2D**, **magnetomotive force**.

# ## Perform imports and define constants
#
# Perform required imports.

import os
import tempfile
import time

import ansys.aedt.core

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

# ## Import project
#
# Download the files required to run this example to the temporary working folder.

project_path = ansys.aedt.core.downloads.download_file(
    source="maxwell_magnetic_force",
    name="Maxwell_Magnetic_Force.aedt",
    destination=temp_folder.name,
)

# ## Initialize and launch Maxwell 2D
#
# Initialize and launch Maxwell 2D, providing the version and the path of the project.

m2d = ansys.aedt.core.Maxwell2d(
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    project=project_path,
    design="Maxwell2DDesign1",
)

# ## Create a design variable
#
# Parametrize the polyline x position.

m2d["xl"] = "10mm"

# ## Create polyline
#
# Create a polyline, specifying its points.

poly = m2d.modeler.create_polyline(
    points=[["xl", -10, 0], ["xl", 10, 0]], name="polyline"
)

# ## Plot model

model = m2d.plot(show=False)
model.plot(os.path.join(temp_folder.name, "Image.jpg"))

# ## Add parametric sweep
#
# Add a parametric sweep where the parameter to sweep is ``xl``.
# Create a linear step sweep from ``10mm`` to ``15mm`` every ``1mm`` step.

param_sweep = m2d.parametrics.add(
    variable="xl",
    start_point="10mm",
    end_point="15mm",
    step=1,
    variation_type="LinearStep",
)

# ## Compute magnetomotive force along the line
#
# Create and add a new formula to add in the PyAEDT advanced fields calculator.

quantity = "H_field_{}".format(poly.name)
my_expression = {
    "name": quantity,
    "description": "Magnetomotive force along a line",
    "design_type": ["Maxwell 2D", "Maxwell 3D"],
    "fields_type": ["Fields"],
    "primary_sweep": "distance",
    "assignment": poly.name,
    "assignment_type": ["Line"],
    "operations": [
        "Fundamental_Quantity('H')",
        "Operation('Tangent')",
        "Operation('Dot')",
        "EnterLine('assignment')",
        "Operation('LineValue')",
        "Operation('Integrate')",
    ],
    "report": ["Data Table"],
}
m2d.post.fields_calculator.add_expression(my_expression, poly.name)

# ## Add parametric sweep calculation specifying the quantity (H).

param_sweep.add_calculation(calculation=quantity, report_type="Fields", ranges={})

# ## Analyze parametric sweep

param_sweep.analyze(cores=NUM_CORES)

# ## Create data table report
#
# Create a data table report to display H for each polyline position.
# Afterwards, export results to a CSV file.

report = m2d.post.create_report(
    expressions=quantity,
    report_category="Fields",
    plot_type="Data Table",
    plot_name=quantity,
    primary_sweep_variable="xl",
)
m2d.post.export_report_to_csv(
    project_dir=temp_folder.name,
    plot_name=quantity,
)

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
