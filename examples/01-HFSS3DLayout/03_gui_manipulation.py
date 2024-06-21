# # HFSS 3D Layout UI
#
# This example shows how to modify the 3D Layout user interface.

# # Preparation
# Import required packages

# +
import time
import tempfile
from pyaedt import Hfss3dLayout
from pyaedt.downloads import download_file
try:
    from ansys.pyaedt.examples.constants import AEDT_VERSION
except:
    AEDT_VERSION = "2024.1"

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
# -

# Set ``NG_MODE`` to ``True`` in order to run in non-graphical mode. The example is currently set up to run in graphical mode.

NG_MODE = False

# Download example board.

aedb = download_file(
    source="edb/ANSYS-HSD_V1.aedb", destination=temp_folder.name
)

# ## Launch HFSS 3D Layout
#
# Initialize AEDT and launch HFSS 3D Layout.

h3d = Hfss3dLayout(aedb, version=AEDT_VERSION)
h3d.save_project()

# ## Net visibility
# Hide all nets.

h3d.modeler.change_net_visibility(visible=False)

# Show two specified nets.

h3d.modeler.change_net_visibility(["5V", "1V0"], visible=True)

# Show all layers.

for layer in h3d.modeler.layers.all_signal_layers:
    layer.is_visible = True

# Change the layer color.

layer = h3d.modeler.layers.layers[h3d.modeler.layers.layer_id("1_Top")]
layer.set_layer_color(0, 255, 0)
h3d.modeler.fit_all()

# ## Disable component visibility

# Disable component visibility for ``"1_Top"`` and ``"16_Bottom"`` layers.

top = h3d.modeler.layers.layers[h3d.modeler.layers.layer_id("1_Top")]
top.is_visible_component = False

bot = h3d.modeler.layers.layers[h3d.modeler.layers.layer_id("16_Bottom")]
bot.is_visible_component = False

# ## Display the Layout
#
# Fit all so that you can visualize all.

h3d.modeler.fit_all()

# ## Close AEDT

h3d.close_project(save_project=True)

# ## Cleanup
#
# All project files are saved in the folder ``temp_file.dir``. If you've run this example as a Jupyter notbook you 
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

time.sleep(3)
temp_folder.cleanup()
