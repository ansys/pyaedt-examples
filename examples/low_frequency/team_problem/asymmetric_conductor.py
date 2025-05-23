# # Asymmetric conductor analysis
#
# This example uses PyAEDT to set up the TEAM 7 problem for an asymmetric
# conductor with a hole and solve it using the Maxwell 3D eddy current solver.
# For more information on this problem, see this
# [paper](https://www.compumag.org/wp/wp-content/uploads/2018/06/problem7.pdf).
#
# Keywords: **Maxwell 3D**, **Asymmetric conductor**.

# ## Prerequisites
#
# ### Perform imports

# +
import os
import tempfile
import time

import numpy as np
from ansys.aedt.core import Maxwell3d
from ansys.aedt.core.generic.file_utils import write_csv
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

# ### Launch Maxwell 3D
#
# Create an instance of the ``Maxwell3d`` class named ``m3d`` by providing
# the project and design names, the solver, and the version.

project_name = os.path.join(temp_folder.name, "COMPUMAG2.aedt")
m3d = Maxwell3d(
    project=project_name,
    design="TEAM_7_Asymmetric_Conductor",
    solution_type="EddyCurrent",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)
m3d.modeler.model_units = "mm"

# ## Model Preparation
#
# ### Define the Maxwell 3D analysis setup
#
# Add a Maxwell 3D setup with frequency points at DC, 50 Hz, and 200Hz.
# Otherwise, the default PyAEDT setup values are used. To approximate a DC field in the
# eddy current solver, use a low frequency value. Second-order shape functions improve
# the smoothness of the induced currents in the plate.

# +
dc_freq = 0.1
stop_freq = 50

setup = m3d.create_setup(name="Setup1")
setup.props["Frequency"] = "200Hz"
setup.props["HasSweepSetup"] = True
setup.add_eddy_current_sweep(
    sweep_type="LinearStep",
    start_frequency=dc_freq,
    stop_frequency=stop_freq,
    step_size=stop_freq - dc_freq,
    clear=True,
)
setup.props["UseHighOrderShapeFunc"] = True
setup.props["PercentError"] = 0.4
# -

# ### Define coil dimensions
#
# Define coil dimensions as shown on the TEAM7 drawing of the coil.

coil_external = 150 + 25 + 25
coil_internal = 150
coil_r1 = 25
coil_r2 = 50
coil_thk = coil_r2 - coil_r1
coil_height = 100
coil_centre = [294 - 25 - 150 / 2, 25 + 150 / 2, 19 + 30 + 100 / 2]

# ### Define expressions to evaluate solution data
# Use expressions to construct the three dimensions needed to describe the midpoints of
# the coil.

dim1 = coil_internal / 2 + (coil_external - coil_internal) / 4
dim2 = coil_internal / 2 - coil_r1
dim3 = dim2 + np.sqrt(((coil_r1 + (coil_r2 - coil_r1) / 2) ** 2) / 2)

# ### Draw the coil
# Use coordinates to draw a polyline along which to sweep the coil cross sections.

P1 = [dim1, -dim2, 0]
P2 = [dim1, dim2, 0]
P3 = [dim3, dim3, 0]
P4 = [dim2, dim1, 0]

# Create a coordinate system to use as a reference for the coil.

m3d.modeler.create_coordinate_system(
    origin=coil_centre, mode="view", view="XY", name="Coil_CS"
)

# Create a polyline. One quarter of the coil is modeled by sweeping a 2D sheet along a polyline.

test = m3d.modeler.create_polyline(
    points=[P1, P2, P3, P4], segment_type=["Line", "Arc"], name="Coil"
)
test.set_crosssection_properties(section="Rectangle", width=coil_thk, height=coil_height)

# Duplicate and unite the polyline to create the full coil.

m3d.modeler.duplicate_around_axis(
    assignment="Coil",
    axis="Global",
    angle=90,
    clones=4,
    create_new_objects=True,
    is_3d_comp=False,
)
m3d.modeler.unite("Coil, Coil_1, Coil_2")
m3d.modeler.unite("Coil, Coil_3")
m3d.modeler.fit_all()

# ### Assign material and enable the field solution inside the copper coil
#
# Assign the material ``Cooper`` from the Maxwell internal library to the coil and
# allow a solution inside the coil.

m3d.assign_material(assignment="Coil", material="Copper")
m3d.solve_inside("Coil")

# ### Create terminal
#
# Create a terminal for the coil from a cross-section that is split and one half deleted.

m3d.modeler.section(assignment="Coil", plane="YZ")
m3d.modeler.separate_bodies(assignment="Coil_Section1")
m3d.modeler.delete(assignment="Coil_Section1_Separate1")

# ### Add variable for coil excitation
#
# Use a parameter to define the coil current.
# The units in this case are Ampere$\times$Turns.

