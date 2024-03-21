# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Constants used in PyAEDT examples.
"""

AEDT_VERSION = "2024.1"
EDB_VERSION = "2024.1"
NUM_CORES = 4

HEADER = """# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE."""

EDB_PREAMBLE = """# This example shows how you can use EDB to create a layout.
# ## Final expected project
#
# <img src="_static/diff_via.png" width="500">"""

EDB_IMPORTS = """
# +
import os
import tempfile

from ansys.pyaedt.examples.constants import EDB_VERSION
from pyedb import Edb
# -"""

EDB_TMP_DIR = r"""# Create and return a temporary directory
temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
print(f"Temporary directory created at {temp_dir.name}")"""

EDB_APP_SETUP = r"""# +
aedb_path = os.path.join(temp_dir.name, "create_via.aedb")
print(f"Path used to save the AEDB file: {aedb_path}")

edb = Edb(edbpath=aedb_path, edbversion=edb_version)
# -"""

EDB_PROCESSING = """# ## Add stackup layers
# A stackup can be created layer by layer or imported from a CSV file or XML file.

edb.stackup.add_layer("GND")
edb.stackup.add_layer(
    "Diel", "GND", layer_type="dielectric", thickness="0.1mm", material="FR4_epoxy"
)
edb.stackup.add_layer("TOP", "Diel", thickness="0.05mm")

# ## Create signal net and ground planes

points = [[0.0, 0], [100e-3, 0.0]]
edb.modeler.create_trace(points, "TOP", width=1e-3)
points = [[0.0, 1e-3], [0.0, 10e-3], [100e-3, 10e-3], [100e-3, 1e-3], [0.0, 1e-3]]
edb.modeler.create_polygon(points, "TOP")
points = [[0.0, -1e-3], [0.0, -10e-3], [100e-3, -10e-3], [100e-3, -1e-3], [0.0, -1e-3]]
edb.modeler.create_polygon(points, "TOP")

# ## Create vias with parametric positions

edb.padstacks.create("MyVia")
edb.padstacks.place([5e-3, 5e-3], "MyVia")
edb.padstacks.place([15e-3, 5e-3], "MyVia")
edb.padstacks.place([35e-3, 5e-3], "MyVia")
edb.padstacks.place([45e-3, 5e-3], "MyVia")
edb.padstacks.place([5e-3, -5e-3], "MyVia")
edb.padstacks.place([15e-3, -5e-3], "MyVia")
edb.padstacks.place([35e-3, -5e-3], "MyVia")
edb.padstacks.place([45e-3, -5e-3], "MyVia")

# ## Generate geometry plot

edb.nets.plot(None, color_by_net=True)

# ## Generate stackup plot

edb.stackup.plot(plot_definitions="MyVia")"""
