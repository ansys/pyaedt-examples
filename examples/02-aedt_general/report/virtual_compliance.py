# # PCIE virtual compliance
#
# This example shows how to generate a compliance report in PyAEDT using
# the ``VirtualCompliance`` class.
#
# Keywords: **Circuit**, **Automatic report**, **virtual compliance**.


# ## Perform imports and define constants
# Import the required packages.

import os.path
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.generic.compliance import VirtualCompliance

# ## Define constants

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored. In this example, the temporary directory
# in where the example is stored and simulation data is saved.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download example data

download_folder = ansys.aedt.core.downloads.download_file(
    source="pcie_compliance", destination=temp_folder.name
)
project_folder = os.path.join(download_folder, "project")
project_path = os.path.join(project_folder, "PCIE_GEN5_only_layout.aedtz")

# ## Launch AEDT and solve layout
#
# Open the HFSS 3D Layout project and analyze it using the SIwave solver.
# Before solving, this code ensures that the model is solved from DC to 70GHz and that
# causality and passivity are enforced.

h3d = ansys.aedt.core.Hfss3dLayout(project_path)
h3d.remove_all_unused_definitions()
h3d.edit_cosim_options(simulate_missing_solution=False)
h3d.setups[0].sweeps[0].props["EnforcePassivity"] = True
h3d.setups[0].sweeps[0].props["Sweeps"]["Data"] = "LIN 0MHz 70GHz 0.1GHz"
h3d.setups[0].sweeps[0].props["EnforceCausality"] = True
h3d.setups[0].sweeps[0].update()
h3d.analyze(cores=NUM_CORES)
h3d = ansys.aedt.core.Hfss3dLayout(version=242)
touchstone_path = h3d.export_touchstone()

# ## Create LNA project
#
# Use the LNA (linear network analysis) setup to retrieve Touchstone files
# and generate frequency domain reports.

circuit = ansys.aedt.core.Circuit(project=h3d.project_name, design="Touchstone")
status, diff_pairs, comm_pairs = circuit.create_lna_schematic_from_snp(
    input_file=touchstone_path,
    start_frequency=0,
    stop_frequency=70,
    auto_assign_diff_pairs=True,
    separation=".",
    pattern=["component", "pin", "net"],
    analyze=True,
)
insertion = circuit.get_all_insertion_loss_list(
    drivers=diff_pairs,
    receivers=diff_pairs,
    drivers_prefix_name="X1",
    receivers_prefix_name="U1",
    math_formula="dB",
    nets=["RX0", "RX1", "RX2", "RX3"],
)
return_diff = circuit.get_all_return_loss_list(
    excitations=diff_pairs,
    excitation_name_prefix="X1",
    math_formula="dB",
    nets=["RX0", "RX1", "RX2", "RX3"],
)
return_comm = circuit.get_all_return_loss_list(
    excitations=comm_pairs,
    excitation_name_prefix="COMMON_X1",
    math_formula="dB",
    nets=["RX0", "RX1", "RX2", "RX3"],
)

# ## Create TDR project
#
# Create a TDR project to compute transient simulation and retrieve
# the TDR measurement on a differential pair.
# The original circuit schematic is duplicated and modified to achieve this target.

result, tdr_probe_name = circuit.create_tdr_schematic_from_snp(
    input_file=touchstone_path,
    tx_schematic_pins=["X1.A2.PCIe_Gen4_RX0_P"],
    tx_schematic_differential_pins=["X1.A3.PCIe_Gen4_RX0_N"],
    termination_pins=["U1.AP26.PCIe_Gen4_RX0_P", "U1.AN26.PCIe_Gen4_RX0_N"],
    differential=True,
    rise_time=35,
    use_convolution=True,
    analyze=True,
    design_name="TDR",
)

# ## Create AMI project
#
# Create an Ibis AMI project to compute an eye diagram simulation and retrieve
# eye mask violations.

_, eye_curve_tx, eye_curve_rx = circuit.create_ami_schematic_from_snp(
    input_file=touchstone_path,
    ibis_tx_file=os.path.join(project_folder, "models", "pcieg5_32gt.ibs"),
    tx_buffer_name="1p",
    rx_buffer_name="2p",
    tx_schematic_pins=["U1.AM25.PCIe_Gen4_TX0_CAP_P"],
    rx_schematic_pins=["X1.B2.PCIe_Gen4_TX0_P"],
    tx_schematic_differential_pins=["U1.AL25.PCIe_Gen4_TX0_CAP_N"],
    rx_schematic_differentialial_pins=["X1.B3.PCIe_Gen4_TX0_N"],
    ibis_tx_component_name="Spec_Model",
    use_ibis_buffer=False,
    differential=True,
    bit_pattern="random_bit_count=2.5e3 random_seed=1",
    unit_interval="31.25ps",
    use_convolution=True,
    analyze=True,
    design_name="AMI",
)

circuit.save_project()

# ## Create virtual compliance report
#
# Initialize the ``VirtualCompliance`` class
# and set up the main project information needed to generate the report.
#

# <img src="_static/virtual_compliance_class.png" width="500">

# <img src="_static/virtual_compliance_configs.png" width="500">

template = os.path.join(download_folder, "pcie_gen5_templates", "main.json")

v = VirtualCompliance(circuit.desktop_class, str(template))

# ## Customize project and design
#
# Define the path to the project file and the
# design names to be used in each report generation.
#
# <img src=" _static/virtual_compliance_usage.png" width="400">

v.project_file = circuit.project_file
v.reports["insertion losses"].design_name = "LNA"
v.reports["return losses"].design_name = "LNA"
v.reports["common mode return losses"].design_name = "LNA"
v.reports["tdr from circuit"].design_name = "TDR"
v.reports["eye1"].design_name = "AMI"
v.reports["eye3"].design_name = "AMI"
v.parameters["erl"].design_name = "LNA"
v.specs_folder = os.path.join(download_folder, "readme_pictures")

# ## Define trace names
#
# Change the trace name with projects and users.
# Reuse the compliance template and update traces accordingly.

v.reports["insertion losses"].traces = insertion

v.reports["return losses"].traces = return_diff

v.reports["common mode return losses"].traces = return_comm

v.reports["eye1"].traces = eye_curve_tx
v.reports["eye3"].traces = eye_curve_tx
v.reports["tdr from circuit"].traces = tdr_probe_name
v.parameters["erl"].trace_pins = [
    [
        "X1.A5.PCIe_Gen4_RX1_P",
        "X1.A6.PCIe_Gen4_RX1_N",
        "U1.AR25.PCIe_Gen4_RX1_P",
        "U1.AP25.PCIe_Gen4_RX1_N",
    ],
    [7, 8, 18, 17],
]

# ## Generate PDF report
#
# Generate the reports and produce a PDF report.
#
# <img src="_static/virtual_compliance_scattering1.png" width="400">
# <img src="_static/virtual_compliance_scattering2.png" width="400">
# <img src="_static/virtual_compliance_eye.png" width="400">

v.create_compliance_report()

# ## Release AEDT

h3d.save_project()
h3d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