Coil_Excitation = 2742
m3d["Coil_Excitation"] = str(Coil_Excitation) + "A"
m3d.assign_current(assignment="Coil_Section1", amplitude="Coil_Excitation", solid=False)
m3d.modeler.set_working_coordinate_system("Global")

# ### Add material
#
# Add a material named ``team3_aluminium``.

mat = m3d.materials.add_material("team7_aluminium")
mat.conductivity = 3.526e7

# ### Create the aluminium plate with a hole
#
# Draw the aluminium plate with a hole by subtracting two cuboids.

plate = m3d.modeler.create_box(
    origin=[0, 0, 0], sizes=[294, 294, 19], name="Plate", material="team7_aluminium"
)
m3d.modeler.fit_all()
hole = m3d.modeler.create_box(origin=[18, 18, 0], sizes=[108, 108, 19], name="Hole")
m3d.modeler.subtract(blank_list="Plate", tool_list=["Hole"], keep_originals=False)

# ### Draw background region
#
# The background air region defines the full volumetric solution domain.

m3d.modeler.create_air_region(
    x_pos=100, y_pos=100, z_pos=100, x_neg=100, y_neg=100, z_neg=100
)

# ### Adjust eddy effects for plate and coil
#
# Disable the eddy effects for the plate and coil. This forces the current to flow uniformly through the coils cross-section as would be the case for stranded wires.

m3d.eddy_effects_on(assignment="Plate")
m3d.eddy_effects_on(
    assignment=["Coil", "Region", "Line_A1_B1mesh", "Line_A2_B2mesh"],
    enable_eddy_effects=False,
    enable_displacement_current=False,
)

# ### Create expression for $B_z$ in Gauss
#
# Create an expression for the $z$-component of $\bf{B}$ in Gauss using PyAEDT advanced fields calculator.

bz = {
    "name": "Bz",
    "description": "Z component of B in Gauss",
    "design_type": ["Maxwell 3D"],
    "fields_type": ["Fields"],
    "primary_sweep": "Distance",
    "assignment": "",
    "assignment_type": ["Line"],
    "operations": [
        "NameOfExpression('<Bx,By,Bz>')",
        "Operation('ScalarZ')",
        "Scalar_Function(FuncValue='Phase')",
        "Operation('AtPhase')",
        "Scalar_Constant(10000)",
        "Operation('*')",
        "Operation('Smooth')",
    ],
    "report": ["Field_3D"],
}
m3d.post.fields_calculator.add_expression(bz, None)

# ### Draw two lines along which to plot $B_z$
#
# Draw two lines along which to plot Bz. The following code also adds a small cylinder
# to refine the mesh locally around each line.

# +
lines = ["Line_A1_B1", "Line_A2_B2"]
mesh_diameter = "2mm"

line_points_1 = [["0mm", "72mm", "34mm"], ["288mm", "72mm", "34mm"]]
polyline = m3d.modeler.create_polyline(points=line_points_1, name=lines[0])
l1_mesh = m3d.modeler.create_polyline(points=line_points_1, name=lines[0] + "mesh")
l1_mesh.set_crosssection_properties(section="Circle", width=mesh_diameter)

line_points_2 = [["0mm", "144mm", "34mm"], ["288mm", "144mm", "34mm"]]
polyline2 = m3d.modeler.create_polyline(points=line_points_2, name=lines[1])
l2_mesh = m3d.modeler.create_polyline(points=line_points_2, name=lines[1] + "mesh")
l2_mesh.set_crosssection_properties(section="Circle", width=mesh_diameter)
# -

# Published measurement results are included with this script via the following list.
# Test results are used to create text files for import into a rectangular plot
# and to overlay simulation results.

# +
project_dir = temp_folder.name
dataset = [
    "Bz A1_B1 000 0",
    "Bz A1_B1 050 0",
    "Bz A1_B1 050 90",
    "Bz A1_B1 200 0",
    "Bz A1_B1 200 90",
    "Bz A2_B2 050 0",
    "Bz A2_B2 050 90",
    "Bz A2_B2 200 0",
    "Bz A2_B2 200 90",
]
header = ["Distance [mm]", "Bz [Tesla]"]

