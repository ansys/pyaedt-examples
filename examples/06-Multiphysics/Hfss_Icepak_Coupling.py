# # Multiphysics: HFSS-Icepak multiphysics analysis
#
# This example shows how you can create a project from scratch in HFSS and Icepak (linked to HFSS).
# This includes creating a setup, solving it, and creating postprocessing outputs.
#
# To provide the advanced postprocessing features needed for this example, the ``numpy``,
# ``matplotlib``, and ``pyvista`` packages must be installed on the machine.
#
# This examples runs only on Windows using CPython.

# ## Perform required imports
#
# Perform required imports.

import os
import tempfile
import time

from ansys.pyaedt.examples.constants import AEDT_VERSION, NUM_CORES
import pyaedt
from pyaedt.generic.pdf import AnsysReport

# ## Create temporary directory
#
# Create temporary directory.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Setup
#
# Set non-graphical mode.

non_graphical = False

# ## Launch AEDT and initialize HFSS
#
# Launch AEDT and initialize HFSS. If there is an active HFSS design, the ``hfss``
# object is linked to it. Otherwise, a new design is created.

hfss = pyaedt.Hfss(
    projectname=os.path.join(temp_dir.name, "Icepak_HFSS_Coupling"),
    designname="RF",
    specified_version=AEDT_VERSION,
    non_graphical=non_graphical,
    new_desktop_session=True,
)

# ## Parameters
#
# Parameters can be instantiated by defining them as a key used for the application
# instance as demonstrated below. The prefix ``$`` is used to define
# project-wide scope for the parameter. Otherwise the parameter scope is limited the current design.

hfss["$coax_dimension"] = "100mm"  # Project-wide scope.
udp = hfss.modeler.Position(0, 0, 0)
hfss["inner"] = "3mm"  # Local "Design" scope.

# ## Create coaxial and cylinders
#
# Create a coaxial and three cylinders. You can apply parameters
# directly using the `pyaedt.modeler.Primitives3D.Primitives3D.create_cylinder`
# method. You can assign a material directly to the object creation action.
# Optionally, you can assign a material using the `assign_material` method.

# TODO: How does this work when two true surfaces are defined?
o1 = hfss.modeler.create_cylinder(
    cs_axis=hfss.PLANE.ZX,
    position=udp,
    radius="inner",
    height="$coax_dimension",
    numSides=0,
    name="inner",
)
o2 = hfss.modeler.create_cylinder(
    cs_axis=hfss.PLANE.ZX,
    position=udp,
    radius=8,
    height="$coax_dimension",
    numSides=0,
    matname="teflon_based",
)
o3 = hfss.modeler.create_cylinder(
    cs_axis=hfss.PLANE.ZX,
    position=udp,
    radius=10,
    height="$coax_dimension",
    numSides=0,
    name="outer",
)

# ## Assign colors
#
# Assign colors to each primitive.

o1.color = (255, 0, 0)
o2.color = (0, 255, 0)
o3.color = (255, 0, 0)
o3.transparency = 0.8
hfss.modeler.fit_all()

# ## Assign materials
#
# Assign materials. You can assign materials either directly when creating the primitive,
# which was done for ``id2``, or after the object is created.

o1.material_name = "Copper"
o3.material_name = "Copper"

# ## Perform modeler operations
#
# Perform modeler operations. You can subtract, add, and perform other operations
# using either the object ID or object name.

hfss.modeler.subtract(o3, o2, True)
hfss.modeler.subtract(o2, o1, True)

# ## Assign Mesh Operations
#
# Most mesh operations are accessible using the ``mesh`` property
# which is an instance of the ``pyaedt.modules.MeshIcepak.IcepakMesh`` class.
#
# This example demonstrates the use of several common mesh
# operations.

hfss.mesh.assign_initial_mesh_from_slider(level=6)
hfss.mesh.assign_model_resolution(names=[o1.name, o3.name], defeature_length=None)
hfss.mesh.assign_length_mesh(names=o2.faces, isinside=False, maxlength=1, maxel=2000)

# ## Create HFSS Sources
#
# The RF power dissipated in the HFSS model will act as the thermal
# source for in Icepak. The ``create_wave_port_between_objects`` method
# s used to assign the RF ports that inject RF power into the HFSS
# model. If the parameter ``add_pec_cap=True``, then the method
# creates a perfectly conducting (lossless) cap covering the port.

