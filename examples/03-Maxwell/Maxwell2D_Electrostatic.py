# # Maxwell 2D Electrostatic analysis

# This example shows how you can use PyAEDT to create a Maxwell 2D electrostatic analysis.
# It shows how to create the geometry, load material properties from an Excel file and
# set up the mesh settings. Moreover, it focuses on post-processing operations, in particular how to
# plot field line traces, relevant for an electrostatic analysis.

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

# ## Download .xlsx file
#
# Set local temporary folder to export the .xlsx file to.

file_name_xlsx = pyaedt.downloads.download_file(
    source="field_line_traces", name="my_copper.xlsx", destination=temp_folder.name
)

# ## Initialize dictionaries
#
# Initialize dictionaries that contain all the definitions for the design variables.

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
m2d = pyaedt.Maxwell2d(
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

# ## Read materials from .xslx file
#
# Read materials from .xslx file into and set into design.

mats = m2d.materials.import_materials_from_excel(file_name_xlsx)

# ## Create design geometries
#
# Create a rectangle and a circle and assign the material read from the .xlsx file.
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
# Assign voltage excitations to rectangle and circle.

m2d.assign_voltage(assignment=rect.id, amplitude=0, name="Ground")
m2d.assign_voltage(assignment=circle.id, amplitude=50e6, name="50kV")

# ## Create initial mesh settings
#
# Assign a surface mesh to the rectangle.

m2d.mesh.assign_surface_mesh_manual(assignment=["Ground"], surface_deviation=0.001)

# ## Create, validate and analyze the setup
#
# Create, update, validate and analyze the setup.

setup_name = "MySetupAuto"
setup = m2d.create_setup(name=setup_name)
setup.props["PercentError"] = 0.5
setup.update()
m2d.validate_simple()
m2d.analyze_setup(name=setup_name, use_auto_settings=False)

# ## Evaluate the E Field tangential component
#
# Evaluate the E Field tangential component along the given polylines.
# Add these operations to the Named Expression list in Field Calculator.

e_line = m2d.post.fields_calculator.add_expression(
    calculation="e_line", assignment=None
)
m2d.post.fields_calculator.expression_plot(
    calculation="e_line", assignment="Poly1", names=[e_line]
)
m2d.post.fields_calculator.expression_plot(
    calculation="e_line", assignment="Poly12", names=[e_line]
)

# ## Create Field Line Traces Plot
#
# Create Field Line Traces Plot specifying as seeding faces
# the ground, the electrode and the region
# and as ``In surface objects`` only the region.

plot = m2d.post.create_fieldplot_line_traces(
    seeding_faces=["Ground", "Electrode", "Region"],
    in_volume_tracing_objs=["Region"],
    plot_name="LineTracesTest",
)

# ## Update Field Line Traces Plot
#
# Update field line traces plot.
# Update seeding points number, line style and line width.

plot.SeedingPointsNumber = 20
plot.LineStyle = "Cylinder"
plot.LineWidth = 3
plot.update()

# ## Export field line traces plot
#
# Export field line traces plot.
# For field lint traces plot, the export file format is ``.fldplt``.

m2d.post.export_field_plot(
    plot_name="LineTracesTest", output_dir=temp_folder.name, file_format="fldplt"
)

# ## Export the mesh field plot
#
# Export the mesh in ``aedtplt`` format.

m2d.post.export_mesh_obj(setup=m2d.nominal_adaptive)

# ## Save project, release AEDT and clean up temporary directory
#
# Save project, release AEDT and remove both the project and temporary directory.

m2d.save_project()
m2d.release_desktop()

time.sleep(3)
temp_folder.cleanup()
