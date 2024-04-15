# # EDB: Power Integrity Analysis
# This example shows how to configure EDB for power integrity analysis, and load EDB into HFSS 3D Layout for analysis
# and post-processing.

# # Preparation
# Import required packages
# +
import os
import tempfile
from pyedb import Edb
from pyedb.misc.downloads import download_file

VERSION = "2024.1"
# -

# Download example board.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

aedb = download_file(
    directory="edb/ANSYS-HSD_V1.aedb", destination=temp_folder.name
)

download_file(
    directory="touchstone", filename="GRM32_DC0V_25degC_series.s2p", destination=temp_folder.name
)

edbapp = Edb(aedb, edbversion=VERSION)

# # Change via hole size and plating thickness

pdef = edbapp.padstacks.definitions["v35h15"]
pdef.hole_diameter = "0.2mm"
pdef.hole_plating_thickness = "25um"

# # Assign S-parameter to capactitors.
# In this example, "GRM32_DC0V_25degC_series.s2p" is assigned to C3 and C4, which share the same component part number.
# When "apply_to_all": True, all components share part number "CAPC3216X180X20ML20" will be assigned the S-parameter. In this case, "components" becomes exceptional li

comp_def = edbapp.definitions.component["CAPC0603X33X15LL03T05"]
comp_def.add_n_port_model(
    fpath=os.path.join(temp_folder.name, "touchstone", "GRM32_DC0V_25degC_series.s2p"),
    name="GRM32_DC0V_25degC_series")
comp_def.components["C206"].use_s_parameter_model(name="GRM32_DC0V_25degC_series", reference_net="GND")
comp_def.components["C110"].use_s_parameter_model(name="GRM32_DC0V_25degC_series", reference_net="GND")

# ## Create pin groups.
# In this example, the listed pins on component U2 are groups in two pin groups. Alternatively, use "net": "GND" to group all pins connected to net "GND".
_, pin_group_1 = edbapp.siwave.create_pin_group(
    reference_designator="U1",
    pin_numbers=["AD14", "AD15", "AD16", "AD17"],
    group_name="PIN_GROUP_1"
)
_, pin_group_2 = edbapp.siwave.create_pin_group_on_net(
    reference_designator="U1",
    net_name="GND",
    group_name="PIN_GROUP_2"
)

# # Create ports
# Create a circuit port between the two pin groups just created.

positive_terminal = pin_group_1.get_terminal(name="port1", create_new_terminal=True)
negative_terminal = pin_group_2.get_terminal(create_new_terminal=True)
edbapp.create_port(
    terminal=positive_terminal,
    ref_terminal=negative_terminal,
    is_circuit_port=True
)

# # Create SIwave DC analysis

setup = edbapp.create_siwave_syz_setup("siwave_syz")
setup.pi_slider_position = 1
setup.add_frequency_sweep(
    frequency_sweep=[
        ["log scale", "1MHz", "1GHz", 20],
    ]
)

# # Do cutout

edbapp.cutout(
    signal_list=["1V0"],
    reference_list=["GND"],
    extent_type="ConvexHull",
    expansion_size=0.002,
    use_round_corner=False,
    output_aedb_path="",
    open_cutout_at_end=True,
    use_pyaedt_cutout=True,
    number_of_threads=4,
    use_pyaedt_extent_computing=True,
    extent_defeature=0,
    remove_single_pin_components=False,
    custom_extent="",
    custom_extent_units="mm",
    include_partial_instances=False,
    keep_voids=True,
    check_terminals=False,
    include_pingroups=False,
    expansion_factor=0,
    maximum_iterations=10,
    preserve_components_with_model=False,
    simple_pad_check=True,
    keep_lines_as_path=False
)

# Load configuration from JSON

edbapp.save()
edbapp.close()

# The configured EDB file is saved in a temp folder.

print(temp_folder.name)

# All above can be achieved by Edb.configuration.load() too. Please refer to HFSS 3DLayout example 01_power_integrity
