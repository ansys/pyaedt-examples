# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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


# # EDB: Rename nets and ports
#
# This example shows how you can use PyEDB to rename ports and nets.


# ## Perform required imports
# Perform required imports, which includes importing a section.

from pyedb import Edb
from pyedb.generic.general_methods import generate_unique_folder_name
import pyedb.misc.downloads as downloads

# ## Download ANSYS EDB
# Download ANSYS generic design from public repository.

temp_folder = generate_unique_folder_name()
targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)

# ## opening EDB
# Opening EDB with ANSYS release 2024.2

EDB_VERSION = "2024.2"
edbapp = Edb(edbpath=targetfile, edbversion=EDB_VERSION)

# ## Renaming all signal nets
# Using the net name setter to rename.

for net_name, net in edbapp.nets.signal.items():
    net.name = f"{net_name}_test"

# ## Creating coaxial port on component U1 and all ddr4_dqs nets
# Selecting all nets from ddr4_dqs and component U1 and create coaxial ports
# On corresponding pins.

comp_u1 = edbapp.components.instances["U1"]
signal_nets = [net for net in comp_u1.nets if "ddr4_dqs" in net.lower()]
edbapp.hfss.create_coax_port_on_component("U1", net_list=signal_nets)
edbapp.components.set_solder_ball(component="U1", sball_diam="0.3mm", sball_height="0.3mm")

# ## Renaming all ports
# Renaming all port with _renamed string as suffix example.

for port_name, port in edbapp.ports.items():
    port.name = f"{port_name}_renamed"

# ## Saving and closing EDB
# Once the EDB saved and closed, this can be imported in ANSYS AEDT as an HFSS 3D Layout project.

edbapp.save()
edbapp.close()
