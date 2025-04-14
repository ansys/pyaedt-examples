# # 2D Axi-symmetric Actuator - Force Calculation
#
# This example demonstrates how to leverage both: axi-symmetry and the magnetostatic solver
# to calculate the forces experienced by the anchor of an actuator due to change in
# current and anchor location
#
# Most examples can be described as a series of steps that comprise a workflow.
# 1. Import packages and instantiate the application.
# 2. Do something useful and interesting like creating the model, assign materials and boundary conditions, etc.
# 3. Run one or more analyses.
# 4. View the results.
#
# Keywords: **Maxwell2D**, **axi-symmetry** **magnetostatic**, **translational motion**, **installation example**

# ## Prerequisites
#
# ### Perform imports

# +
import os
import tempfile
import time

import ansys.aedt.core  # Interface to Ansys Electronics Desktop

# -

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.1"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.


# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ### Launch Maxwell 2d
#
# Create an instance of
# the ``Maxwell2d`` class. The Ansys Electronics Desktop will be launched
# with an active Maxwell2D design. The ``m2d`` object is subsequently
# used to
# create and simulate the actuator model.

project_name = os.path.join(temp_folder.name, "2d_axi_magsta_actuator.aedt")
m2d = ansys.aedt.core.Maxwell2d(
    project=project_name,
    solution_type="MagnetostaticZ",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Model Preparation
#
# ### Define actuator's housing point location
#
# The actuator's housing is built using line segments
# for readability and reusability we define the points
# as a python's list of lists, where each sublist defines an
# x-, y-, z-coordinate. (e.g., [[x1,y1,z1],...,[xn,yn,zn]].

points_housing = [
    [0, 0, 0],
    [0, 0, -10],
    [12, 0, -10],
    [12, 0, 10],
    [2.5, 0, 10],
    [2.5, 0, 8],
    [10, 0, 8],
    [10, 0, -8],
    [2, 0, -8],
    [2, 0, 0],
]

# ### Declare and initialize design parameters

m2d.modeler.model_units = "mm"  # Global units used in geometry creation
m2d[r"Amp_1"] = "1000A"  # Net current applied to coil
m2d[r"move"] = "0mm"  # Displacement applied to anchor

# ### Create 2D model
#
# Build coil, anchor and housing geometries
coil_m = m2d.modeler.create_rectangle(
    origin=[r"3mm", r"0mm", r"7mm"], sizes=[-14, 6], name=r"Coil", material=r"Copper"
)
anchor_m = m2d.modeler.create_rectangle(
    origin=[r"0mm", r"0mm", r"13mm - move"],
    sizes=[-8, 2],
    name=r"Anchor",
    material=r"steel_1008",
)
housing_m = m2d.modeler.create_polyline(
    points_housing, close_surface=True, name=r"Housing", material=r"steel_1008"
)
m2d.modeler.cover_lines(housing_m)

# Create surrounding vacuum domain
region_m = m2d.modeler.create_region(pad_percent=100)
region_m.material_name = r"vacuum"

# Fit all geometrical entities into the modeler's window
m2d.modeler.fit_all()

# ### Assign boundary conditions
#
# Apply zero magnetic vector potential on the region edges
# that the field only has a tangential component at the edge of the
# surrounding domain/region
m2d.assign_vector_potential(assignment=region_m.edges, boundary=r"VectorPotential1")

# ### Assign Excitation
#
# Create a current driven coil by applying a current excitation in the coil domain
m2d.assign_current(assignment=coil_m.name, amplitude=r"Amp_1", name="Current1")

# ### Enable force calculation on the anchor
m2d.assign_force(
    assignment=anchor_m,
    force_name="Force",
)

# ### Define solution setup
#
setup = m2d.create_setup(r"MySetup")
print(setup.props)
setup.props[r"MaximumPasses"] = 15
setup.props[r"PercentRefinement"] = 30
setup.props[r"PercentError"] = 0.1
setup.props[r"MinimumPasses"] = 2
setup.props[r"RelativeResidual"] = 1e-6

# ### Create variable/parameter sweeps
#
# Enable sweeps over coil net current and anchor displacement
value_sweep = m2d.parametrics.add(
    r"Amp_1", 500, 2000, 500, name="ParametricSetup1", variation_type="LinearStep"
)
value_sweep.add_variation(r"move", 0, 4, 1, variation_type="LinearStep")
#

# ### Run analysis
#
# > Run the simulation.

value_sweep.analyze(cores=NUM_CORES)

# ## Postprocess
#
# Create a Force vs. move (displacement) Report/Plot for every current value
#
m2d.post.create_report(
    expressions=[r"Force.Force_z"],
    variations={r"Amp_1": r"All", r"move": r"All"},
    plot_name=r"Force Plot 1",
    primary_sweep_variable=r"move",
    plot_type=r"Rectangular Plot",
)


# ## Finish
#
# ### Save the project

m2d.save_project()
m2d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
