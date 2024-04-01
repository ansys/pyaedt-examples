# # Circuit: AMI PostProcessing
#
# This example demonstartes advanced postprocessing of AMI simulations.

# <img src='_static/spectrum_plot.png' width="500">

# ## Perform required imports
#
# Perform required imports. Note that [Numpy](https://numpy.org/) 
# and [Matplotlib](https://matplotlib.org/) are required to run this example.

# +
import os
import tempfile

from ansys.pyaedt.examples.constants import AEDT_VERSION
from matplotlib import pyplot as plt
import numpy as np
import pyaedt
# -

# ## Download Example Data
#
# The ``download_file()`` method retrieves example
# data from the PyAnsys 
# [example-data](https://github.com/ansys/example-data/tree/master/pyaedt) repository.
#
# - The fist argument is the folder name where
#   the example files are located in the GitHub repository.
# - The 2nd argument is the file to retrieve.
# - The 3rd argument is the destination folder.
#
# Files are placed in the destination folder.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
project_path = pyaedt.downloads.download_file("ami", filename="ami_usb.aedtz", destintion=temp_dir.name)

# ## Launch AEDT
#
# Launch AEDT in graphical mode. This example uses SI units.

desktopVersion = AEDT_VERSION

# ## Set non-graphical mode
#
# Set non-graphical mode.
# You can set ``non_graphical`` either to ``True`` or ``False``.
# The Boolean parameter ``new_thread`` defines whether to create a new instance
# of AEDT or try to connect to an existing instance of it.

non_graphical = False
NewThread = True

# ## Launch AEDT with Circuit and enable Pandas as the output format
#
# All outputs obtained with the `get_solution_data` method will have the 
# [Pandas](https://pandas.pydata.org/docs/user_guide/index.html) format.
# Launch AEDT with Circuit. The `pyaedt.Desktop` class initializes AEDT
# and starts the specified version in the specified mode.

pyaedt.settings.enable_pandas_output = True
cir = pyaedt.Circuit(
    projectname=os.path.join(project_path),
    non_graphical=non_graphical,
    specified_version=desktopVersion,
    new_desktop_session=NewThread,
)

# ## Solve AMI setup
#
# Solve the transient setup.

cir.analyze()

# ## Get AMI report
#
# Get AMI report data

plot_name = "WaveAfterProbe<b_input_43.int_ami_rx>"
cir.solution_type = "NexximAMI"
original_data = cir.post.get_solution_data(
    expressions=plot_name,
    setup_sweep_name="AMIAnalysis",
    domain="Time",
    variations=cir.available_variations.nominal,
)
original_data_value = original_data.full_matrix_real_imag[0]
original_data_sweep = original_data.primary_sweep_values
print(original_data_value)

# ## Plot data
#
# Create a plot based on solution data.

fig = original_data.plot()

# ## Extract Wave Form
#
# Use the _WaveAfterProbe_ plot type to extract the
# waveform using an AMI receiver clock probe.
# The signal is extracted at a specific clock
# flank with additional half unit interval.

probe_name = "b_input_43"
source_name = "b_output4_42"
plot_type = "WaveAfterProbe"
setup_name = "AMIAnalysis"
ignore_bits = 100
unit_interval = 0.1e-9
sample_waveform = cir.post.sample_ami_waveform(
    setupname=setup_name,
    probe_name=probe_name,
    source_name=source_name,
    variation_list_w_value=cir.available_variations.nominal,
    unit_interval=unit_interval,
    ignore_bits=ignore_bits,
    plot_type=plot_type,
)

# ## Plot waveform and samples
#
# Create the plot from a start time to stop time in seconds

# +
tstop = 55e-9
tstart = 50e-9
scale_time = pyaedt.constants.unit_converter(
    1, unit_system="Time", input_units="s", output_units=original_data.units_sweeps["Time"]
)
scale_data = pyaedt.constants.unit_converter(
    1, unit_system="Voltage", input_units="V", output_units=original_data.units_data[plot_name]
)

tstop_ns = scale_time * tstop
tstart_ns = scale_time * tstart

for time in original_data_value[plot_name].index:
    if tstart_ns <= time[0]:
        start_index_original_data = time[0]
        break
for time in original_data_value[plot_name][start_index_original_data:].index:
    if time[0] >= tstop_ns:
        stop_index_original_data = time[0]
        break
for time in sample_waveform[0].index:
    if tstart <= time:
        sample_index = sample_waveform[0].index == time
        start_index_waveform = sample_index.tolist().index(True)
        break
for time in sample_waveform[0].index:
    if time >= tstop:
        sample_index = sample_waveform[0].index == time
        stop_index_waveform = sample_index.tolist().index(True)
        break

original_data_zoom = original_data_value[start_index_original_data:stop_index_original_data]
sampled_data_zoom = sample_waveform[0].values[start_index_waveform:stop_index_waveform] * scale_data
sampled_time_zoom = sample_waveform[0].index[start_index_waveform:stop_index_waveform] * scale_time

