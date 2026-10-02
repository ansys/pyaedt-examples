# # RLC filter circuit design analysis
#
# This example demonstrates how to use PyAEDT to set up and analyze an RLC filter circuit in Twin Builder.
# It covers setup creation, parametric sweeps of key circuit parameters, and post-processing of simulation results.
# Generated plots illustrate how the parametric sweep affects the circuit response.
# Key behaviors such as resonance peaking, damping, and current flow under different resistance values are examined.
#
# Keywords: **Twin Builder**, **RLC**.

# +
import tempfile

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_file

# -

# ## Define constants
#
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2026.1"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.
TB_FILE_NAME = "RLC_Filter_pyaedt.aedt"
TB_DESIGN_NAME = "RLC_Filter_Optimetrics"

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
# The ``download_file()`` method provides access to a library
# of examples and models from the Ansys GitHub organization:
# [example-data repository](https://github.com/ansys/example-data).

project_path = download_file(
    source="pyaedt/twinbuilder_rlc_filter",
    name=TB_FILE_NAME,
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

setup = tb.create_setup(setup_type="TwinbuilderTR", name="TR")

# Change setup properties to specify the stop time, minimum time step, and maximum time step.
# In the order: Stop Time, Min time step, Max time step.

setup.props["TransientData"][0] = "10ms"
setup.props["TransientData"][1] = "1us"
setup.props["TransientData"][2] = "20us"
setup.update()

# Save and close the project to ensure that all changes are written to disk.
# Reopen the project to ensure that the changes are reflected in the current session.

tb.close_project(save=True)
tb = ansys.aedt.core.TwinBuilder(
    project=project_path,
    design=TB_DESIGN_NAME,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Parametric sweep
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

# Analyze parametric sweep

sweep.analyze()

# ## Post-processing
#
# In this example two different approaches to post-processing are demonstrated.
# The first approach uses the ``create_report`` method to creat in AEDT a report with the specified expressions and domain.
# The second approach uses the ``get_report_data`` method to retrieve the report data in Python without creating a report in AEDT.
# After retrieving the data, the results are exported to a CSV file.

# ## Create reports in AEDT
#
# First report shows the startup response and steady-state apmlitude/phase difference between the voltage across
# the source ``V_IN.V`` and the voltage across the shunt capacitor ``C_SHUNT.V`` assuming a 10V, 10mH, 50ohm input.

vars = tb.available_variations.all
vars["$Rseries"] = "50ohm"
vars["$Lseries"] = "10mH"
vars["$Vdrive"] = "10V"
report_voltages = tb.post.create_report(
    plot_name="RLC 10V 10mH 50ohm Input Output",
    domain="Time",
    expressions=["C_SHUNT.V"],
    primary_sweep_variable="Time",
    variations=vars,
    context={"optimetrics_setup": sweep.name}
)

# Second report shows resonance for different values of series inductance.
# The report shows the voltage across the shunt capacitor ``C_SHUNT.V`` for different values of series inductance.
# Values for the series inductance are 5, 10, 15, and 20 mH while the series resistance is fixed at 50 ohms and the drive voltage is fixed at 10V.

vars = tb.available_variations.all
vars["$Rseries"] = "50ohm"
vars["$Lseries"] = "All"
vars["$Vdrive"] = "10V"
report_resonance = tb.post.create_report(
    plot_name="RLC Output Voltage vs Inductance at 10V 50ohm",
    domain="Time",
    expressions=["C_SHUNT.V"],
    primary_sweep_variable="Time",
    variations=vars,
    context={"optimetrics_setup": sweep.name}
)

# ## Export report data to CSV
#
# Export the report data to a CSV file for further analysis or documentation.

#export one as csv
tb.post.export_report_to_csv()

#export one with another format
tb.post.export_report_to_file()

# Post-processing without creating a report in AEDT GUI

