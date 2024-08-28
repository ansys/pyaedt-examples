# # Magnetomotive force calculation along a contour
#
# This example shows how to use PyAEDT to calculate
# the magnetomotive force along several lines.
# It shows how to leverage PyAEDT advanced fields calculator
# to insert a custom formula, in this case the integral
# of the H field along a line.
#
# Keywords: **Maxwell 2D**, **magnetomotive force**.


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

# ## Import project
#
# The files required to run this example will be downloaded into the temporary working folder.

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

# ## Create a polyline
#
# Create a polyline specifying its points.

poly = m2d.modeler.create_polyline(points=[[10, -10, 0], [10, 10, 0]], name="polyline")

# Duplicate polyline along a vector

polys = [poly.name]
polys.extend(poly.duplicate_along_line(vector=[-0.5, 0, 0], clones=10))

# ## Plot model

model = m2d.plot(show=False)
model.plot(os.path.join(temp_folder.name, "Image.jpg"))

# ## Analyze setup
#
# Analyze setup specifying setup name

m2d.analyze_setup(name=m2d.setups[0].name, cores=NUM_CORES, use_auto_settings=False)

# ## Compute magnetomotive force along each line
#
# Create and add a new formula to add in PyAEDT advanced fields calculator.
# Create fields report object and get field data.
# Create a Data Table report for H field along each line and export it in a .csv file.

for p in polys:
    quantity = "H_field_{}".format(p)
    my_expression = {
        "name": quantity,
        "description": "Magnetomotive force along a line",
        "design_type": ["Maxwell 2D", "Maxwell 3D"],
        "fields_type": ["Fields"],
        "primary_sweep": "distance",
        "assignment": p,
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
    m2d.post.fields_calculator.add_expression(my_expression, p)
    report = m2d.post.reports_by_category.fields(
        expressions=quantity, setup=m2d.nominal_sweep, polyline=p
    )
    data = report.get_solution_data()
    h = data.data_magnitude()
    report = m2d.post.create_report(
        expressions=quantity,
        context=p,
        polyline_points=1,
        report_category="Fields",
        plot_type="Data Table",
        plot_name=quantity,
    )
    m2d.post.export_report_to_csv(
        project_dir=temp_folder.name,
        plot_name=quantity,
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
