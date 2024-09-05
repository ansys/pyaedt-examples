# # Automatic report creation
#
# This example demonstrates how to create reports from a JSON template file.
#
#
# Keywords: **Circuit**, **Report**.

# ## Perform required imports
#
# Perform required imports and set the local path to the path for PyAEDT. This example uses
# data from the [example-data repository](https://github.com/ansys/example-data/tree/master)
# located in ``pyaedt\custom_reports``.

# +
import os
import tempfile
import time

import ansys.aedt.core
from IPython.display import Image

# ## Define constants

AEDT_VERSION = "2024.2"
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory
#
# Create temporary directory.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT with the Circuit Interface
#
# ### Application keyword arguments:
#
# The application is started by instantiating an instance of
# [pyaedt.Circuit](https://aedt.docs.pyansys.com/version/stable/API/_autosummary/pyaedt.circuit.Circuit.html).
#
# - The argument ``non_graphical`` specifies whether or not an interactive session will be launched or if
#   AEDT runs in non-graphical mode.
# - The Boolean parameter ``new_desktop`` specifies if a new instance
#   of AEDT will be launched. If it is set to ``False`` the API will try to connect to a running session.
#
# This example extracts an archived project. The full path
# to the extracted project is accessible from the ``cir.project_file`` property.

# +
project_path = ansys.aedt.core.downloads.download_file(
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

# ## Create a Spectral Report
#
# The JSON file is used to customize the report. In a spectral report, you can add Limit lines, and
# notes can be added to the report. The report axes, grid, and the legend can also be modified. The custom reports
# can be created in AEDT in non-graphical mode using version 2023 R2 and later.

report1 = circuit.post.create_report_from_configuration(
    os.path.join(project_path, "Spectrum_CISPR_Basic.json")
)
out = circuit.post.export_report_to_jpg(
    project_path=circuit.working_directory, plot_name=report1.plot_name
)

# Now render the image.

Image(os.path.join(circuit.working_directory, report1.plot_name + ".jpg"))

# Every aspect of the report can be customized. The method ``crate_report_from_configuration`` reads the
# report configuration from a ``*.json`` file and generates the custom report.

report1_full = circuit.post.create_report_from_configuration(
    os.path.join(project_path, "Spectrum_CISPR_Custom.json")
)
out = circuit.post.export_report_to_jpg(
    circuit.working_directory, report1_full.plot_name
)
Image(os.path.join(circuit.working_directory, report1_full.plot_name + ".jpg"))

# ## Transient Report
#
# The JSON configuration file can be read and modified from the API prior to creating the report.
# The following code modifies the trace rendering
# prior to creating the report.

# +
props = ansys.aedt.core.general_methods.read_json(
    os.path.join(project_path, "Transient_CISPR_Custom.json")
)

report2 = circuit.post.create_report_from_configuration(
    report_settings=props, solution_name="NexximTransient"
)
out = circuit.post.export_report_to_jpg(circuit.working_directory, report2.plot_name)
Image(os.path.join(circuit.working_directory, report2.plot_name + ".jpg"))
# -

# The ``props`` dictionary can be used to customize any aspect of an existing report or generate a new report.
# In this example the name of the curve is customized.

props["expressions"] = {"V(Battery)": {}, "V(U1_VDD)": {}}
props["plot_name"] = "Battery Voltage"
report3 = circuit.post.create_report_from_configuration(
    report_settings=props, solution_name="NexximTransient"
)
out = circuit.post.export_report_to_jpg(circuit.working_directory, report3.plot_name)
Image(os.path.join(circuit.working_directory, report3.plot_name + ".jpg"))

# ## Eye Diagram
#
# Create an eye diagram. the JSON file can be used to create an eye diagram, including the eye mask as demonsrated here.

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
# Save the project and close AEDT. The example has finished running. Project files can be retrieved
# from ``temp_folder.name``.

circuit.save_project()
print("Project Saved in {}".format(circuit.project_path))

circuit.release_desktop()
time.sleep(3)

# ## Cleanup
#
# The following cell cleans up the temporary directory and
# removes all project files.

temp_folder.cleanup()
