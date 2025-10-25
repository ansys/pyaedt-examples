# # Maxwell 3D-Icepak electrothermal analysis
#
# This example uses PyAEDT to set up a simple Maxwell design consisting of a coil and a ferrite core.
# Coil current is set to 100A, and coil resistance and ohmic loss are analyzed.
# Ohmic loss is mapped to Icepak, and a thermal analysis is performed.
# Icepak calculates a temperature distribution, and it is mapped back to Maxwell (2-way coupling).
# Coil resistance and ohmic loss are analyzed again in Maxwell. Results are printed in AEDT Message Manager.
#
# Keywords: **Multiphysics**, **Maxwell**, **Icepak**, **Wireless Charging**.

# ## Prerequisites
#
# ### Perform imports

# +
import os
import tempfile
import time

import ansys.aedt.core  # Interface to Ansys Electronics Desktop
from ansys.aedt.core.generic.constants import Axis
# -

# ### Define constants
#
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.2"
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in this example removes the temporary folder and
# > all contents. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ### Launch application
#
# The syntax for different applications in AEDT differ
# only in the name of the class. This example demonstrates the use of the
# ``Maxwell3d`` and ``Icepak`` classes.
#
# > **Note:** An AEDT _Project_ is created when the ``Maxwell3d`` class is instantiated. An instance of
# > the ``Icepak`` class will be used later to insert and simulate an
# > Icepak design to demonstrate
# > the coupled electrical-thermal workflow.

# +
maxwell_design_name = "1 Maxwell"
icepak_design_name = "2 Icepak"

project_name = os.path.join(temp_folder.name, "Maxwell-Icepak-2way-Coupling")

m3d = ansys.aedt.core.Maxwell3d(
    project=project_name,
    design=maxwell_design_name,
    solution_type="EddyCurrent",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
)
# -

# ## Model Preparation
#
# ### Build the model
#
# Create the coil, coil terminal, core, and surrounding air region. The coil and core
# are created by drawing a rectangle and sweeping it about the z-axis.

# +
coil_origin = [70, 0, -11]  # [x, y, z] position of the rectangle origin.
coil_xsection = [11, 110]  # [z-size, x-size]
core_origin = [45, 0, -18]
core_xsection = [7, 160]

coil = m3d.modeler.create_rectangle(
    orientation="XZ", origin=coil_origin, sizes=coil_xsection, name="Coil"
)
coil.sweep_around_axis(axis=Axis.Z)
coil_terminal = m3d.modeler.create_rectangle(
    orientation="XZ", origin=coil_origin, sizes=coil_xsection, name="Coil_terminal"
)

core = m3d.modeler.create_rectangle(
    orientation="XZ", origin=core_origin, sizes=core_xsection, name="Core"
)
core.sweep_around_axis(axis=Axis.Z)

# The air region should be sufficiently large to avoid interaction with the
# coil magnetic field.

region = m3d.modeler.create_region(pad_percent=[20, 20, 20, 20, 500, 100])
# -

# #### Restore view
#
# If you are using PyAEDT with an interactive desktop, you may want to fit the visible view to fit the model.
# PyAEDT allows direct access to the native API for this command using the property `m3d.odesktop`.
#
# Uncomment and run the following cell if you are running PyAEDT interactively and would like to automatically fit the
# window to the model.
#
# > **Note:** Native API calls do not allow for introspection or follow PIP
# > syntax guidelines. Full documentation for the native API is available in
# > the built-in AEDT [help](https://ansyshelp.ansys.com/account/secured?returnurl=/Views/Secured/Electronics/v242/en//Subsystems/Maxwell/Subsystems/Maxwell%20Scripting/Maxwell%20Scripting.htm).

# +
# desktop=m3d.odesktop.RestoreWindow()  # Fit the active view
# desktop = m3d.post.still_focus_oneditor()
# -

# ### Create and assign material
#
# Define a new material for the AWG40 Litz wire copper strands:
#
# - Strand diameter = 0.08 mm
# - Number of parallel strands in the Litz wire = 24
#
# The built-in material "ferrite" will be assigned to the core.
# The material "vacuum" will be assigned to the outer region.
#
# You will also see the return value when
#  ``True`` printed when material is successfully assigned.

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

# ### Define the source
#
# The coil carries 0.5 A and 20 turns.

# +
turns = 20
wire_current = 0.5
m3d.assign_coil(["Coil_terminal"], conductors_number=turns, name="Coil_terminal")
m3d.assign_winding(is_solid=False, current=wire_current * turns, name="Winding1")

m3d.add_winding_coils(assignment="Winding1", coils=["Coil_terminal"])
# -

# ### Assign mesh operations
#
# Mesh "seeding" is used to accelerate the auto-adaptive mesh refinement.

m3d.mesh.assign_length_mesh(
    ["Core"], maximum_length=15, maximum_elements=None, name="Inside_Core"
)
m3d.mesh.assign_length_mesh(
    ["Coil"], maximum_length=30, maximum_elements=None, name="Inside_Coil"
)

# ### Set object temperature and enable feedback
#
# The impact of Joule heating on conductivity can be considered
# by adding a "thermal modifier" to the ``cu_litz`` material definition.
# In this example, conductivity increases by 0.393% per $\Delta^o$C. The temperature of the objects is set to the default value ($22^o$C).

