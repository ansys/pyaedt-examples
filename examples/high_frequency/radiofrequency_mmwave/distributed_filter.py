# # distributed filter design
#
# This example demonstrates how to use the ``FilterSolutions`` module of the PyAEDT package 
# to design and export a band-pass Butterworth filter with ring resonator topology to HFSS.
#
# Keywords: **filter solutions**

# ## Perform imports and define constants
#
# Perform required imports.


import ansys.aedt.core
import ansys.aedt.core.filtersolutions
from ansys.aedt.core.filtersolutions_core.attributes import FilterType, FilterClass
from ansys.aedt.core.filtersolutions_core.distributed_topology import TopologyType, TapPosition
from ansys.aedt.core.filtersolutions_core.distributed_substrate import SubstrateType
from ansys.aedt.core.filtersolutions_core.distributed_substrate import SubstrateEr, SubstrateResistivity
from ansys.aedt.core.filtersolutions_core.export_to_aedt import ExportFormat


# Define constants.

AEDT_VERSION = "2025.2"


# ## Create distributed filter design
#
# Create a distributed filter design and assign the class, type, frequency, and order.

distributed_design = ansys.aedt.core.filtersolutions.DistributedDesign(version=AEDT_VERSION)
distributed_design.attributes.filter_class = FilterClass.BAND_PASS
distributed_design.attributes.filter_type = FilterType.ELLIPTIC
distributed_design.attributes.pass_band_center_frequency = "3GHz"
distributed_design.attributes.pass_band_width_frequency = "400MHz"
distributed_design.attributes.filter_order = 6


# ## Define frequency range of filter
#
# Define the frequency range of the filter between 2GHz to 4GHz to ensure that the 
# filter operates within the desired frequency band.

distributed_design.graph_setup.minimum_frequency = "2GHz"
distributed_design.graph_setup.maximum_frequency = "4GHz"

# ## Define topology of filter
#
# Select the Ring Resonator topology from the available topology list and configure its parameters.  
# This includes defining key properties such as resonator dimensions, coupling gaps, and substrate  
# characteristics to achieve the desired band-pass filtering performance.  

distributed_design.topology = TopologyType.RING_RESONATOR
distributed_design.topology.tap_position = TapPosition.BACK
distributed_design.topology.mitered_corners = True
distributed_design.topology.resonator_line_width = "1mm"
distributed_design.topology.resonator_gap_width = "300um"

# ## Define substrtate parameters of filter
#

# Select the appropriate filter substrate type and configure its associated parameters,  
# such as dielectric constant, thickness, and loss tangent, to ensure optimal performance.

distributed_design.substrate.substrate_type = SubstrateType.MICROSTRIP
distributed_design.substrate.substrate_er = SubstrateEr.GERMANIUM
distributed_design.substrate.substrate_resistivity = SubstrateResistivity.COPPER
distributed_design.substrate.substrate_conductor_thickness = "3um"
distributed_design.substrate.substrate_dielectric_height = "1mm"

# ## Export lumped element model of the filter to HFSS
#
# Export the designed filter with the added transmission zero to
# HFSS with the defined export parameters.

distributed_design.export_to_aedt.schematic_name = "DistributedFilter"
distributed_design.export_to_aedt.simulate_after_export_enabled = True
distributed_design.export_to_aedt.smith_plot_enabled = True
distributed_design.export_to_aedt.table_data_enabled = True
distributed_design.export_to_aedt.export_design(export_format=ExportFormat.DIRECT_TO_AEDT)

# <img src="_static/distributed_filter_export_to_desktop.png" width="400">