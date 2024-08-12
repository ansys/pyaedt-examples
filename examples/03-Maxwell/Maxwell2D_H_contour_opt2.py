# # Maxwell 2D: Magnetomotive force calculation along a contour
#
# This example shows how to use PyAEDT to calculate
# the magnetomotive force along a line that changes position.
# It shows how to leverage PyAEDT advanced fields calculator
# to insert a custom formula, in this case the integral
# of the H field along a line and compute the field for each position.

# ## Perform required imports
#
# Perform required imports.

import os
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

# ## Import project
#
# The files required to run this example will be downloaded into the temporary working folder.

project_path = pyaedt.downloads.download_file(
    source="maxwell_magnetic_force",
    name="Maxwell_Magnetic_Force",
    destination=temp_folder.name,
)

# ## Initialize and launch Maxwell 2D
#
# Initialize and launch Maxwell 2D, providing the version and the path of the project.

m2d = pyaedt.Maxwell2d(
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    project=project_path,
    design="Maxwell2DDesign1",
)

# ## Create a new design variable
#
# Parametrize polyline x position.

m2d["xl"] = "10mm"

# ## Create a polyline
#
# Create a polyline specifying its points.

poly = m2d.modeler.create_polyline(
    points=[["xl", -10, 0], ["xl", 10, 0]], name="polyline"
)

# ## Add a parametric sweep
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
# Create and add a new formula to add in PyAEDT advanced fields calculator.

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

param_sweep.analyze()

# ## Create a data table report
#
# Create a data table report to display H for each polyline position.
# Afterward export results in a .csv file.

report = m2d.post.create_report(
    expressions=quantity,
    report_category="Fields",
    plot_type="Data Table",
    plot_name=quantity,
    primary_sweep_variable="xl",
)
m2d.post.export_report_to_csv(
    project_dir=os.path.join(temp_folder.name, "{}.csv".format(quantity)),
    plot_name=quantity,
)

# ## Release AEDT and clean up temporary directory
#
# Release AEDT and remove both the project and temporary directory.

m2d.release_desktop()

time.sleep(3)
temp_folder.cleanup()
