# # Electrostatic analysis

# This example shows how to use PyAEDT to create a Maxwell 2D electrostatic analysis.
# It shows how to create the geometry, load material properties from a Microsoft Excel file, and
# set up the mesh settings. Moreover, it focuses on postprocessing operations, in particular how to
# plot field line traces, which are relevant for an electrostatic analysis.
#
# Keywords: **Maxwell 2D**, **electrostatic**.

# ## Perform imports and define constants
#
# Perform required imports.

# +
import os
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_file
# -

# Define constants.

AEDT_VERSION = "2025.1"
NUM_CORES = 4
NG_MODE = False

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``..

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download Excel file
#
# Set the local temporary folder to export the Excel (XLSX) file to.

file_name_xlsx = download_file(
    source="field_line_traces", name="my_copper.xlsx", local_path=temp_folder.name
)

# ## Initialize dictionaries
#
# Initialize the dictionaries that contain all the definitions for the design variables.

# +
geom_params_circle = {
    "circle_x0": "-10mm",
    "circle_y0": "0mm",
    "circle_z0": "0mm",
    "circle_axis": "Z",
    "circle_radius": "1mm",
}

geom_params_rectangle = {
    "r_x0": "1mm",
    "r_y0": "5mm",
    "r_z0": "0mm",
    "r_axis": "Z",
    "r_dx": "-1mm",
    "r_dy": "-10mm",
}
# -

# ## Launch AEDT and Maxwell 2D
#
# Launch AEDT and Maxwell 2D after first setting up the project and design names,
# the solver, and the version. The following code also creates an instance of the
# ``Maxwell2d`` class named ``m2d``.

project_name = os.path.join(temp_folder.name, "M2D_Electrostatic.aedt")
m2d = ansys.aedt.core.Maxwell2d(
    project=project_name,
    version=AEDT_VERSION,
    design="Design1",
    solution_type="Electrostatic",
    new_desktop=True,
    non_graphical=NG_MODE,
)

# ## Set modeler units
#
# Set modeler units to ``mm``.

m2d.modeler.model_units = "mm"

# ## Define variables from dictionaries
#
# Define design variables from the created dictionaries.

for k, v in geom_params_circle.items():
    m2d[k] = v
for k, v in geom_params_rectangle.items():
    m2d[k] = v

# ## Read materials from Excel file
#
# Read materials from the Excel file into the design.

mats = m2d.materials.import_materials_from_excel(file_name_xlsx)

# ## Create design geometries
#
# Create a rectangle and a circle. Assign the material read from the Excel file.
# Create two new polylines and a region.

# +
rect = m2d.modeler.create_rectangle(
    origin=["r_x0", "r_y0", "r_z0"],
    sizes=["r_dx", "r_dy", 0],
    name="Ground",
    material=mats[0],
)
rect.color = (0, 0, 255)  # rgb
rect.solve_inside = False

circle = m2d.modeler.create_circle(
    origin=["circle_x0", "circle_y0", "circle_z0"],
    radius="circle_radius",
    num_sides="0",
    is_covered=True,
    name="Electrode",
    material=mats[0],
)
circle.color = (0, 0, 255)  # rgb
circle.solve_inside = False

poly1_points = [[-9, 2, 0], [-4, 2, 0], [2, -2, 0], [8, 2, 0]]
poly2_points = [[-9, 0, 0], [9, 0, 0]]
poly1_id = m2d.modeler.create_polyline(
    points=poly1_points, segment_type="Spline", name="Poly1"
)
poly2_id = m2d.modeler.create_polyline(points=poly2_points, name="Poly2")
m2d.modeler.split(assignment=[poly1_id, poly2_id], plane="YZ", sides="NegativeOnly")
m2d.modeler.create_region(pad_value=[20, 100, 20, 100])
# -

# ## Define excitations
#
# Assign voltage excitations to the rectangle and circle.

m2d.assign_voltage(assignment=rect.id, amplitude=0, name="Ground")
m2d.assign_voltage(assignment=circle.id, amplitude=50e6, name="50kV")

# ## Create initial mesh settings
#
# Assign a surface mesh to the rectangle.

m2d.mesh.assign_surface_mesh_manual(assignment=["Ground"], surface_deviation=0.001)

# ## Create, validate, and analyze setup

setup_name = "MySetupAuto"
setup = m2d.create_setup(name=setup_name)
setup.props["PercentError"] = 0.5
setup.update()
m2d.validate_simple()
m2d.analyze_setup(name=setup_name, use_auto_settings=False, cores=NUM_CORES)

# ## Evaluate the E Field tangential component
#
# Evaluate the E Field tangential component along the given polylines.
# Add these operations to the **Named Expression** list in the field calculator.

e_line = m2d.post.fields_calculator.add_expression(
    calculation="e_line", assignment=None
)
m2d.post.fields_calculator.expression_plot(
    calculation="e_line", assignment="Poly1", names=[e_line]
)
m2d.post.fields_calculator.expression_plot(
    calculation="e_line", assignment="Poly12", names=[e_line]
)

# ## Create field line traces plot
#
# Create a field line traces plot specifying as seeding faces
# the ground, the electrode, and the region
# and as ``In surface objects`` only the region.

plot = m2d.post.create_fieldplot_line_traces(
    seeding_faces=["Ground", "Electrode", "Region"],
    in_volume_tracing_objs=["Region"],
    plot_name="LineTracesTest",
)

# ## Update field line traces plot
#
# Update the field line traces plot.
# Update the seeding points number, line style, and line width.

plot.SeedingPointsNumber = 20
plot.LineStyle = "Cylinder"
plot.LineWidth = 3
plot.update()

# ## Export field line traces plot
#
# Export the field line traces plot.
# For the field lint traces plot, the export file format is ``.fldplt``.

m2d.post.export_field_plot(
    plot_name="LineTracesTest", output_dir=temp_folder.name, file_format="fldplt"
)

# ## Export mesh field plot
#
# Export the mesh to an AEDTPLT file.

m2d.post.export_mesh_obj(setup=m2d.nominal_adaptive)

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
