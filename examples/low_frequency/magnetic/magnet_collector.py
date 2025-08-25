# ## Prerequisites
#
# ### Perform imports

# +
import tempfile

import ansys.aedt.core  # Interface to Ansys Electronics Desktop
from ansys.aedt.core.examples.downloads import download_file

# -

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.1"
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

# ### Launch Maxwell 2d
#
# Create an instance of
# the ``Maxwell2d`` class. The Ansys Electronics Desktop will be launched
# with an active Maxwell2D design. The ``m2d`` object is subsequently
# used to
# create and simulate the actuator model.

m3d = ansys.aedt.core.Maxwell3d(
    project="magnet_collector",
    solution_type="MagnetostaticZ",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Add materials
#
# Create custom material ``"Aimant"``.

mat = m3d.materials.add_material("Aimant")
mat.permeability = "1.1"
mat.set_magnetic_coercivity(value=2005600, x=1, y=1, z=1)
mat.update()

# Create custom material ``"Iron"``.

mat = m3d.materials.add_material("Iron")
mat.permeability = "NONLINEAR - BH CURVE"
mat.set_magnetic_coercivity(value=0, x=1, y=0, z=0)

# ## Import geometry as a STEP file
#
# You can test importing a STEP or a Parasolid file by changing the source argument
# in the ``download_file`` method.
# Both file formats are available to download.

# TO CHECK IF BOTH STEP AND PARASOLID FILES ARE AVAILABLE AND HOW TO PLACE COMPONENTS IN THE DESIGN
collector_path = download_file(
    source="step", name="[].step", local_path=temp_folder.name
)
m3d.modeler.import_3d_cad(collector_path)

# ## Define variables
#
# Later on we want to see how the magnetic flux density changes with the position of the collector.
# Define the collector position along the Z direction as a variable.

m3d["collector_z_pos"] = "5mm"
m3d["magnet_radius"] = "2mm"
m3d["magnet_height"] = "8mm"
m3d["polyline_z_pos"] = "-50mm"

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
    material="TO_ADD",
)

# ## Create a polyline
#
# Create a polyline to plot the field onto.

line = m3d.modeler.create_polyline(
    points=[[0, 0, 0], [0, 0, "polyline_z_pos"]], name="line"
)
