# # Automatic report creation
#
# This example shows how to create reports from a JSON template file.
#
#
# Keywords: **Circuit**, **report**.

# ## Perform imports and define constants
#
# Import the required packages. This example uses
# data from the [example-data repository](https://github.com/ansys/example-data/tree/master)
# located in ``pyaedt\custom_reports``.

# +
import os
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_file
from IPython.display import Image
# -

# Define constants.

AEDT_VERSION = "2025.1"
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT with Circuit
#
# AEDT is started by instantiating an instance of
# [pyaedt.Circuit](https://aedt.docs.pyansys.com/version/stable/API/_autosummary/pyaedt.circuit.Circuit.html).
#
# ### Application keyword arguments
#
# - The argument ``non_graphical`` specifies whether an interactive session is launched or if
#   AEDT is to run in non-graphical mode.
# - The Boolean parameter ``new_desktop`` specifies if a new instance
#   of AEDT is launched. If it is set to ``False``, the API tries to connect to a running session.
#
# This example extracts an archived project. The full path
# to the extracted project is accessible from the ``cir.project_file`` property.

# +
project_path = download_file(
    source="custom_reports/", destination=temp_folder.name
)

circuit = ansys.aedt.core.Circuit(
    project=os.path.join(project_path, "CISPR25_Radiated_Emissions_Example23R1.aedtz"),
    non_graphical=NG_MODE,
    version=AEDT_VERSION,
    new_desktop=True,
)
circuit.analyze()  # Run the circuit analysis.
# -

# ## Create a spectral report
#
# The JSON file is used to customize the report. In a spectral report, you can add limit lines. You can also
# add notes to a report and modify the axes, grid, and legend. Custom reports
# can be created in AEDT in non-graphical mode using version 2023 R2 and later.

report1 = circuit.post.create_report_from_configuration(
    os.path.join(project_path, "Spectrum_CISPR_Basic.json")
)
out = circuit.post.export_report_to_jpg(
    project_path=circuit.working_directory, plot_name=report1.plot_name
)

# Render the image.

Image(os.path.join(circuit.working_directory, report1.plot_name + ".jpg"))

# You can customize every aspect of the report. The method ``crate_report_from_configuration()`` reads the
# report configuration from a JSON file and generates the custom report.

report1_full = circuit.post.create_report_from_configuration(
    os.path.join(project_path, "Spectrum_CISPR_Custom.json")
)
out = circuit.post.export_report_to_jpg(
    circuit.working_directory, report1_full.plot_name
)
Image(os.path.join(circuit.working_directory, report1_full.plot_name + ".jpg"))

# ## Create a transient report
#
# The JSON configuration file can be read and modified from the API prior to creating the report.
# The following code modifies the trace rendering prior to creating the report.

# +
props = ansys.aedt.core.generic.file_utils.read_json(
    os.path.join(project_path, "Transient_CISPR_Custom.json")
)

report2 = circuit.post.create_report_from_configuration(
    report_settings=props, solution_name="NexximTransient"
)
out = circuit.post.export_report_to_jpg(circuit.working_directory, report2.plot_name)
Image(os.path.join(circuit.working_directory, report2.plot_name + ".jpg"))
# -

# The ``props`` dictionary can be used to customize any aspect of an existing report or generate a new report.
# In this example, the name of the curve is customized.

props["expressions"] = {"V(Battery)": {}, "V(U1_VDD)": {}}
props["plot_name"] = "Battery Voltage"
report3 = circuit.post.create_report_from_configuration(
    report_settings=props, solution_name="NexximTransient"
)
out = circuit.post.export_report_to_jpg(circuit.working_directory, report3.plot_name)
Image(os.path.join(circuit.working_directory, report3.plot_name + ".jpg"))

# ## Create an eye diagram
#
# You can use the JSON file to create an eye diagram. The following code includes the eye.

report4 = circuit.post.create_report_from_configuration(
    os.path.join(project_path, "EyeDiagram_CISPR_Basic.json")
)
out = circuit.post.export_report_to_jpg(circuit.working_directory, report4.plot_name)
Image(os.path.join(circuit.working_directory, report4.plot_name + ".jpg"))

# +
report4_full = circuit.post.create_report_from_configuration(
    os.path.join(project_path, "EyeDiagram_CISPR_Custom.json")
)

out = circuit.post.export_report_to_jpg(
    circuit.working_directory, report4_full.plot_name
)
Image(os.path.join(circuit.working_directory, report4_full.plot_name + ".jpg"))
# -

# ## Save project and close AEDT
#
# Save the project and close AEDT. The example has finished running. You can retrieve project files
# from ``temp_folder.name``.

circuit.save_project()
print("Project Saved in {}".format(circuit.project_path))

circuit.release_desktop()
time.sleep(3)

# ## Clean up
#
# The following cell cleans up the temporary directory and
# removes all project files.

temp_folder.cleanup()
