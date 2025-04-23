# # Doppler setup
#
# This example shows how to use PyAEDT to create a multipart scenario in HFSS SBR+
# and set up a doppler analysis.
#
# Keywords: **HFSS**, **SBR+**, **doppler**.

# ## Perform imports and define constants
#
# Perform required imports.

# +
import os
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_multiparts
# -

# Define constants.

AEDT_VERSION = "2025.1"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download 3D component
# Download the 3D component that is needed to run the example.

library_path = download_multiparts(
    local_path=temp_folder.name
)

# ## Launch HFSS and open project
#
# Launch HFSS and open the project.

project_name = os.path.join(temp_folder.name, "doppler.aedt")
app = ansys.aedt.core.Hfss(
    version=AEDT_VERSION,
    solution_type="SBR+",
    new_desktop=True,
    project=project_name,
    close_on_exit=True,
    non_graphical=NG_MODE,
)

# Creation of the "actors" in the scene is comprised of many editing steps. Disabling the autosave option helps
# avoid delays that occur while the project is being saved.

app.autosave_disable()

# ## Save project and rename design
#
# Save the project to the temporary folder and rename the design.

design = "doppler_sbr"
app.rename_design(design)
app.save_project()

# ## Set up library paths
#
# Specify the location of 3D components used to create the scene.

actor_lib = os.path.join(library_path, "actor_library")
env_lib = os.path.join(library_path, "environment_library")
radar_lib = os.path.join(library_path, "radar_modules")
env_folder = os.path.join(env_lib, "road1")
person_folder = os.path.join(actor_lib, "person3")
car_folder = os.path.join(actor_lib, "vehicle1")
bike_folder = os.path.join(actor_lib, "bike1")
bird_folder = os.path.join(actor_lib, "bird1")

# ## Define environment
#
# Define the background environment.

road1 = app.modeler.add_environment(input_dir=env_folder, name="Bari")
prim = app.modeler

# ## Place actors
#
# Place actors in the environment. This code places persons, birds, bikes, and cars
# in the environment.

person1 = app.modeler.add_person(
    input_dir=person_folder,
    speed=1.0,
    global_offset=[25, 1.5, 0],
    yaw=180,
    name="Massimo",
)
person2 = app.modeler.add_person(
    input_dir=person_folder,
    speed=1.0,
    global_offset=[25, 2.5, 0],
    yaw=180,
    name="Devin",
)
car1 = app.modeler.add_vehicle(
    input_dir=car_folder, speed=8.7, global_offset=[3, -2.5, 0], name="LuxuryCar"
)
bike1 = app.modeler.add_vehicle(
    input_dir=bike_folder,
    speed=2.1,
    global_offset=[24, 3.6, 0],
    yaw=180,
    name="Alberto_in_bike",
)
bird1 = app.modeler.add_bird(
    input_dir=bird_folder,
    speed=1.0,
    global_offset=[19, 4, 3],
    yaw=120,
    pitch=-5,
    flapping_rate=30,
    name="Pigeon",
)
bird2 = app.modeler.add_bird(
    input_dir=bird_folder,
    speed=1.0,
    global_offset=[6, 2, 3],
    yaw=-60,
    pitch=10,
    name="Eagle",
)

# ## Place radar
#
# Place radar on the car. The radar is created relative to the car's coordinate
# system.

radar1 = app.create_sbr_radar_from_json(
    radar_file=radar_lib,
    name="Example_1Tx_1Rx",
    offset=[2.57, 0, 0.54],
    use_relative_cs=True,
    relative_cs_name=car1.cs_name,
)

# ## Create setup
#
# Create setup and validate it. The ``create_sbr_pulse_doppler_setup()`` method
# creates a setup and a parametric sweep on the time variable with a
# duration of two seconds. The step is computed automatically from CPI.

setup, sweep = app.create_sbr_pulse_doppler_setup(sweep_time_duration=2)
app.set_sbr_current_sources_options()
app.validate_simple()

# ## Solve and release AEDT
#
# Solve and release AEDT. To solve, uncomment the ``app.analyze_setup`` command
# to activate the simulation.

# +
# app.analyze_setup(sweep.name)
# -

# ## Release AEDT
#
# Release AEDT and close the example.

app.save_project()
app.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``. If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
