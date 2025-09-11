# ## Prerequisites
#
# ### Perform imports

# +
import tempfile
import time

import ansys.aedt.core  # Interface to Ansys Electronics Desktop
from ansys.aedt.core.generic.constants import Axis, Plane

# -

# ### Define constants
#
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ### Launch Maxwell 3d
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
# Later on we want to see how the magnetic flux density changes with the position of the collector.

m3d["magnet_radius"] = "2mm"
m3d["magnet_height"] = "15mm"
m3d["magnet_z_pos"] = "0mm"

# ## Add materials
#
# Create custom material ``"Aimant"``.

mat = m3d.materials.add_material("Aimant")
mat.permeability = "1.1"
mat.set_magnetic_coercivity(value=2005600, x=1, y=0, z=0)
mat.update()

# ## Create non-linear magnetic material with single valued BH curve
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

# Create custom material and add it to the AEDT library using the ``add_material`` method

mat = m3d.materials.add_material("Fer")
mat.permeability.value = bh_curve
mat.set_magnetic_coercivity(value=0, x=1, y=0, z=0)
mat.update()

# ## Create a simple geometry to model the collector
#
# Create a simple geometry to model the collector and assign a material to it.

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
    pad_value=20, pad_type="Percentage Offset", name="Region"
)

# ## Create the collector cross-section on the XZ plane

section = collector.section("XZ")

# ## Create simulation setup

setup = m3d.create_setup()
setup.props["MaximumPasses"] = 10
setup.props["PercentRefinement"] = 30
setup.props["PercentError"] = 2
setup.props["MinimumPasses"] = 2
setup.props["NonlinearResidual"] = 1e-3

# ## Add parametric sweep
#
# Create a linear count sweep where the parameter to sweep is ``"relative_cs_origin_z"``.
# The collector positions is changed at each step to see how the magnetic flux density on the polyline changes.
# Enable the saving fields option.

param_sweep = m3d.parametrics.add(
    variable="magnet_z_pos",
    start_point=m3d["magnet_z_pos"],
    end_point="25mm",
    step=5,
    variation_type="LinearCount",
)

param_sweep.props["ProdOptiSetupDataV2"]["SaveFields"] = True

# ## Analyze parametric sweep

param_sweep.analyze(cores=NUM_CORES)

# ## Create reports
#
# Create a rectangular and data plots of the magnetic flux density on the polyline
# for the different collector positions.

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

# ## Create field plots on the surface of the actuator's arms

m3d.post.create_fieldplot_surface(
    assignment=[Plane.ZX], quantity="Mag_B", plot_name="Mag_B1", field_type="Fields"
)

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
