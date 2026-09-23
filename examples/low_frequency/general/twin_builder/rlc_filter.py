# # RLC filter circuit design analysis
#
# This example demonstrates how to use PyAEDT to set up and analyze an RLC filter circuit in Twin Builder.
# It covers setup creation, parametric sweeps of key circuit parameters, and post-processing of simulation results.
# Generated plots illustrate how the parametric sweep affects the circuit response.
# Key behaviors such as resonance peaking, damping, and current flow under different resistance values are examined.
#
# Keywords: **Twin Builder**, **RLC**.

# +
import os
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_file

# -

# ## Define constants
#
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2026.1"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.
TB_DESIGN_NAME = "_"

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download AEDT file
#
# Set the local temporary folder to export the AEDT file to.

project_path = download_file(
    source="_",
    name="_.aedt",
    local_path=temp_folder.name,
)

# ## Launch Twinbuilder AEDT
#
# Create an instance of the ``Twinbuilder`` class.
# The Ansys Electronics Desktop will be launched with the active Twinbuilder design.
# The ``tb`` object is subsequently used to create and simulate the model.

tb = ansys.aedt.core.TwinBuilder(
    project=project_path,
    design=TB_DESIGN_NAME,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Analysis setup
#
# Create a transient setup.
# If ``setup_type`` is not specified, the default setup type is used (Transient).

setup = tb.create_setup()

# Change setup properties to specify the stop time, minimum time step, and maximum time step.
# In the order: Stop Time, Min time step, Max time step.

setup.props["TransientData"][0] = "10ms"
setup.props["TransientData"][1] = "1us"
setup.props["TransientData"][2] = "20us"
setup.update()

# Parametric sweep
#
# Create a parametric sweep for the RLC filter circuit.
# The sweep varies the series resistance, series inductance, and drive voltage.

sweep = tb.parametrics.add(
    variable="$Rseries",
    start_point=25,
    end_point=100,
    step=4,
    variation_type="LinearCount",
)
sweep.add_variation(
    sweep_variable="$Lseries",
    start_point=5,
    end_point=20,
    step=4,
    variation_type="LinearCount",
)
sweep.add_variation(
    sweep_variable="$Vdrive",
    start_point=1,
    end_point=10,
    step=4,
    variation_type="LinearCount",
)

#TEST

setup.analyze()
#sweep.analyze()

