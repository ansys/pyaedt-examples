# # Bath plate analysis
#
# This example uses PyAEDT to set up the TEAM 3 bath plate problem and
# solve it using the Maxwell 3D eddy current solver.
#
# For more information on this problem, see this
# [paper](https://www.compumag.org/wp/wp-content/uploads/2018/06/problem3.pdf).
#
# Keywords: **Maxwell 3D**, **TEAM 3 bath plate**

# ## Prerequisites
#
# ### Perform imports

# +
import os
import tempfile
import time

import ansys.aedt.core
# -

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.2"
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

# ### Launch Maxwell 3D
#
# Create an instance of the ``Maxwell3d`` class named ``m3d`` by providing
# the project and design names, the solver, and the version.

m3d = ansys.aedt.core.Maxwell3d(
    project=os.path.join(temp_folder.name, "COMPUMAG.aedt"),
    design="TEAM_3_Bath_Plate",
    solution_type="EddyCurrent",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)
uom = m3d.modeler.model_units = "mm"

# ### Add variable
#
# Add a design variable named ``Coil_Position`` to use later to adjust the
# position of the coil.

Coil_Position = -20
m3d["Coil_Position"] = str(Coil_Position) + m3d.modeler.model_units

# ### Add material
#
# Add a material named ``team3_aluminium`` for the ladder plate.

mat = m3d.materials.add_material(name="team3_aluminium")
mat.conductivity = 32780000

# ### Draw background region
#
# Draw a background region that uses the default properties for an air region.

m3d.modeler.create_air_region(
    x_pos=100, y_pos=100, z_pos=100, x_neg=100, y_neg=100, z_neg=100
)

# ### Draw ladder plate and assign material
#
# Draw a ladder plate and assign it the newly created material ``team3_aluminium``.

m3d.modeler.create_box(
    origin=[-30, -55, 0],
    sizes=[60, 110, -6.35],
    name="LadderPlate",
    material="team3_aluminium",
)
m3d.modeler.create_box(origin=[-20, -35, 0], sizes=[40, 30, -6.35], name="CutoutTool1")
m3d.modeler.create_box(origin=[-20, 5, 0], sizes=[40, 30, -6.35], name="CutoutTool2")
m3d.modeler.subtract(
    blank_list="LadderPlate",
    tool_list=["CutoutTool1", "CutoutTool2"],
    keep_originals=False,
)

# ### Add mesh refinement to ladder plate

# > **Note:** You can uncomment the following code.

# m3d.mesh.assign_length_mesh(
#     assignment="LadderPlate",
#     maximum_length=3,
#     maximum_elements=None,
#     name="Ladder_Mesh",
# )

# ### Draw search coil and assign excitation
#
# Draw a search coil and assign it a ``stranded`` current excitation.
# The stranded type forces the current density to be constant in the coil.

m3d.modeler.create_cylinder(
    orientation="Z",
    origin=[0, "Coil_Position", 15],
    radius=40,
    height=20,
    name="SearchCoil",
    material="copper",
)
m3d.modeler.create_cylinder(
    orientation="Z",
    origin=[0, "Coil_Position", 15],
    radius=20,
    height=20,
    name="Bore",
    material="copper",
)
m3d.modeler.subtract(blank_list="SearchCoil", tool_list="Bore", keep_originals=False)
m3d.modeler.section(assignment="SearchCoil", plane="YZ")
m3d.modeler.separate_bodies(assignment="SearchCoil_Section1")
m3d.modeler.delete(assignment="SearchCoil_Section1_Separate1")
m3d.assign_current(
    assignment=["SearchCoil_Section1"],
    amplitude=1260,
    solid=False,
    name="SearchCoil_Excitation",
)

# ### Draw a line for plotting $B_z$
#
# Draw a line for plotting Bz later. Bz is the Z component of the flux
# density. The following code also adds a small diameter cylinder to refine the
# mesh locally around the line.

line_points = [["0mm", "-55mm", "0.5mm"], ["0mm", "55mm", "0.5mm"]]
m3d.modeler.create_polyline(points=line_points, name="Line_AB")
poly = m3d.modeler.create_polyline(points=line_points, name="Line_AB_MeshRefinement")
poly.set_crosssection_properties(section="Circle", width="0.5mm")

