# ## Prerequisites
#
# ### Perform imports

# +
import tempfile
import time

import ansys.aedt.core  # Interface to Ansys Electronics Desktop
from ansys.aedt.core.examples.downloads import download_file

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
m3d["magnet_height"] = "18mm"
m3d["relative_cs_origin_z"] = "0mm"

# ## Add materials
#
# Create custom material ``"Aimant"``.

mat = m3d.materials.add_material("Aimant")
mat.permeability = "1.1"
mat.set_magnetic_coercivity(value=-2005600, x=-1, y=0, z=0)
mat.update()

# Create custom material ``"Iron"``.
#
# This material uses a BH curve to define its nonlinear magnetic properties.
# The BH curve is firstly downloaded and then imported as a dataset into material properties.

iron_bh_curve_path = download_file(
    source="bh_curve", name="iron_bh_curve.tab", local_path=temp_folder.name
)
mat = m3d.materials.add_material("Iron")
iron_bh_curve = m3d.import_dataset1d(iron_bh_curve_path)
mat.permeability.value = [[a, b] for a, b in zip(iron_bh_curve.x, iron_bh_curve.y)]
mat.set_magnetic_coercivity(value=0, x=1, y=0, z=0)
mat.update()

# ## Import geometry as a STEP file
#
# You can test importing a STEP or a Parasolid file by changing the source argument
# in the ``download_file`` method.
# Both file formats are available to download.
# A relative coordinate system is created to facilitate moving the collector along the Z direction.
# The material "Iron" is assigned to the collector and its coordinate system is set to the relative coordinate system
# previously created.

collector_path = download_file(
    source="step", name="[].step", local_path=temp_folder.name
)
relative_cs = m3d.modeler.create_coordinate_system(
    origin=[0, 0, "relative_cs_origin_z"], name="collector_cs"
)
m3d.modeler.import_3d_cad(collector_path)
collector = m3d.modeler.object_list[0]
collector.material_name = "Iron"
collector.part_coordinate_system = relative_cs.name
m3d.modeler.set_working_coordinate_system("Global")

# ## Create magnet
#
# Create a cylinder and assign a material to it.

magnet = m3d.modeler.create_cylinder(
    orientation=ansys.aedt.core.constants.AXIS.Z,
    origin=[0, 0, 0],
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

x_1_center = collector.bottom_face_z.center[0]
y_1_center = collector.bottom_face_z.center[1]
line = m3d.modeler.create_polyline(
    points=[[x_1_center, y_1_center, 0], [x_1_center, y_1_center, "100mm"]], name="line"
)

# ## Create a vacuum region to enclose all objects

region = m3d.modeler.create_region(
    pad_value=50, pad_type="Percentage Offset", name="Region"
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
# Create a linear count sweep where the parameter to sweep is ``"relative_cs_origin_z"``.
# The collector positions is changed at each step to see how the magnetic flux density on the polyline changes.
# Enable the saving fields option.

param_sweep = m3d.parametrics.add(
    variable="relative_cs_origin_z",
    start_point=m3d["relative_cs_origin_z"],
    end_point="-50mm",
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
    variations={"relative_cs_origin_z": "All"},
    context=line.name,
    polyline_points=101,
)

rectangular_plot = m3d.post.create_report(
    expressions="Mag_B",
    report_category="Fields",
    plot_type="Rectangular Plot",
    plot_name="Mag_B",
    variations={"relative_cs_origin_z": "All"},
    context=line.name,
    polyline_points=101,
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
