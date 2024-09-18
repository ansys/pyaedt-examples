# # Maxwell 3D-Icepak electrothermal analysis
#
# This example uses PyAEDT to set up a simple Maxwell design consisting of a coil and a ferrite core.
# Coil current is set to 100A, and coil resistance and ohmic loss are analyzed.
# Ohmic loss is mapped to Icepak, and a thermal analysis is performed.
# Icepak calculates a temperature distribution, and it is mapped back to Maxwell (2-way coupling).
# Coil resistance and ohmic loss are analyzed again in Maxwell. Results are printed in AEDT Message Manager.
#
# Keywords: **Multiphysics**, **Maxwell**, **Icepak**, **Wireless Charging**.
#
# ## Perform imports and define constants
#
# Perform required imports.

import os
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.generic.constants import AXIS

# Define constants.

AEDT_VERSION = "2024.2"
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch application
#
# The syntax for different applications in AEDT differ
# only in the name of the class. This template uses
# the ``Hfss()`` class. Modify this text as needed.

# +
project_name = os.path.join(temp_folder.name, "Maxwell-Icepak-2way-Coupling")
maxwell_design_name = "1 Maxwell"
icepak_design_name = "2 Icepak"

m3d = ansys.aedt.core.Maxwell3d(
    project=project_name,
    design=maxwell_design_name,
    solution_type="EddyCurrent",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
)
# -

# ## Set up model
#
# Create the coil, coil terminal, core, and region.

# +
coil = m3d.modeler.create_rectangle(
    orientation="XZ", origin=[70, 0, -11], sizes=[11, 110], name="Coil"
)

coil.sweep_around_axis(axis=AXIS.Z)

coil_terminal = m3d.modeler.create_rectangle(
    orientation="XZ", origin=[70, 0, -11], sizes=[11, 110], name="Coil_terminal"
)

core = m3d.modeler.create_rectangle(
    orientation="XZ", origin=[45, 0, -18], sizes=[7, 160], name="Core"
)
core.sweep_around_axis(axis=AXIS.Z)

# Magnetic flux is not concentrated by the core in +z-direction. Therefore, more padding is needed in that direction.
region = m3d.modeler.create_region(pad_percent=[20, 20, 20, 20, 500, 100])
# -

# ### Create and assign material
#
# Create a new cooper material: Copper AWG40 Litz wire, strand diameter = 0.08mm,
# 24 parallel strands. Then assign materials: Assign the coil to AWG40 copper,
# the core to ferrite, and the region to vacuum.

# +
no_strands = 24
strand_diameter = 0.08

cu_litz = m3d.materials.duplicate_material("copper", "copper_litz")
cu_litz.stacking_type = "Litz Wire"
cu_litz.wire_diameter = str(strand_diameter) + "mm"
cu_litz.wire_type = "Round"
cu_litz.strand_number = no_strands

m3d.assign_material(region.name, "vacuum")
m3d.assign_material(coil.name, "copper_litz")
m3d.assign_material(core.name, "ferrite")
# -

# Assign coil current. The coil consists of 20 turns. The total current is 10A.
# Note that each coil turn consists of 24 parallel Litz strands as indicated earlier.

# +
no_turns = 20
coil_current = 10
m3d.assign_coil(["Coil_terminal"], conductors_number=no_turns, name="Coil_terminal")
m3d.assign_winding(is_solid=False, current=coil_current, name="Winding1")

m3d.add_winding_coils(assignment="Winding1", coils=["Coil_terminal"])
# -

# ## Assign mesh operations
#
# Mesh operations are not necessary in the eddy current solver because of auto-adaptive meshing.
# However, with appropriate mesh operations, less adaptive passes are needed

m3d.mesh.assign_length_mesh(
    ["Core"], maximum_length=15, maximum_elements=None, name="Inside_Core"
)
m3d.mesh.assign_length_mesh(
    ["Coil"], maximum_length=30, maximum_elements=None, name="Inside_Coil"
)

# Set conductivity as a function of temperature. Resistivity increases by 0.393% per K.

cu_resistivity_temp_coefficient = 0.00393
cu_litz.conductivity.add_thermal_modifier_free_form(
    "1.0/(1.0+{}*(Temp-20))".format(cu_resistivity_temp_coefficient)
)

# ## Set object temperature and enable feedback
#
# Set the temperature of the objects to the default temperature (22 degrees C)
# and enable temperature feedback for two-way coupling.

m3d.modeler.set_objects_temperature(["Coil"], ambient_temperature=22)

# ## Assign matrix
#
# Assign matrix for resistance and inductance calculation.

m3d.assign_matrix(["Winding1"], matrix_name="Matrix1")

# ## Create and analyze simulation setup
#
# The simulation frequency is 150 kHz.

setup = m3d.create_setup(name="Setup1")
setup.props["Frequency"] = "150kHz"
m3d.analyze_setup("Setup1")

# ## Postprocess
#
# Calculate analytical DC resistance and compare it with the simulated coil
# resistance. Print them in AEDT Message Manager, along with the ohmic loss in
# coil before the temperature feedback.

# +
report = m3d.post.create_report(expressions="Matrix1.R(Winding1,Winding1)")
solution = report.get_solution_data()
resistance = solution.data_magnitude()[0]

report_loss = m3d.post.create_report(expressions="StrandedLossAC")
solution_loss = report_loss.get_solution_data()
em_loss = solution_loss.data_magnitude()[0]

