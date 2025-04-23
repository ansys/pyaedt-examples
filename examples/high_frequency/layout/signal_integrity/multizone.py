# # Multi-zone simulation with SIwave
#
# This example shows how to simulate multiple zones with SIwave.
#
# Keywords: **Circuit**, **multi-zone**.

# ## Perform imports and define constants
#
# Perform required imports, which includes importing a section.

# +
import os.path
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core import Circuit, Edb
from ansys.aedt.core.examples.downloads import download_file
# -

# Define constants.

EDB_VERSION = "2025.1"

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download EDB folder

edb_file = download_file(
    source="edb/siwave_multi_zones.aedb", local_path=temp_folder.name
)
work_folder = os.path.join(temp_folder.name, "work")
aedt_file = os.path.splitext(edb_file)[0] + ".aedt"
circuit_project_file = os.path.join(temp_folder.name, "multizone_clipped_circuit.aedt")
print(edb_file)


# ## Set AEDT version


edb_version = EDB_VERSION

# ## Define ground net
#
# Define the common reference net used across all subdesigns, which is mandatory for this workflow.

common_reference_net = "GND"

# ## Load project
#
# Check if the AEDT file exists and remove it to allow EDB loading. Then, load the initial EDB file.

if os.path.isfile(aedt_file):
    os.remove(aedt_file)
edb = Edb(edbversion=edb_version, edbpath=edb_file)

# ## Copy project zones
#
# Copy project zone into the subproject.

edb_zones = edb.copy_zones(working_directory=work_folder)

# ## Split zones
#
# Clip subdesigns along with corresponding zone definitions
# and create a port of clipped signal traces.

defined_ports, project_connexions = edb.cutout_multizone_layout(
    edb_zones, common_reference_net
)

# ## Create circuit
#
# Create circuit design, import all subprojects as EM models, and connect
# all corresponding pins in the circuit.

circuit = Circuit(version=edb_version, project=circuit_project_file)
circuit.connect_circuit_models_from_multi_zone_cutout(
    project_connections=project_connexions,
    edb_zones_dict=edb_zones,
    ports=defined_ports,
    model_inc=70,
)

# ## Set up simulation
#
# Add Nexxim LNA simulation setup.

circuit_setup = circuit.create_setup("Pyedt_LNA")

# ## Add frequency sweep
#
# Add a frequency sweep from 0 GHt to 20 GHz with a 10 NHz frequency step.

circuit_setup.props["SweepDefinition"]["Data"] = "LIN {} {} {}".format(
    "0GHz", "20GHz", "10MHz"
)

# ## Start simulation
#
# Analyze all SIwave projects and solve the circuit. Uncomment the following line to run the analysis.

# circuit.analyze()

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

# Plot results.

circuit.post.create_report(
    expressions=["dB(S(U0,U0))", "dB(S(U1,U0))"], context="Differential Pairs"
)

# ## Release AEDT
#
# Release AEDT and close the example.

circuit.save_project()
circuit.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``. If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
