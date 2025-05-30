# # Choke setup
#
# This example shows how to use PyAEDT to create a choke setup in Maxwell 3D.
#
# Keywords: **Maxwell 3D**, **choke**.

# ## Perform imports and define constants
#
# Perform required imports.

# +
import json
import os
import tempfile
import time

import ansys.aedt.core
# -

# Define constants.

AEDT_VERSION = "2025.1"
NG_MODE = False  # Open AEDT UI when it is launched.


# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch Maxwell3D
#
# Launch Maxwell 3D 2024 R2 in graphical mode.

project_name = os.path.join(temp_folder.name, "choke.aedt")
m3d = ansys.aedt.core.Maxwell3d(
    project=project_name,
    solution_type="EddyCurrent",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Define parameters
#
# The dictionary values contain the different parameter values of the core and
# the windings that compose the choke. You must not change the main structure of
# the dictionary. The dictionary has many primary keys, including
# ``"Number of Windings"``, ``"Layer"``, and ``"Layer Type"``, that have
# dictionaries as values. The keys of these dictionaries are secondary keys
# of the dictionary values, such as ``"1"``, ``"2"``, ``"3"``, ``"4"``, and
# ``"Simple"``.
#
# You must not modify the primary or secondary keys. You can modify only their values.
# You must not change the data types for these keys. For the dictionaries from
# ``"Number of Windings"`` through ``"Wire Section"``, values must be Boolean. Only
# one value per dictionary can be ``True``. If all values are ``True``, only the first one
# remains set to ``True``. If all values are ``False``, the first value is chosen as the
# correct one by default. For the dictionaries from ``"Core"`` through ``"Inner Winding"``,
# values must be strings, floats, or integers.
#
# Descriptions follow for the primary keys:
#
# - ``"Number of Windings"``: Number of windings around the core.
# - ``"Layer"``: Number of layers of all windings.
# - ``"Layer Type"``: Whether layers of a winding are linked to each other
# - ``"Similar Layer"``: Whether layers of a winding have the same number of turns and
# same spacing between turns.
# - ``"Mode"``: When there are only two windows, whether they are in common or differential mode.
# - ``"Wire Section"``: Type of wire section and number of segments.
# - ``"Core"``: Design of the core.
# - ``"Outer Winding"``: Design of the first layer or outer layer of a winding and the common
# parameters for all layers.
# - ``"Mid Winding"``: Turns and turns spacing (``Coil Pit``) for the second or
# mid layer if it is necessary.
# - ``"Inner Winding"``: Turns and turns spacing (``Coil Pit``) for the third or inner
# layer if it is necessary.
# - ``"Occupation(%)"``: An informative parameter that is useless to modify.
#
# The following parameter values work. You can modify them if you want.

values = {
    "Number of Windings": {"1": False, "2": False, "3": True, "4": False},
    "Layer": {"Simple": False, "Double": False, "Triple": True},
    "Layer Type": {"Separate": False, "Linked": True},
    "Similar Layer": {"Similar": False, "Different": True},
    "Mode": {"Differential": True, "Common": False},
    "Wire Section": {"None": False, "Hexagon": False, "Octagon": True, "Circle": False},
    "Core": {
        "Name": "Core",
        "Material": "ferrite",
        "Inner Radius": 100,
        "Outer Radius": 143,
        "Height": 25,
        "Chamfer": 0.8,
    },
    "Outer Winding": {
        "Name": "Winding",
        "Material": "copper",
        "Inner Radius": 100,
        "Outer Radius": 143,
        "Height": 25,
        "Wire Diameter": 5,
        "Turns": 2,
        "Coil Pit(deg)": 4,
        "Occupation(%)": 0,
    },
    "Mid Winding": {"Turns": 7, "Coil Pit(deg)": 4, "Occupation(%)": 0},
    "Inner Winding": {"Turns": 10, "Coil Pit(deg)": 4, "Occupation(%)": 0},
}

# ## Convert dictionary to JSON file
#
# Convert the dictionary to a JSON file. PyAEDT methods ask for the path of the
# JSON file as an argument. You can convert a dictionary to a JSON file.

# +
json_path = os.path.join(temp_folder.name, "choke_example.json")

with open(json_path, "w") as outfile:
    json.dump(values, outfile)
# -

# ## Verify parameters of JSON file
#
# Verify parameters of the JSON file. The ``check_choke_values()`` method takes
# the JSON file path as an argument and does the following:
#
# - Checks if the JSON file is correctly written (as explained earlier)
# - Checks equations on windings parameters to avoid having unintended intersections

dictionary_values = m3d.modeler.check_choke_values(
    input_dir=json_path, create_another_file=False
)
print(dictionary_values)

# ## Create choke
#
# Create the choke. The ``create_choke()`` method takes the JSON file path as an
# argument.

list_object = m3d.modeler.create_choke(input_file=json_path)
print(list_object)
core = list_object[1]
first_winding_list = list_object[2]
second_winding_list = list_object[3]
third_winding_list = list_object[4]

# ## Assign excitations

first_winding_faces = m3d.modeler.get_object_faces(
    assignment=first_winding_list[0].name
)
second_winding_faces = m3d.modeler.get_object_faces(
    assignment=second_winding_list[0].name
)
third_winding_faces = m3d.modeler.get_object_faces(
    assignment=third_winding_list[0].name
)
m3d.assign_current(
    assignment=[first_winding_faces[-1]],
    amplitude=1000,
    phase="0deg",
    swap_direction=False,
    name="phase_1_in",
)
m3d.assign_current(
    assignment=[first_winding_faces[-2]],
    amplitude=1000,
    phase="0deg",
    swap_direction=True,
    name="phase_1_out",
)
m3d.assign_current(
    assignment=[second_winding_faces[-1]],
    amplitude=1000,
    phase="120deg",
    swap_direction=False,
    name="phase_2_in",
)
m3d.assign_current(
    assignment=[second_winding_faces[-2]],
    amplitude=1000,
    phase="120deg",
    swap_direction=True,
    name="phase_2_out",
)
m3d.assign_current(
    assignment=[third_winding_faces[-1]],
    amplitude=1000,
    phase="240deg",
    swap_direction=False,
    name="phase_3_in",
)
m3d.assign_current(
    assignment=[third_winding_faces[-2]],
    amplitude=1000,
    phase="240deg",
    swap_direction=True,
    name="phase_3_out",
)

# ## Assign matrix

m3d.assign_matrix(
    assignment=["phase_1_in", "phase_2_in", "phase_3_in"], matrix_name="current_matrix"
)

# ## Create mesh operation

mesh = m3d.mesh
mesh.assign_skin_depth(
    assignment=[first_winding_list[0], second_winding_list[0], third_winding_list[0]],
    skin_depth=0.20,
    triangulation_max_length="10mm",
    name="skin_depth",
)
mesh.assign_surface_mesh_manual(
    assignment=[first_winding_list[0], second_winding_list[0], third_winding_list[0]],
    surface_deviation=None,
    normal_dev="30deg",
    name="surface_approx",
)

# ## Create boundaries
#
# Create the boundaries. A region with openings is needed to run the analysis.

region = m3d.modeler.create_air_region(
    x_pos=100, y_pos=100, z_pos=100, x_neg=100, y_neg=100, z_neg=0
)

# ## Create setup
#
# Create a setup with a sweep to run the simulation. Depending on your machine's
# computing power, the simulation can take some time to run.

setup = m3d.create_setup("MySetup")
print(setup.props)
setup.props["Frequency"] = "100kHz"
setup.props["PercentRefinement"] = 15
setup.props["MaximumPasses"] = 10
setup.props["HasSweepSetup"] = True
setup.add_eddy_current_sweep(
    sweep_type="LinearCount",
    start_frequency=100,
    stop_frequency=1000,
    step_size=12,
    units="kHz",
    clear=True
)

# ## Save project

m3d.save_project()
m3d.modeler.fit_all()
m3d.plot(
    show=False,
    output_file=os.path.join(temp_folder.name, "Image.jpg"),
    plot_air_objects=True,
)

# ## Release AEDT

m3d.save_project()
m3d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
