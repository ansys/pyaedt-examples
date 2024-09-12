# # Spiral inductor
#
# This example shows how to use PyAEDT to create a spiral inductor, solve it, and plot results.
#
# Keywords: **HFSS**, **spiral**, **inductance**, **output variable**.

# ## Perform imports and define constants
#
# Perform required imports.

import os
import tempfile
import time

import ansys.aedt.core

# Define constants.

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch HFSS
#
# Create an HFSS design and change the units to microns.

project_name = os.path.join(temp_folder.name, "spiral.aedt")
hfss = ansys.aedt.core.Hfss(
    project=project_name,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    design="A1",
    new_desktop=True,
    solution_type="Modal",
)
hfss.modeler.model_units = "um"

# ## Define variables
#
# Define input variables. You can use the values that follow or edit
# them.

rin = 10
width = 2
spacing = 1
thickness = 1
Np = 8
Nr = 10
gap = 3
hfss["Tsub"] = "6" + hfss.modeler.model_units

# ## Standardize polyline
#
# Define a function that creates a polyline using the ``create_line()`` method. This
# function creates a polyline having a fixed width, thickness, and material.


def create_line(pts):
    hfss.modeler.create_polyline(
        pts,
        xsection_type="Rectangle",
        xsection_width=width,
        xsection_height=thickness,
        material="copper",
    )


# ## Create spiral inductor
#
# Create the spiral inductor. This spiral inductor is not
# parametric, but you could parametrize it later.

ind = hfss.modeler.create_spiral(
    internal_radius=rin,
    width=width,
    spacing=spacing,
    turns=Nr,
    faces=Np,
    thickness=thickness,
    material="copper",
    name="Inductor1",
)


# ## Center return path
#
# Center the return path.

x0, y0, z0 = ind.points[0]
x1, y1, z1 = ind.points[-1]
create_line([(x0 - width / 2, y0, -gap), (abs(x1) + 5, y0, -gap)])
hfss.modeler.create_box(
    [x0 - width / 2, y0 - width / 2, -gap - thickness / 2],
    [width, width, gap + thickness],
    matname="copper",
)

# Create port 1.

hfss.modeler.create_rectangle(
    orientation=ansys.aedt.core.constants.PLANE.YZ,
    origin=[abs(x1) + 5, y0 - width / 2, -gap - thickness / 2],
    sizes=[width, "-Tsub+{}{}".format(gap, hfss.modeler.model_units)],
    name="port1",
)
hfss.lumped_port(assignment="port1", integration_line=ansys.aedt.core.constants.AXIS.Z)

# Create port 2.

create_line([(x1 + width / 2, y1, 0), (x1 - 5, y1, 0)])
hfss.modeler.create_rectangle(
    ansys.aedt.core.constants.PLANE.YZ,
    [x1 - 5, y1 - width / 2, -thickness / 2],
    [width, "-Tsub"],
    name="port2",
)
hfss.lumped_port(assignment="port2", integration_line=ansys.aedt.core.constants.AXIS.Z)

# Create the silicon substrate and the ground plane.

# +
hfss.modeler.create_box(
    [x1 - 20, x1 - 20, "-Tsub-{}{}/2".format(thickness, hfss.modeler.model_units)],
    [-2 * x1 + 40, -2 * x1 + 40, "Tsub"],
    material="silicon",
)

hfss.modeler.create_box(
    [x1 - 20, x1 - 20, "-Tsub-{}{}/2".format(thickness, hfss.modeler.model_units)],
    [-2 * x1 + 40, -2 * x1 + 40, -0.1],
    material="PEC",
)
# -

# ## set up model
#
# Create the air box and radiation boundary condition.

# +
box = hfss.modeler.create_box(
    [
        x1 - 20,
        x1 - 20,
        "-Tsub-{}{}/2 - 0.1{}".format(
            thickness, hfss.modeler.model_units, hfss.modeler.model_units
        ),
    ],
    [-2 * x1 + 40, -2 * x1 + 40, 100],
    name="airbox",
    material="air",
)

hfss.assign_radiation_boundary_to_objects("airbox")
# -

# Assign a material override that allows object intersections,
# assigning conductors higher priority than insulators.

hfss.change_material_override()

# View the model.

hfss.plot(
    show=False,
    output_file=os.path.join(hfss.working_directory, "Image.jpg"),
    plot_air_objects=False,
)

# ## Generate the solution
#
# Create the setup, including a frequency sweep. Then, solve the project.

setup1 = hfss.create_setup(name="setup1")
setup1.props["Frequency"] = "10GHz"
hfss.create_linear_count_sweep(
    setup="setup1",
    units="GHz",
    start_frequency=1e-3,
    stop_frequency=50,
    num_of_freq_points=451,
    sweep_type="Interpolating",
)
hfss.save_project()
hfss.analyze(cores=NUM_CORES)

# ## Postprocess
#
# Get report data and use the following formulas to calculate
# the inductance and quality factor.

L_formula = "1e9*im(1/Y(1,1))/(2*pi*freq)"
Q_formula = "im(Y(1,1))/re(Y(1,1))"

# Define the inductance as a postprocessing variable.

hfss.create_output_variable("L", L_formula, solution="setup1 : LastAdaptive")

# Plot the results using Matplotlib.

data = hfss.post.get_solution_data([L_formula, Q_formula])
data.plot(
    curves=[L_formula, Q_formula], formula="re", x_label="Freq", y_label="L and Q"
)

# Export results to a CSV file

data.export_data_to_csv(os.path.join(hfss.toolkit_directory, "output.csv"))

# ## Save project and close AEDT
#
# Save the project and close AEDT.

hfss.save_project()
hfss.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes
# all temporary files, including the project folder.

temp_folder.cleanup()
