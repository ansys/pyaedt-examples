# # Maxwell 3D: Busbar mechanical analysis
#
# This example uses PyAEDT and pymechanical to set up the a busbar force analysis

# ## Perform required imports
#
# Perform required imports.

import tempfile

from ansys.pyaedt.examples.constants import AEDT_VERSION
from pyaedt import Maxwell3d

# ## Create temporary directory
#
# Create temporary directory.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Set non-graphical mode
#
# Set non-graphical mode.
# You can set ``non_graphical`` either to ``True`` or ``False``.

non_graphical = False

# ## Launch AEDT and Maxwell 3D
#
# Launch AEDT and Maxwell 3D. The following code sets up the project,
# design names, the solver, and the version.
# It also creates an instance of the ``Maxwell3d`` class named ``m3d``.

# +
project_name = "Busbars"
design_name = "1 Maxwell transient"
solver = "Transient"
desktop_version = AEDT_VERSION

m3d = Maxwell3d(
    projectname=project_name,
    designname=design_name,
    solution_type=solver,
    specified_version=desktop_version,
    non_graphical=non_graphical,
    new_desktop_session=True,
)
m3d.modeler.model_units = "mm"

# -

# ## Add Maxwell 3D setup
#
# Add a Maxwell 3D transient setup

# +
dc_freq = 0.1
stop_freq = 50

setup = m3d.create_setup(setupname="Setup1")
setup.props["StopTime"] = "40ms"
setup.props["TimeStep"] = "1ms"

# -
bar1 = m3d.modeler.create_box(
    position=[0, 0, 0], dimensions_list=[5, 20, 1], matname="copper", name="bar1"
)

bar2 = m3d.modeler.create_box(
    position=[0, 0, 5], dimensions_list=[5, 20, 1], matname="copper", name="bar2"
)

m3d.modeler.create_region(pad_percent=[300, 0, 300])

m3d.enable_harmonic_force([bar1, bar2])
terminals = bar1.faces_on_bounding_box
m3d.assign_coil(terminals)

m3d.assign_winding()