# ### Add Maxwell 3D setup
#
# Add a Maxwell 3D setup with frequency points at 50 Hz and 200 Hz.

setup = m3d.create_setup(name="Setup1")
setup.props["Frequency"] = "200Hz"
setup.props["HasSweepSetup"] = True
setup.props["MaximumPasses"] = 1
setup.add_eddy_current_sweep(
    sweep_type="LinearStep", start_frequency=50, stop_frequency=200, step_size=150, clear=True
)

# ### Adjust eddy effects
#
# Adjust eddy effects for the ladder plate and the search coil. The setting for
# eddy effect is ignored for the stranded conductor type used in the search coil.

m3d.eddy_effects_on(
    assignment=["LadderPlate"],
    enable_eddy_effects=True,
    enable_displacement_current=True,
)
m3d.eddy_effects_on(
    assignment=["SearchCoil"],
    enable_eddy_effects=False,
    enable_displacement_current=True,
)

# ### Add linear parametric sweep
#
# Add a linear parametric sweep for the two coil positions.

sweep_name = "CoilSweep"
param = m3d.parametrics.add(
    variable="Coil_Position",
    start_point=-20,
    end_point=0,
    step=20,
    variation_type="LinearStep",
    name=sweep_name,
)
param["SaveFields"] = True
param["CopyMesh"] = False
param["SolveWithCopiedMeshOnly"] = True

# ### Solve parametric sweep
#
# Solve the parametric sweep directly so that results of all variations are available.

m3d.save_project()
param.analyze(cores=NUM_CORES)

# ## Postprocess
#
# ### Create expression for Bz
#
# Create an expression for Bz using PyAEDT advanced fields calculator.

bz = {
    "name": "Bz",
    "description": "Z component of B",
    "design_type": ["Maxwell 3D"],
    "fields_type": ["Fields"],
    "primary_sweep": "Distance",
    "assignment": "",
    "assignment_type": ["Line"],
    "operations": [
        "NameOfExpression('<Bx,By,Bz>')",
        "Operation('ScalarZ')",
        "Scalar_Constant(1000)",
        "Operation('*')",
        "Operation('Smooth')",
    ],
    "report": ["Field_3D"],
}
m3d.post.fields_calculator.add_expression(bz, None)

# ### Plot $|B_z|$ as a function of frequency
#
# Plot $|B_z|$ as a function of frequency for both coil positions.

# +
variations = {
    "Distance": ["All"],
    "Freq": ["All"],
    "Phase": ["0deg"],
    "Coil_Position": ["All"],
}

m3d.post.create_report(
    expressions="mag(Bz)",
    variations=variations,
    primary_sweep_variable="Distance",
    report_category="Fields",
    context="Line_AB",
    plot_name="mag(Bz) Along 'Line_AB' Coil",
)
# -

# ### Get simulation results from a solved setup
#
# Get simulation results from a solved setup as a ``SolutionData`` object.

# +

solutions = m3d.post.get_solution_data(
    expressions="mag(Bz)",
    report_category="Fields",
    context="Line_AB",
    variations=variations,
    primary_sweep_variable="Distance",
)
# -

# ### Set up sweep value and plot solution

solutions.active_variation["Coil_Position"] = -0.02
solutions.plot()

# ### Change sweep value and plot solution
#
# Change the sweep value and plot the solution again.
# Uncomment to show plots.

solutions.active_variation["Coil_Position"] = 0
# solutions.plot()

# ### Plot induced current density on surface of ladder plate
#
# Plot the induced current density, ``"Mag_J"``, on the surface of the ladder plate.

ladder_plate = m3d.modeler.objects_by_name["LadderPlate"]
intrinsics = {"Freq": "50Hz", "Phase": "0deg"}
m3d.post.create_fieldplot_surface(
    assignment=ladder_plate.faces,
    quantity="Mag_J",
    intrinsics=intrinsics,
    plot_name="Mag_J",
)

# ## Finish
#
# ### Save the project

m3d.save_project()
m3d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
