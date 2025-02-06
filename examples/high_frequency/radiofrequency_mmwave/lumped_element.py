# # Lumped element filter design
#
# This example shows how to use PyAEDT to use the ``FilterSolutions`` module to design and
# visualize the frequency response of a band-pass Butterworth filter.
#
# Keywords: **filter solutions**

# ## Perform imports and define constants
#
# Perform required imports.

import ansys.aedt.core
import matplotlib.pyplot as plt
from ansys.aedt.core.filtersolutions_core.attributes import (
    FilterClass, FilterImplementation, FilterType)
from ansys.aedt.core.filtersolutions_core.ideal_response import \
    FrequencyResponseColumn

# Define constants.

AEDT_VERSION = "2025.1"

# ## Define function used for plotting
#
# Define formal plot function.


def format_plot():
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude S21 (dB)")
    plt.title("Ideal Frequency Response")
    plt.xscale("log")
    plt.legend()
    plt.grid()


# ## Create lumped filter design
#
# Create a lumped element filter design and assign the class, type, frequency, and order.

design = ansys.aedt.core.FilterSolutions(
    version=AEDT_VERSION, implementation_type=FilterImplementation.LUMPED
)
design.attributes.filter_class = FilterClass.BAND_PASS
design.attributes.filter_type = FilterType.BUTTERWORTH
design.attributes.pass_band_center_frequency = "1G"
design.attributes.pass_band_width_frequency = "500M"
design.attributes.filter_order = 5

# ## Plot frequency response of filter
#
# Plot the frequency response of the filter without any transmission zeros.

freq, mag_db = design.ideal_response.frequency_response(
    FrequencyResponseColumn.MAGNITUDE_DB
)
plt.plot(freq, mag_db, linewidth=2.0, label="Without Tx Zero")
format_plot()
plt.show()

# ## Add a transmission zero to filter design
#
# Add a transmission zero that yields nulls separated by two times the pass band width (1 GHz).
# Plot the frequency response of the filter with the transmission zero.

design.transmission_zeros_ratio.append_row("2.0")
freq_with_zero, mag_db_with_zero = design.ideal_response.frequency_response(
    FrequencyResponseColumn.MAGNITUDE_DB
)
plt.plot(freq, mag_db, linewidth=2.0, label="Without Tx Zero")
plt.plot(freq_with_zero, mag_db_with_zero, linewidth=2.0, label="With Tx Zero")
format_plot()
plt.show()

# ## Generate netlist for designed filter
#
# Generate and print the netlist for the designed filter with the added transmission zero to
# the filter.

netlist = design.topology.circuit_response()
print("Netlist: \n", netlist)