# +
hfss.wave_port(
    signal="inner",
    reference="outer",
    integration_line=1,
    create_port_sheet=True,
    create_pec_cap=True,
    name="P1",
)

hfss.wave_port(
    signal="inner",
    reference="outer",
    integration_line=4,
    create_pec_cap=True,
    create_port_sheet=True,
    name="P2",
)

port_names = hfss.get_all_sources()
hfss.modeler.fit_all()
# -

# ## HFSS Simulation Setup
#
# Create a setup. A setup is created with default values. After its creation,
# you can change values and update the setup. The ``update`` method returns a Boolean
# value.

hfss.set_active_design(hfss.design_name)
setup = hfss.create_setup("MySetup")
setup.props["Frequency"] = "1GHz"
setup.props["BasisOrder"] = 2
setup.props["MaximumPasses"] = 1

# ## HFSS Frequency Sweep
#
# The frequency sweep defines the RF frequency range over which the RF power is
# injected into the structure.

sweepname = hfss.create_linear_count_sweep(
    setupname="MySetup",
    unit="GHz",
    freqstart=0.8,
    freqstop=1.2,
    num_of_freq_points=401,
    sweep_type="Interpolating",
)

# ## Create Icepak model
#
# After an HFSS setup has been defined, the model can be lnked to an Icepak
# design and the coupled physics analysis can be run. The `FieldAnalysis3D.copy_solid_bodies_from()`
# method imports a model from HFSS into Icepak including all material definitions.

ipk = pyaedt.Icepak(designname="CalcTemp")
ipk.copy_solid_bodies_from(hfss)

# ## Link RF Thermal Source
#
# The RF loss in HFSS will be used as the thermal source in Icepak.

surfaceobj = ["inner", "outer"]
ipk.assign_em_losses(
    designname=hfss.design_name,
    setupname="MySetup",
    sweepname="LastAdaptive",
    map_frequency="1GHz",
    surface_objects=surfaceobj,
    paramlist=["$coax_dimension", "inner"],
)

# ## Assign the Direction of Gravity
#
# Set the direction of gravity for convection in Icepak. Gravity drives a temperature gradient
# due to the dependence of gas density on temperature.

ipk.edit_design_settings(hfss.GRAVITY.ZNeg)

# ## Set up the Icepak Project
#
# The initial solution setup applies default values that can subsequently
# be modified as shown here.
# The ``props`` property enables access to all solution settings.
#
# The ``update`` function
# applies the settings to the setup. The setup creation process is identical
# for all tools.

setup_ipk = ipk.create_setup("SetupIPK")
setup_ipk.props["Convergence Criteria - Max Iterations"] = 3

# ### Icepak Solution Properties
#
# The setup properties are accessible through the ``props`` property as
# an ordered dict. The ``keys()`` method can be used to retrieve all settings for
# the setup.
#
# Find properties that contain the string ``"Convergence"`` and print the default values.

conv_props = [k for k in setup_ipk.props.keys() if "Convergence" in k]
print("Here are some default setup properties:")
for p in conv_props:
    print('"' + p + '" -> ' + str(setup_ipk.props[p]))

# ### Edit or Review Mesh Parameters
#
# Edit or review the mesh parameters. After a mesh is created, you can access
# a mesh operation to edit or review parameter values.

airbox = ipk.modeler.get_obj_id("Region")
ipk.modeler[airbox].display_wireframe = True
airfaces = ipk.modeler.get_object_faces(airbox)
ipk.assign_openings(airfaces)

# Save project and attach to Icepak instance

hfss.save_project()
ipk = pyaedt.Icepak()
ipk.solution_type = ipk.SOLUTIONS.Icepak.SteadyTemperatureAndFlow
ipk.modeler.fit_all()

# ## Solve the Project
#
# Solve the Icepak and HFSS models.

ipk.setups[0].analyze(num_cores=NUM_CORES)
hfss.save_project()
hfss.modeler.fit_all()
hfss.setups[0].analyze()

# ### Plot and Export Results
#
# Generate field plots in the HFSS project and export them as images.

