# # Configuration files
#
# This example shows how you can use PyAEDT to export configuration files and reuse
# them to import in a new project. A configuration file is supported by these applications:
#
# * HFSS
# * 2D Extractor and Q3D Extractor
# * Maxwell
# * Icepak (in AEDT)
# * Mechanical (in AEDT)
#
# The following sections are covered:
#
# * Variables
# * Mesh operations (except Icepak)
# * Setup and optimetrics
# * Material properties
# * Object properties
# * Boundaries and excitations
#
# When a boundary is attached to a face, the tool tries to match it with a
# ``FaceByPosition`` on the same object name on the target design. If, for
# any reason, this face position has changed or the object name in the target
# design has changed, the boundary fails to apply.
#
# Keywords: **General**, **configuration file**, **setup**.

# ## Preparation
# Import the required packages

# +
import os
import tempfile
import time

import ansys.aedt.core

# -

# Define constants

AEDT_VERSION = "2024.2"
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory
#
# Create temporary directory.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download project

project_full_name = ansys.aedt.core.downloads.download_icepak(
    destination=temp_folder.name
)

# ## Open project
#
# Open the Icepak project from the project folder.

ipk = ansys.aedt.core.Icepak(
    project=project_full_name,
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
)
ipk.autosave_disable()

# ## Create source blocks
#
# Create a source block on the CPU and memories.

ipk.create_source_block(object_name="CPU", input_power="25W")
ipk.create_source_block(object_name=["MEMORY1", "MEMORY1_1"], input_power="5W")

# ## Assign boundaries
#
# Assign the opening and grille.

region = ipk.modeler["Region"]
ipk.assign_openings(air_faces=region.bottom_face_x.id)
ipk.assign_grille(air_faces=region.top_face_x.id, free_area_ratio=0.8)

# ## Create setup
#
# Create the setup. Properties can be set up from the ``setup`` object
# with getters and setters. They don't have to perfectly match the property
# syntax.

setup1 = ipk.create_setup()
setup1["FlowRegime"] = "Turbulent"
setup1["Max Iterations"] = 5
setup1["Solver Type Pressure"] = "flex"
setup1["Solver Type Temperature"] = "flex"
ipk.save_project()

# ## Export project to step file
#
# Export the current project to the step file.

filename = ipk.design_name
file_path = os.path.join(ipk.working_directory, filename + ".step")
ipk.export_3d_model(
    file_name=filename,
    file_path=ipk.working_directory,
    file_format=".step",
    assignment_to_export=[],
    assignment_to_remove=[],
)

# ## Export configuration files
#
# Export the configuration files. You can optionally disable the export and
# import sections. Supported formats are json and toml files

conf_file = ipk.configurations.export_config(
    os.path.join(ipk.working_directory, "config.toml")
)
ipk.close_project()

# ## Create project
#
# Create an Icepak project and import the step.

new_project = os.path.join(temp_folder.name, "example.aedt")
app = ansys.aedt.core.Icepak(version=AEDT_VERSION, project=new_project)
app.modeler.import_3d_cad(file_path)

# ## Import and apply configuration file
#
# Import and apply the configuration file. You can apply all or part of the
# JSON file that you import using options in the ``configurations`` object.

out = app.configurations.import_config(conf_file)
is_conf_imported = app.configurations.results.global_import_success

# ## Release AEDT
# Close the project and release AEDT.

app.release_desktop()
time.sleep(
    3
)  # Allow Electronics Desktop to shut down before cleaning the temporary project folder.

# ## Cleanup
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell removes
# all temporary files, including the project folder.

temp_folder.cleanup()