fig, ax = plt.subplots()
ax.plot(sampled_time_zoom, sampled_data_zoom, "r*")
ax.plot(np.array(list(original_data_zoom.index.values)), original_data_zoom.values, color="blue")
ax.set_title("WaveAfterProbe")
ax.set_xlabel(original_data.units_sweeps["Time"])
ax.set_ylabel(original_data.units_data[plot_name])
plt.show()
# -

# ## Plot Slicer Scatter
#
# Create the plot from a start time to stop time in seconds

fig, ax2 = plt.subplots()
ax2.plot(sample_waveform[0].index, sample_waveform[0].values, "r*")
ax2.set_title("Slicer Scatter: WaveAfterProbe")
ax2.set_xlabel("s")
ax2.set_ylabel("V")
plt.show()

# ## Plot Scatter Histogram
#
# Create the plot from a start time to stop time in seconds.

fig, ax4 = plt.subplots()
ax4.set_title("Slicer Histogram: WaveAfterProbe")
ax4.hist(sample_waveform[0].values, orientation="horizontal")
ax4.set_ylabel("V")
ax4.grid()
plt.show()

# ## Transient Report
#
# Get Transient report data

plot_name = "V(b_input_43.int_ami_rx.eye_probe.out)"
cir.solution_type = "NexximTransient"
original_data = cir.post.get_solution_data(
    expressions=plot_name,
    setup_sweep_name="NexximTransient",
    domain="Time",
    variations=cir.available_variations.nominal,
)

# ## Sample Waveform
#
# Extract waveform at specific clock time plus half unit interval.

# +
original_data.enable_pandas_output = False
original_data_value = original_data.data_real()
original_data_sweep = original_data.primary_sweep_values
waveform_unit = original_data.units_data[plot_name]
waveform_sweep_unit = original_data.units_sweeps["Time"]
tics = np.arange(20e-9, 100e-9, 1e-10, dtype=float)

sample_waveform = cir.post.sample_waveform(
    waveform_data=original_data_value,
    waveform_sweep=original_data_sweep,
    waveform_unit=waveform_unit,
    waveform_sweep_unit=waveform_sweep_unit,
    unit_interval=unit_interval,
    clock_tics=tics,
    pandas_enabled=False,
)
# -

# ## Plot Waveform
#
# Create the plot from a start time to stop time in seconds.

# +
tstop = 40.0e-9
tstart = 25.0e-9
scale_time = pyaedt.constants.unit_converter(
    1, unit_system="Time", input_units="s", output_units=waveform_sweep_unit
)
scale_data = pyaedt.constants.unit_converter(
    1, unit_system="Voltage", input_units="V", output_units=waveform_unit
)

tstop_ns = scale_time * tstop
tstart_ns = scale_time * tstart

for time in original_data_sweep:
    if tstart_ns <= time:
        start_index_original_data = original_data_sweep.index(time)
        break
for time in original_data_sweep[start_index_original_data:]:
    if time >= tstop_ns:
        stop_index_original_data = original_data_sweep.index(time)
        break
cont = 0
for frame in sample_waveform:
    if tstart <= frame[0]:
        start_index_waveform = cont
        break
    cont += 1
for frame in sample_waveform[start_index_waveform:]:
    if frame[0] >= tstop:
        stop_index_waveform = cont
        break
    cont += 1

original_data_zoom = original_data_value[start_index_original_data:stop_index_original_data]
original_sweep_zoom = original_data_sweep[start_index_original_data:stop_index_original_data]
original_data_zoom_array = np.array(list(map(list, zip(original_sweep_zoom, original_data_zoom))))
original_data_zoom_array[:, 0] *= 1
sampled_data_zoom_array = np.array(sample_waveform[start_index_waveform:stop_index_waveform])
sampled_data_zoom_array[:, 0] *= scale_time
sampled_data_zoom_array[:, 1] *= scale_data

fig, ax = plt.subplots()
ax.plot(sampled_data_zoom_array[:, 0], sampled_data_zoom_array[:, 1], "r*")
ax.plot(original_sweep_zoom, original_data_zoom_array[:, 1], color="blue")
ax.set_title(plot_name)
ax.set_xlabel(waveform_sweep_unit)
ax.set_ylabel(waveform_unit)
plt.show()
# -

# ## Plot Slicer Scatter
#
# Create the plot from a start time to stop time in seconds.

sample_waveform_array = np.array(sample_waveform)
fig, ax2 = plt.subplots()
ax2.plot(sample_waveform_array[:, 0], sample_waveform_array[:, 1], "r*")
ax2.set_title("Slicer Scatter: " + plot_name)
ax2.set_xlabel("s")
ax2.set_ylabel("V")
plt.show()

# ## Save Project
#
# Save the project and close AEDT.

cir.save_project()
print("Project Saved in {}".format(cir.project_path))
cir.release_desktop()

temp_dir.cleanup()  # Remove project folder and temporary files.