cu_resistivity_temp_coefficient = 0.00393
cu_litz.conductivity.add_thermal_modifier_free_form(
    "1.0/(1.0+{}*(Temp-20))".format(cu_resistivity_temp_coefficient)
)
m3d.modeler.set_objects_temperature(["Coil"], ambient_temperature=22)

# ### Assign the matrix calculation to the winding
#
# The resistance and inductance calculations for the coil are enabled by
# adding the matrix assignment to the winding.

m3d.assign_matrix(["Winding1"], matrix_name="Matrix1")

# ### Create the simulation setup
#
# The simulation frequency is 150 kHz. You can query and modify the properties of the simulation setup using ``setup.props``. The "PercentError" establishes the minimum allowed change in energy due to the change in mesh size and ensure a small global solution error.

setup = m3d.create_setup(name="Setup1")
setup.props["Frequency"] = "150kHz"
setup.props["MaximumPasses"] = 4
setup.props["PercentError"] = 0.5
setup.props["MinimumConvergedPasses"] = 2

# ### Run the Maxwell 3D analysis
#
# The following command runs the 3D finite element analysis in Maxwell.

m3d.analyze_setup("Setup1")

# ## Postprocessing
#
# ### DC resistance
#
# The DC resistance of the coil can be calculated analyticially. The following cell compares the known
# DC resistance with the simulated coil
# resistance.
#
# The values can be displayed in the AEDT "Message Manager". The Ohmic loss in
# coil is calculated and displayed so we can see the change when Joule
# heating is considered.

# +
report = m3d.post.create_report(expressions="Matrix1.R(Winding1,Winding1)")
solution = report.get_solution_data()
resistance = solution.get_expression_data(formula="magnitude")[0][0]  # Resistance is the first matrix element.

report_loss = m3d.post.create_report(expressions="StrandedLossAC")
solution_loss = report_loss.get_solution_data()
em_loss = solution_loss.get_expression_data(formula="magnitude")[0][0]
# -

# ### Analyitic calculation of DC resistance

# +
cu_cond = float(cu_litz.conductivity.value)

# Average radius of a coil turn = 125 mm
avg_coil_radius = (
    coil_xsection[1] / 2 + coil_origin[0] / 2
) * 0.001  # Convert to meters
l_conductor = turns * 2 * avg_coil_radius * 3.1415

# R = resistivity * length / area / no_strand
r_analytic_DC = (
    (1.0 / cu_cond)
    * l_conductor
    / (3.1415 * (strand_diameter * 0.001 / 2) ** 2)
    / no_strands
)

# Print results in AEDT Message Manager
m3d.logger.info(f"*******Coil analytical DC resistance =  {r_analytic_DC:.2f}Ohm")
m3d.logger.info(
    f"*******Coil resistance at 150kHz BEFORE temperature feedback =  {resistance:.2f}Ohm"
)
m3d.logger.info(
    f"*******Ohmic loss in coil BEFORE temperature feedback =  {em_loss / 1000:.2f}W"
)
# -

# ## Create the thermal model
#
# The following commands insert an Icepak design into the AEDT project, copies the solid objects from Maxwell 3D, and modifies the region dimensions so they're suitable
# for thermal convection analysis.

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

# ### Map coil losses
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
# Assign the opening in the Icepak model to allow free airflow.

faces = ipk.modeler["Region"].faces
face_names = [face.id for face in faces]
ipk.assign_free_opening(face_names, boundary_name="Opening1")

# ### Assign monitor
#
# Assign a temperature monitor on the coil surface.

temp_monitor = ipk.assign_point_monitor([70, 0, 0], monitor_name="PointMonitor1")

# ### Set up Icepak solution
#
# Icepak solution settings are modified by updating the ``props`` associated with the solution setup.

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

# ### Add two-way coupling
#
# The temperature update from Icepak to Maxwell 3D is activated using the method ``assign_2way_coupling()``. The Ohmic
# loss in Maxwell will change due to the temperature increase, which in turn will change the results
# from the Icepak simulation. By default, this iteration occurs twice. However, the named argument
# ``number_of_iterations`` can be passed to the ``assign_2way_coupling`` method to increase the number of iterations.
#
# The full electro-thermal analysis is run by calling the ``analyze_setup()`` method.

ipk.assign_2way_coupling()

# ### Run Icepak analysis

ipk.analyze_setup(name=solution_setup.name)

# ## Postprocess
#
# Plot the temperature on object surfaces.

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
temp = solution_temp.get_expression_data(formula="magnitude")[1][0]
m3d.logger.info("*******Coil temperature =  {:.2f}deg C".format(temp))
# -

# ### Get updated resistance from Maxwell 3D
#
# The temperature of the coil increases, and consequently the coil resistance increases.

# +
report_new = m3d.post.create_report(expressions="Matrix1.R(Winding1,Winding1)")
solution_new = report_new.get_solution_data()
resistance_new = solution_new.get_expression_data(formula="magnitude")[1][0]
resistance_increase = (resistance_new - resistance) / resistance * 100

report_loss_new = m3d.post.create_report(expressions="StrandedLossAC")
solution_loss_new = report_loss_new.get_solution_data()
em_loss_new = solution_loss_new.get_expression_data(formula="magnitude")[1][0]

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

# ### Save the project

ipk.save_project()
ipk.release_desktop()
time.sleep(3)  # Allow AEDT to shut down before cleaning the temporary project folder.

# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