line_length = [
    0,
    18,
    36,
    54,
    72,
    90,
    108,
    126,
    144,
    162,
    180,
    198,
    216,
    234,
    252,
    270,
    288,
]
data = [
    [
        -6.667,
        -7.764,
        -8.707,
        -8.812,
        -5.870,
        8.713,
        50.40,
        88.47,
        100.9,
        104.0,
        104.8,
        104.9,
        104.6,
        103.1,
        97.32,
        75.19,
        29.04,
    ],
    [
        4.90,
        -17.88,
        -22.13,
        -20.19,
        -15.67,
        0.36,
        43.64,
        78.11,
        71.55,
        60.44,
        53.91,
        52.62,
        53.81,
        56.91,
        59.24,
        52.78,
        27.61,
    ],
    [
        -1.16,
        2.84,
        4.15,
        4.00,
        3.07,
        2.31,
        1.89,
        4.97,
        12.61,
        14.15,
        13.04,
        12.40,
        12.05,
        12.27,
        12.66,
        9.96,
        2.36,
    ],
    [
        -3.63,
        -18.46,
        -23.62,
        -21.59,
        -16.09,
        0.23,
        44.35,
        75.53,
        63.42,
        53.20,
        48.66,
        47.31,
        48.31,
        51.26,
        53.61,
        46.11,
        24.96,
    ],
    [
        -1.38,
        1.20,
        2.15,
        1.63,
        1.10,
        0.27,
        -2.28,
        -1.40,
        4.17,
        3.94,
        4.86,
        4.09,
        3.69,
        4.60,
        3.48,
        4.10,
        0.98,
    ],
    [
        -1.83,
        -8.50,
        -13.60,
        -15.21,
        -14.48,
        -5.62,
        28.77,
        60.34,
        61.84,
        56.64,
        53.40,
        52.36,
        53.93,
        56.82,
        59.48,
        52.08,
        26.56,
    ],
    [
        -1.63,
        -0.60,
        -0.43,
        0.11,
        1.26,
        3.40,
        6.53,
        10.25,
        11.83,
        11.83,
        11.01,
        10.58,
        10.80,
        10.54,
        10.62,
        9.03,
        1.79,
    ],
    [
        -0.86,
        -7.00,
        -11.58,
        -13.36,
        -13.77,
        -6.74,
        24.63,
        53.19,
        54.89,
        50.72,
        48.03,
        47.13,
        48.25,
        51.35,
        53.35,
        45.37,
        24.01,
    ],
    [
        -1.35,
        -0.71,
        -0.81,
        -0.67,
        0.15,
        1.39,
        2.67,
        3.00,
        4.01,
        3.80,
        4.00,
        3.02,
        2.20,
        2.78,
        1.58,
        1.37,
        0.93,
    ],
]
# -

# ### Write dataset values to a CSV file
#
# Dataset details are used to encode test parameters in the text files.
# For example, ``Bz A1_B1 050 0`` is the Z component of flux density ``B``
# along line ``A1_B1`` at 50 Hz and 0 deg.

line_length.insert(0, header[0])
for i in range(len(dataset)):
    data[i].insert(0, header[1])
    ziplist = zip(line_length, data[i])
    file_path = os.path.join(temp_folder.name, str(dataset[i]) + ".csv")
    write_csv(output_file=file_path, list_data=ziplist)

# ### Create rectangular plots and import test data into report
#
# Create rectangular plots, using text file encoding to control their formatting.
# Import test data into the correct plot and overlay with the simulation results.
# Variations for a DC plot must have a different frequency and phase than the other plots.

for item in range(len(dataset)):
    if item % 2 == 0:
        t = dataset[item]
        plot_name = t[0:3] + "Along the Line" + t[2:9] + ", " + t[9:12] + "Hz"
        if t[9:12] == "000":
            variations = {
                "Distance": ["All"],
                "Freq": [str(dc_freq) + "Hz"],
                "Phase": ["0deg"],
                "Coil_Excitation": ["All"],
            }
        else:
            variations = {
                "Distance": ["All"],
                "Freq": [t[9:12] + "Hz"],
                "Phase": ["0deg", "90deg"],
                "Coil_Excitation": ["All"],
            }
        report = m3d.post.create_report(
            plot_name=plot_name,
            report_category="Fields",
            context="Line_" + t[3:8],
            primary_sweep_variable="Distance",
            variations=variations,
            expressions=t[0:2],
        )
        file_path = os.path.join(temp_folder.name, str(dataset[i]) + ".csv")
        report.import_traces(input_file=file_path, plot_name=plot_name)

# Analyze project.

m3d.analyze(cores=NUM_CORES)

# ### Create plots of induced current and flux density on surface of plate
#
# Create two plots of the induced current (``Mag_J``) and the flux density (``Mag_B``) on the
# surface of the plate.

surf_list = m3d.modeler.get_object_faces(assignment="Plate")
intrinsic_dict = {"Freq": "200Hz", "Phase": "0deg"}
m3d.post.create_fieldplot_surface(
    assignment=surf_list,
    quantity="Mag_J",
    intrinsics=intrinsic_dict,
    plot_name="Mag_J",
)
m3d.post.create_fieldplot_surface(
    assignment=surf_list,
    quantity="Mag_B",
    intrinsics=intrinsic_dict,
    plot_name="Mag_B",
)
m3d.post.create_fieldplot_surface(
    assignment=surf_list, quantity="Mesh", intrinsics=intrinsic_dict, plot_name="Mesh"
)

# ## Finish
#
# ### Save the project

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
