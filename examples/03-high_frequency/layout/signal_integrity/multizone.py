# # Simulate multi-zone layout with SIwave
#
# This example demonstrates simulation of multiple zones with SIwave.
#
# Keywords: **Circuit**, **multi-zone**.

# ## Perform required imports
#
# Perform required imports, which includes importing a section.

# +
import os.path
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core import Circuit, Edb

# -

# ## Define constants

EDB_VERSION = "2024.2"

# ## Create temporary directory
#
# Create temporary directory.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download file
#
# Download the EDB folder.

edb_file = ansys.aedt.core.downloads.download_file(
    directory="edb/siwave_multi_zones.aedb", destination=temp_folder.name
)
work_folder = os.path.join(temp_folder.name, "work")
aedt_file = os.path.splitext(edb_file)[0] + ".aedt"
circuit_project_file = os.path.join(temp_folder.name, "multizone_clipped_circuit.aedt")
print(edb_file)


# ## AEDT version
#
# Sets the AEDT version.

edb_version = EDB_VERSION

# ## Ground net
#
# Common reference net used across all sub-designs, Mandatory for this work flow.

common_reference_net = "GND"

# ## Load the Project
#
# Load initial Edb file, checking if aedt file exists and remove to allow Edb loading.

if os.path.isfile(aedt_file):
    os.remove(aedt_file)
edb = Edb(edbversion=edb_version, edbpath=edb_file)

# ## Project zones
#
# Copy project zone into sub project.

edb_zones = edb.copy_zones(working_directory=work_folder)

# ## Split zones
#
# Clip sub-designs along with corresponding zone definition
# and create port of clipped signal traces.

defined_ports, project_connexions = edb.cutout_multizone_layout(
    edb_zones, common_reference_net
)

# ## Circuit
#
# Create circuit design, import all sub-project as EM model and connect
# all corresponding pins in circuit.

circuit = Circuit(version=edb_version, project=circuit_project_file)
circuit.connect_circuit_models_from_multi_zone_cutout(
    project_connections=project_connexions,
    edb_zones_dict=edb_zones,
    ports=defined_ports,
    model_inc=70,
)

# ## Setup
#
# Add Nexxim LNA simulation setup.

circuit_setup = circuit.create_setup("Pyedt_LNA")

# ## Frequency sweep
#
# Add frequency sweep from 0GHt to 20GHz with 10NHz frequency step.

circuit_setup.props["SweepDefinition"]["Data"] = "LIN {} {} {}".format(
    "0GHz", "20GHz", "10MHz"
)

# ## Start simulation
#
# Analyze all siwave projects and solves the circuit.

circuit.analyze()

# Define differential pairs

circuit.set_differential_pair(
    differential_mode="U0",
    assignment="U0.via_38.B2B_SIGP",
    reference="U0.via_39.B2B_SIGN",
)
circuit.set_differential_pair(
    differential_mode="U1",
    assignment="U1.via_32.B2B_SIGP",
    reference="U1.via_33.B2B_SIGN",
)

# Plot results

circuit.post.create_report(
    expressions=["dB(S(U0,U0))", "dB(S(U1,U0))"], context="Differential Pairs"
)

# ## Release AEDT
#
# Release AEDT and close the example.

circuit.save_project()
circuit.release_desktop()
# Wait 3 seconds to allow Electronics Desktop to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Cleanup
#
# All project files are saved in the folder ``temp_folder.name``. If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