# +
quantity_name = "ComplexMag_H"
intrinsic = {"Freq": hfss.setups[0].props["Frequency"], "Phase": "0deg"}
surface_list = hfss.modeler.get_object_faces("outer")
plot1 = hfss.post.create_fieldplot_surface(
    objlist=surface_list,
    quantityName=quantity_name,
    setup_name=hfss.nominal_adaptive,
    intrinsincDict=intrinsic,
)

hfss.post.plot_field_from_fieldplot(
    plot1.name,
    project_path=temp_dir.name,
    meshplot=False,
    imageformat="jpg",
    view="isometric",
    show=False,
    plot_cad_objs=False,
    log_scale=False,
    file_format="aedtplt",
)
# -

# ## Generate animation from field plots
#
# Generate an animation from field plots using PyVista.

# +
start = time.time()
cutlist = ["Global:XY"]
phase_values = [str(i * 5) + "deg" for i in range(18)]

animated = hfss.post.plot_animated_field(
    quantity="Mag_E",
    object_list=cutlist,
    plot_type="CutPlane",
    setup_name=hfss.nominal_adaptive,
    intrinsics=intrinsic,
    export_path=temp_dir.name,
    variation_variable="Phase",
    variation_list=phase_values,
    show=False,
    export_gif=False,
    log_scale=True,
)
animated.gif_file = os.path.join(temp_dir.name, "animate.gif")

# Set off_screen to False to visualize the animation.
# animated.off_screen = False

animated.animate()

end_time = time.time() - start
print("Total Time", end_time)
# -

# ## Create Icepak plots and export
#
# Create Icepak plots and export them as images using the same functions that
# were used early. Only the quantity is different.

# +
setup_name = ipk.existing_analysis_sweeps[0]
intrinsic = ""
surface_list = ipk.modeler.get_object_faces("inner") + ipk.modeler.get_object_faces("outer")
plot5 = ipk.post.create_fieldplot_surface(surface_list, quantityName="SurfTemperature")

hfss.save_project()
# -

# ## Generate plots outside AEDT
#
# Generate plots outside AEDT using Matplotlib and NumPy.

trace_names = hfss.get_traces_for_plot(category="S")
context = ["Domain:=", "Sweep"]
families = ["Freq:=", ["All"]]
my_data = hfss.post.get_solution_data(expressions=trace_names)
my_data.plot(
    trace_names,
    math_formula="db20",
    xlabel="Frequency (Ghz)",
    ylabel="SParameters(dB)",
    title="Scattering Chart",
    snapshot_path=os.path.join(temp_dir.name, "Touchstone_from_matplotlib.jpg"),
)

# ## Generate PDF pdf_report
#
# Generate a PDF pdf_report with simulation results.
pdf_report = AnsysReport(
    project_name=hfss.project_name, design_name=hfss.design_name, version=AEDT_VERSION
)

# Create report

pdf_report.create()

# Add section for plots

pdf_report.add_section()
pdf_report.add_chapter("Hfss Results")
pdf_report.add_sub_chapter("Field Plot")
pdf_report.add_text("This section contains Field plots of Hfss Coaxial.")
pdf_report.add_image(os.path.join(temp_dir.name, plot1.name + ".jpg"), caption="Coaxial Cable")

# Add a page break and a subchapter for S Parameter results

pdf_report.add_page_break()
pdf_report.add_sub_chapter("S Parameters")
pdf_report.add_chart(
    x_values=my_data.intrinsics["Freq"],
    y_values=my_data.data_db20(),
    x_caption="Freq",
    y_caption=trace_names[0],
    title="S-Parameters",
)
pdf_report.add_image(
    path=os.path.join(temp_dir.name, "Touchstone_from_matplotlib.jpg"),
    caption="Touchstone from Matplotlib",
)

# Add a new section for Icepak results

pdf_report.add_section()
pdf_report.add_chapter("Icepak Results")
pdf_report.add_sub_chapter("Temperature Plot")
pdf_report.add_text("This section contains Multiphysics temperature plot.")

# Add table of content and save PDF.

pdf_report.add_toc()
pdf_report.save_pdf(file_path=temp_dir.name, file_name="AEDT_Results.pdf")

# ## Release AEDT and clean up temporary directory
#
# Release AEDT and clean up temporary directory.

hfss.release_desktop()
temp_dir.cleanup()
