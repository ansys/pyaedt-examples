# # Component antenna array

# This example shows how to create an antenna array using 3D components for the unit
# cell definition. You will see how to set
# up the analysis, generates the EM solution, and post-process the solution data
# using Matplotlib and
# PyVista. This example runs only on Windows using CPython.
#
# Keywords: **HFSS**, **antenna array**, **3D components**, **far field**.

# ## Prerequisites
#
# ### Perform imports

# +
import os
import tempfile
import time

import pyvista as pv

from ansys.aedt.core import Hfss
from ansys.aedt.core.examples.downloads import download_3dcomponent
from ansys.aedt.core.generic import file_utils
from ansys.aedt.core.visualization.advanced.farfield_visualization import (
    FfdSolutionData,
)

from ansys.tools.visualization_interface.backends.pyvista import PyVistaBackend

pv.set_jupyter_backend("html")
# -

# ### Load far field data
#
# An instance of the ``FfdSolutionData`` class
# can be instantiated from the metadata file. Embedded element
# patterns and the exported array geometry are linked through the metadata file.

from pathlib import Path

metadata_file = Path(os.getcwd()) / "metadata" / "pyaedt_antenna_metadata.json"
ffdata = FfdSolutionData(input_file=str(metadata_file))
# -

# ### Generate 3D plot
#
# Use the array-aware far-field data returned by ``get_antenna_data()`` for the
# 3D visualization so that all array elements are rendered with the pattern.

is_doc_build = os.environ.get("PYAEDT_DOC_GENERATION", "0") == "1"
p = pv.Plotter(notebook=True, off_screen=is_doc_build)
ffdata.plot_3d(
    quantity="RealizedGain",
    show=False,
    pyvista_object=p,
)
p.show(jupyter_backend="html")
