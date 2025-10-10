# # 3-Phase Cable with Neutral
#
# This example uses PyAEDT to create a 3-phase cable with neutral
# and solve it using Maxwell 2D AC Magnetic (Eddy Current) solver.
#
# Keywords: **Maxwell 2D**, **cable**, **3-phase**, **field calculator**, **field plot**

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

AEDT_VERSION = "2025.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT and Maxwell 2D
#
# Create an instance of the ``Maxwell2d`` class named ``m2d`` by providing
# the project and design names, the version, and the graphical mode.

project_name = os.path.join(temp_folder.name, "M2D_cable.aedt")
m2d = ansys.aedt.core.Maxwell2d(
    project=project_name,
    design="cable_maxwell_eddy",
    solution_type="AC MagneticXY",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Define modeler units

m2d.modeler.model_units = "mm"

# ## Add materials
#
# Add XLPE material for insulation.

xlpe = m2d.materials.add_material("XLPE")
xlpe.update()
xlpe.conductivity = "0"
xlpe.permittivity = "2.3"

# ## Create geometry of the cable and assign materials
#
# Create geometry of the 3-phase cable with neutral and assign materials.

# ### Create the cable shield

shield = m2d.modeler.create_circle(origin=[0, 0, 0], radius=8, name="Shield")
filler = m2d.modeler.create_circle(origin=[0, 0, 0], radius=7.5, name="Filler")
m2d.modeler.subtract(blank_list=shield.name, tool_list=filler.name)
shield.material_name = "aluminum"
filler.material_name = "polyethylene"
filler.color = [143, 175, 143]
filler.transparency = 0

# ### Create the cable inner conductors

phase_a = m2d.modeler.create_circle(origin=[5, 0, 0], radius=2.0575, material="copper")
cond = m2d.modeler.duplicate_around_axis(
    assignment=phase_a.name, axis="Z", angle=120, clones=3
)
phase_b = m2d.modeler[cond[1][0]]
phase_c = m2d.modeler[cond[1][1]]
phase_a.name = "PhaseA"
phase_a.color = [255, 0, 0]
phase_a.transparency = 0
phase_b.name = "PhaseB"
phase_b.color = [0, 0, 255]
phase_b.transparency = 0
phase_c.name = "PhaseC"
phase_c.color = [0, 255, 0]
phase_c.transparency = 0

# ### Create the cable inner conductor insulation

insul_a = m2d.modeler.create_circle(origin=[5, 0, 0], radius=2.25, material="XLPE")
insul_a.transparency = 0
insul = m2d.modeler.duplicate_around_axis(
    assignment=insul_a.name, axis="Z", angle=120, clones=3
)
insul_b = m2d.modeler[insul[1][0]]
insul_c = m2d.modeler[insul[1][1]]
insul_a.name = "InsulA"
insul_b.name = "InsulB"
insul_c.name = "InsulC"

# ### Create the cable neutral wire and its insulation

# +
neu_ins = m2d.modeler.duplicate_along_line(
    assignment=[phase_a.name, insul_a.name], vector=[-5, 0, 0], clones=2
)
phase_n = m2d.modeler[neu_ins[1][0]]
phase_n.name = "PhaseN"
phase_n.color = [128, 64, 64]
insul_n = m2d.modeler[neu_ins[1][1]]
insul_n.name = "InsulN"

m2d.modeler.subtract(blank_list=filler, tool_list=[insul_a, insul_b, insul_c, insul_n])
m2d.modeler.subtract(blank_list=insul_a, tool_list=phase_a.name)
m2d.modeler.subtract(blank_list=insul_b, tool_list=phase_b.name)
m2d.modeler.subtract(blank_list=insul_c, tool_list=phase_c.name)
m2d.modeler.subtract(blank_list=insul_n, tool_list=phase_n.name)
# -

# ## Create region
#
# Create the air region and assign boundary condition to it.

# +
region = m2d.modeler.create_region(pad_value=200)
m2d.assign_balloon(assignment=region.edges)

m2d.modeler.fit_all()
# -

# ## Assign excitations
#
# Set electrical excitations for the conductive objects.

winding_a = m2d.assign_winding(assignment=phase_a.name, current=200, name="PhaseA")
winding_b = m2d.assign_winding(
    assignment=phase_b.name, current=200, phase=-120, name="PhaseB"
)
winding_c = m2d.assign_winding(
    assignment=phase_c.name, current=200, phase=-240, name="PhaseC"
)
winding_n = m2d.assign_winding(assignment=phase_n.name, current=0, name="PhaseN")
winding_s = m2d.assign_winding(assignment=shield.name, current=0, name="Shield")

# ## Assign matrix
#
# Set matrix for RL parameters calculation.

m2d.assign_matrix(
    assignment=["PhaseA", "PhaseB", "PhaseC", "PhaseN", "Shield"], matrix_name="Matrix1"
)

# ## Assign mesh operation
#
# Assign surface approximation mesh to all objects.

m2d.mesh.assign_surface_mesh_manual(
    assignment=m2d.modeler.object_list, normal_dev="10deg"
)

# ## Analysis setup
#
# Set analysis setup to run the simulation.

setup = m2d.create_setup()
setup["MaximumPasses"] = 15
setup["PercentError"] = 0.1
setup["Frequency"] = "60Hz"

# ## Run the Maxwell 2D analysis
#
# The following command runs the 2D finite element analysis in Maxwell.

m2d.analyze_setup(name=setup.name)

# ## Field plots
#
# ### Plot the magnitude of magnetic flux density

plot1 = m2d.post.create_fieldplot_surface(
    assignment=m2d.modeler.object_list, quantity="Mag_B", plot_name="B"
)

# ### Add the expression for the current density absolute value using the advanced field calculator

j_abs = {
    "name": "Jabs",
    "description": "Absolute value of the current density",
    "design_type": ["Maxwell 2D"],
    "fields_type": ["Fields"],
    "primary_sweep": "",
    "assignment": "",
    "assignment_type": [""],
    "operations": [
        "Fundamental_Quantity('Jt')",
        "Operation('Smooth')",
        "Operation('ScalarZ')",
        "Scalar_Function(FuncValue='Phase')",
        "Operation('AtPhase')",
        "Operation('Abs')",
    ],
    "report": ["Field_2D"],
}
m2d.post.fields_calculator.add_expression(j_abs, None)

# ### Plot the absolute value of the current density in the conductive objects

plot2 = m2d.post.create_fieldplot_surface(
    assignment=[phase_a, phase_b, phase_c],
    quantity="Jabs",
    plot_name="Jabs_cond_3Phase",
)
plot3 = m2d.post.create_fieldplot_surface(
    assignment=[shield, phase_n], quantity="Jabs", plot_name="Jabs_shield_neutral"
)

# ## Release AEDT

m2d.save_project()
m2d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ### Clean up

# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
