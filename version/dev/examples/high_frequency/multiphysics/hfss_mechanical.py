# # HFSS-Mechanical multiphysics analysis
#
# This example shows how to use PyAEDT to create a multiphysics workflow that
# includes Circuit, HFSS, and Mechanical.
#
# Keywords: **Multiphysics**, **HFSS**, **Mechanical AEDT**, **Circuit**.

# ## Perform imports and define constants
#
# Perform required imports.

# +
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_via_wizard
# -

# Define constants.

AEDT_VERSION = "2025.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download and open project
#
# Download and open the project. Save it to the temporary folder.

project_name = download_via_wizard(
    local_path=temp_folder.name
)

# ## Start HFSS
#
# Initialize HFSS.

hfss = ansys.aedt.core.Hfss(
    project=project_name,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)
hfss.change_material_override(True)

# ## Initialize Circuit
#
# Initialize Circuit and add the HFSS dynamic link component.

circuit = ansys.aedt.core.Circuit(version=AEDT_VERSION)
hfss_comp = circuit.modeler.schematic.add_subcircuit_dynamic_link(pyaedt_app=hfss)

# ## Set up dynamic link options
#
# Set up dynamic link options. The argument for the ``set_sim_option_on_hfss_subcircuit()``
# method can be the component name, component ID, or component object.

circuit.modeler.schematic.refresh_dynamic_link(name=hfss_comp.composed_name)
circuit.modeler.schematic.set_sim_option_on_hfss_subcircuit(component=hfss_comp)
hfss_setup_name = hfss.setups[0].name + " : " + hfss.setups[0].sweeps[0].name
circuit.modeler.schematic.set_sim_solution_on_hfss_subcircuit(
    component=hfss_comp.composed_name, solution_name=hfss_setup_name
)

# ## Create ports and excitations
#
# Create ports and excitations. Find component pin locations and create interface
# ports on them. Define the voltage source on the input port.

# +
circuit.modeler.schematic.create_interface_port(
    name="Excitation_1",
    location=[hfss_comp.pins[0].location[0], hfss_comp.pins[0].location[1]],
)
circuit.modeler.schematic.create_interface_port(
    name="Excitation_2",
    location=[hfss_comp.pins[1].location[0], hfss_comp.pins[1].location[1]],
)
circuit.modeler.schematic.create_interface_port(
    name="Port_1",
    location=[hfss_comp.pins[2].location[0], hfss_comp.pins[2].location[1]],
)
circuit.modeler.schematic.create_interface_port(
    name="Port_2",
    location=[hfss_comp.pins[3].location[0], hfss_comp.pins[3].location[1]],
)

ports_list = ["Excitation_1", "Excitation_2"]
source = circuit.assign_voltage_sinusoidal_excitation_to_ports(ports_list)
source.ac_magnitude = 1
source.phase = 0
# -

# ## Create setup

setup_name = "MySetup"
LNA_setup = circuit.create_setup(name=setup_name)
sweep_list = ["LINC", str(4.3) + "GHz", str(4.4) + "GHz", str(1001)]
LNA_setup.props["SweepDefinition"]["Data"] = " ".join(sweep_list)

# ## Solve and push excitations
#
# Solve the circuit and push excitations to the HFSS model to calculate the
# correct value of losses.

circuit.analyze(cores=NUM_CORES)
circuit.push_excitations(instance="S1", setup=setup_name)

# ## Start Mechanical
#
# Start Mechanical and copy bodies from the HFSS project.

mech = ansys.aedt.core.Mechanical(version=AEDT_VERSION)
mech.copy_solid_bodies_from(design=hfss)
mech.change_material_override(True)

# ## Get losses from HFSS and assign convection to Mechanical

mech.assign_em_losses(
    design=hfss.design_name,
    setup=hfss.setups[0].name,
    sweep="LastAdaptive",
    map_frequency=hfss.setups[0].props["Frequency"],
    surface_objects=hfss.get_all_conductors_names(),
)
diels = ["1_pd", "2_pd", "3_pd", "4_pd", "5_pd"]
for el in diels:
    mech.assign_uniform_convection(
        assignment=[mech.modeler[el].top_face_y, mech.modeler[el].bottom_face_y],
        convection_value=3,
    )

# ## Solve and plot thermal results

mech.create_setup()
mech.save_project()
mech.analyze(cores=NUM_CORES)
surfaces = []
for name in mech.get_all_conductors_names():
    surfaces.extend(mech.modeler.get_object_faces(name))
mech.post.create_fieldplot_surface(assignment=surfaces, quantity="Temperature")

# ## Release AEDT
#
# Release AEDT and close the example.

mech.save_project()
mech.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``. If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
