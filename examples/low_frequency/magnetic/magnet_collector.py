# ## Prerequisites
#
# ### Perform imports

# +
import os
import tempfile
import time

import ansys.aedt.core  # Interface to Ansys Electronics Desktop
from ansys.aedt.core.generic.constants import Axis

# -

# ### Define constants
#
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch Maxwell 3d
#
# Create an instance of
# the ``Maxwell3d`` class. The Ansys Electronics Desktop will be launched
# with an active Maxwell3D design. The ``m3d`` object is subsequently
# used to create and simulate the model.

m3d = ansys.aedt.core.Maxwell3d(
    project="magnet_collector",
    solution_type="Magnetostatic",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Define variables
#
# Later on we want to see how the magnetic flux density changes with the position of the magnet.

m3d["magnet_radius"] = "2mm"
m3d["magnet_height"] = "15mm"
m3d["magnet_z_pos"] = "0mm"

# ## Add materials
#
# ### Create custom material ``"Aimant"``.

mat = m3d.materials.add_material("Aimant")
mat.permeability = "1.1"
mat.set_magnetic_coercivity(value=2005600, x=1, y=1, z=0)
mat.update()

# ### Create non-linear magnetic material with single valued BH curve
#
# Create list with  BH curve data

bh_curve = [
    [0.0, 0.0],
    [0.032, 0.5],
    [0.049, 0.8],
    [0.065, 1],
    [0.081, 1.13],
    [0.17, 1.52],
    [0.32, 1.59],
    [0.65, 1.62],
    [0.81, 1.65],
    [1.61, 1.7],
    [3.19, 1.75],
    [4.78, 1.79],
    [6.34, 1.83],
    [7.96, 1.86],
    [15.89, 1.99],
    [31.77, 2.1],
    [63.53, 2.2],
    [158.77, 2.41],
    [317.48, 2.65],
    [635, 3.1],
]

# ### Create custom material "Fer" and assign the BH curve to the permeability value

mat = m3d.materials.add_material("Fer")
mat.permeability.value = bh_curve
mat.set_magnetic_coercivity(value=0, x=1, y=0, z=0)
mat.update()

# ## Create the collector
#
# Create a simple geometry to model the collector and assign a material to it.

# +
collector = m3d.modeler.create_cylinder(
    orientation=ansys.aedt.core.constants.AXIS.Z,
    origin=[12, 13, 25],
    height="3mm",
    radius="9.5mm",
    axisdir="Z",
    name="collector",
)
cylinder2 = m3d.modeler.create_cylinder(
    orientation=ansys.aedt.core.constants.AXIS.Z,
    origin=[12, 13, 25],
    height="3mm",
    radius="8mm",
    axisdir="Z",
    name="cyl2",
)

m3d.modeler.subtract(
    blank_list=[collector], tool_list=[cylinder2], keep_originals=False
)

cylinder3 = m3d.modeler.create_cylinder(
    orientation=ansys.aedt.core.constants.AXIS.Z,
    origin=[12, 13, 28],
    height="3mm",
    radius="8.7mm",
    axisdir="Z",
    name="cyl3",
)
cylinder4 = m3d.modeler.create_cylinder(
    orientation=ansys.aedt.core.constants.AXIS.Z,
    origin=[12, 13, 28],
    height="3mm",
    radius="2mm",
    axisdir="Z",
    name="cyl4",
)

m3d.modeler.subtract(
    blank_list=[cylinder3], tool_list=[cylinder4], keep_originals=False
)
m3d.modeler.unite(assignment=[collector, cylinder3], keep_originals=False)

collector.material_name = "Fer"
# -

# ## Create magnet
#
# Create a cylinder and assign a material to it.

magnet = m3d.modeler.create_cylinder(
    orientation=Axis.Z,
    origin=[0, 0, "magnet_z_pos"],
    radius="magnet_radius",
    height="magnet_height",
    num_sides=0,
    name="magnet",
    material="Aimant",
)

# ## Create a polyline
#
# Create a polyline to plot the field onto.
# The polyline is placed in the center of the collector so to capture the magnetic flux density.

line = m3d.modeler.create_polyline(points=[[12, 13, 0], [12, 13, "32mm"]], name="line")

# ## Create a vacuum region to enclose all objects

region = m3d.modeler.create_region(
    pad_value=50, pad_type="Percentage Offset", name="Region"
)

# ## Create the collector cross-section on the XZ plane

collector_relative_cs = m3d.modeler.create_coordinate_system(
    origin=[12, 13, 28], name="collector_cs"
)
section = m3d.modeler.create_rectangle(
    orientation="XZ",
    position=[-25, 0, -35],
    dimension_list=["50mm", "50mm"],
    name="section",
)
m3d.modeler.set_working_coordinate_system("Global")

# ## Create a dummy geometry for mesh operations
#
# Create a cylinder that encloses the polyline to force the mesh to be finer on the polyline.

dummy_cylinder = m3d.modeler.create_cylinder(
    orientation=Axis.Z,
    origin=[12, 13, 0],
    radius="1mm",
    height="32mm",
    num_sides=6,
    name="dummy_cylinder",
)

# ## Create a custom named expression
#
# Create a custom named expression to calculate relative permeability of the ferromagnetic material.
# This expression is used to see how the relative permeability of the collector changes with magnet position.

mu_r = {
    "name": "mu_r",
    "description": "Relative permeability of the ferromagnetic material",
    "design_type": ["Maxwell 3D"],
    "fields_type": ["Fields"],
    "primary_sweep": "Time",
    "assignment": "",
    "assignment_type": [""],
    "operations": [
        "NameOfExpression('Mag_B')",
        "NameOfExpression('Mag_H')",
        "Scalar_Constant(1.25664e-06)",
        "Operation('*')",
        "Operation('/')",
    ],
    "report": ["Field_3D"],
}
m3d.post.fields_calculator.add_expression(mu_r, None)

# ## Set mesh operations
#
# Assign mesh operations to the dummy cylinder and the collector.

poly_mesh = m3d.mesh.assign_length_mesh(
    assignment=[dummy_cylinder], maximum_length="1mm", name="polyline"
)
collector_mesh = m3d.mesh.assign_length_mesh(
    assignment=[collector],
    inside_selection=False,
    maximum_length="3.8mm",
    name="collector",
)

# ## Create simulation setup

setup = m3d.create_setup()
setup.props["MaximumPasses"] = 10
setup.props["PercentRefinement"] = 30
setup.props["PercentError"] = 2
setup.props["MinimumPasses"] = 2
setup.props["NonlinearResidual"] = 1e-3

# ## Add parametric sweep
#
# Create a linear count sweep where the parameter to sweep is ``"magnet_z_pos"``.
# The magnet position is changed at each step to see how the magnetic behavior of the system changes.
# Enable the saving fields option.

# +
param_sweep = m3d.parametrics.add(
    variable="magnet_z_pos",
    start_point=m3d["magnet_z_pos"],
    end_point="25mm",
    step=5,
    variation_type="LinearCount",
)

param_sweep.props["ProdOptiSetupDataV2"]["SaveFields"] = True
# -

# ### Analyze parametric sweep

param_sweep.analyze(cores=NUM_CORES)

# ## Create reports
#
# Create a rectangular and data plots of the magnetic flux density on the polyline
# for the different magnet positions.

# +
data_table = m3d.post.create_report(
    expressions="Mag_B",
    report_category="Fields",
    plot_type="Data Table",
    plot_name="Mag_B",
    variations={"magnet_z_pos": "All"},
    context=line.name,
    polyline_points=101,
)

rectangular_plot = m3d.post.create_report(
    expressions="Mag_B",
    report_category="Fields",
    plot_type="Rectangular Plot",
    plot_name="Mag_B",
    variations={"magnet_z_pos": "All"},
    context=line.name,
    polyline_points=101,
)
# -

# ## Create field plots
#
# Create field plots over the collector cross-section and on
# the collector surface to see how the magnetic flux density (B),
# the magnetic field strength (H) and the permeability
# of the ferromagnetic material (μ) change.

mag_b = m3d.post.create_fieldplot_surface(
    assignment=[section.name], quantity="Mag_B", plot_name="Mag_B", field_type="Fields"
)
mag_h = m3d.post.create_fieldplot_surface(
    assignment=[section.name], quantity="Mag_H", plot_name="Mag_H", field_type="Fields"
)
mu_r = m3d.post.create_fieldplot_surface(
    assignment=[collector.name], quantity="mu_r", plot_name="mu_r", field_type="Fields"
)

# ## Overlay fields using PyVista
#
# Plot electric field using PyVista and save to an image file.
# Plot the relative permeability on the collector surface at a given magnet position.

m3d["magnet_z_pos"] = "18.75mm"

py_vista_plot = m3d.post.plot_field(
    quantity="mu_r", assignment=collector.name, plot_cad_objs=True, show=False
)
py_vista_plot.isometric_view = False
py_vista_plot.camera_position = [0, 0, 7]
py_vista_plot.focal_point = [0, 0, 0]
py_vista_plot.roll_angle = 0
py_vista_plot.elevation_angle = 0
py_vista_plot.azimuth_angle = 0
py_vista_plot.plot(os.path.join(temp_folder.name, "mu_r.jpg"))

# ## BH curve of the ferromagnetic material
#
# From the plot exported in the previous section, we can see the trend of the relative permeability
# when the magnet gets close to the collector.
# Looking at the scale of the relative permeability, we can see that the collector is far from saturation.
# With a peak value around [...]3.1, the collector is still in the linear region of the BH curve.
# ![BH curve and relative permeability of the ferromagnetic material](../_static/BH.png)
# ![Zoom in on the relative permeability of the ferromagnetic material](../_static/BH_zoom_in.png)

# ## Release AEDT

m3d.save_project()
m3d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