# Analytical calculation of the DC resistance of the coil
cu_cond = float(cu_litz.conductivity.value)
# Average radius of a coil turn = 0.125m
l_conductor = no_turns * 2 * 0.125 * 3.1415
# R = resistivity * length / area / no_strand
r_analytical_DC = (
    (1.0 / cu_cond)
    * l_conductor
    / (3.1415 * (strand_diameter / 1000 / 2) ** 2)
    / no_strands
)

# Print results in AEDT Message Manager
m3d.logger.info(
    "*******Coil analytical DC resistance =  {:.2f}Ohm".format(r_analytical_DC)
)
m3d.logger.info(
    "*******Coil resistance at 150kHz BEFORE temperature feedback =  {:.2f}Ohm".format(
        resistance
    )
)
m3d.logger.info(
    "*******Ohmic loss in coil BEFORE temperature feedback =  {:.2f}W".format(
        em_loss / 1000
    )
)
# -

# ## Insert Icepak design
#
# Insert Icepak design, copy solid objects from Maxwell 3D, and modify region dimensions.

# +
ipk = ansys.aedt.core.Icepak(design=icepak_design_name, version=AEDT_VERSION)
ipk.copy_solid_bodies_from(m3d, no_pec=False)

# Set domain dimensions suitable for natural convection using the diameter of the coil
ipk.modeler["Region"].delete()
coil_dim = coil.bounding_dimension[0]
ipk.modeler.create_region(0, False)
ipk.modeler.edit_region_dimensions(
    [coil_dim / 2, coil_dim / 2, coil_dim / 2, coil_dim / 2, coil_dim * 2, coil_dim]
)
# -

# ## Map coil losses
#
# Map ohmic losses from Maxwell 3D to the Icepak design.

ipk.assign_em_losses(
    design="1 Maxwell",
    setup=m3d.setups[0].name,
    sweep="LastAdaptive",
    assignment=["Coil"],
)

# ### Define boundary conditions
#
# Assign the opening.

faces = ipk.modeler["Region"].faces
face_names = [face.id for face in faces]
ipk.assign_free_opening(face_names, boundary_name="Opening1")

# ### Assign monitor
#
# Assign the temperature monitor on the coil surface.

temp_monitor = ipk.assign_point_monitor([70, 0, 0], monitor_name="PointMonitor1")

# Set up Icepak solution

solution_setup = ipk.create_setup()
solution_setup.props["Convergence Criteria - Max Iterations"] = 50
solution_setup.props["Flow Regime"] = "Turbulent"
solution_setup.props["Turbulent Model Eqn"] = "ZeroEquation"
solution_setup.props["Radiation Model"] = "Discrete Ordinates Model"
solution_setup.props["Include Flow"] = True
solution_setup.props["Include Gravity"] = True
solution_setup.props["Solution Initialization - Z Velocity"] = "0.0005m_per_sec"
solution_setup.props["Convergence Criteria - Flow"] = 0.0005
solution_setup.props["Flow Iteration Per Radiation Iteration"] = "5"

# ## Add two-way coupling and solve the project
#
# Enable mapping temperature distribution back to Maxwell 3D. The default number
# for Maxwell <–> Icepak iterations is 2. However, for increased accuracy,
# you can increate the value for the ``number_of_iterations`` parameter.

ipk.assign_2way_coupling()
ipk.analyze_setup(name=solution_setup.name)

# ## Postprocess
#
# Plot temperature on the object surfaces.

# +
surface_list = []
for name in ["Coil", "Core"]:
    surface_list.extend(ipk.modeler.get_object_faces(name))

surf_temperature = ipk.post.create_fieldplot_surface(
    surface_list, quantity="SurfTemperature", plot_name="Surface Temperature"
)

velocity_cutplane = ipk.post.create_fieldplot_cutplane(
    assignment=["Global:XZ"], quantity="Velocity Vectors", plot_name="Velocity Vectors"
)

surf_temperature.export_image()
velocity_cutplane.export_image(orientation="right")

report_temp = ipk.post.create_report(
    expressions="PointMonitor1.Temperature", primary_sweep_variable="X"
)
solution_temp = report_temp.get_solution_data()
temp = solution_temp.data_magnitude()[0]
m3d.logger.info("*******Coil temperature =  {:.2f}deg C".format(temp))
# -

# ### Get new resistance from Maxwell 3D
#
# The temperature of the coil increases, and consequently the coil resistance increases.

# +
report_new = m3d.post.create_report(expressions="Matrix1.R(Winding1,Winding1)")
solution_new = report_new.get_solution_data()
resistance_new = solution_new.data_magnitude()[0]
resistance_increase = (resistance_new - resistance) / resistance * 100

report_loss_new = m3d.post.create_report(expressions="StrandedLossAC")
solution_loss_new = report_loss_new.get_solution_data()
em_loss_new = solution_loss_new.data_magnitude()[0]

m3d.logger.info(
    "*******Coil resistance at 150kHz AFTER temperature feedback =  {:.2f}Ohm".format(
        resistance_new
    )
)
m3d.logger.info(
    "*******Coil resistance increased by {:.2f}%".format(resistance_increase)
)
m3d.logger.info(
    "*******Ohmic loss in coil AFTER temperature feedback =  {:.2f}W".format(
        em_loss_new / 1000
    )
)
# -

# ### Save project

ipk.save_project()
ipk.release_desktop()
time.sleep(3)  # Allow AEDT to shut down before cleaning the temporary project folder.

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes
# all temporary files, including the project folder.

temp_folder.cleanup()
