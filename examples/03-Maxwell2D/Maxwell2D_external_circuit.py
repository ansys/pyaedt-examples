# # External circuit
#
# This example shows how to create an external delta circuit and connect it with a Maxwell 2D design.
# Keywords:

# ## Perform required imports

import os
import tempfile
import time

import ansys.aedt.core

# ## Define constants

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory and download files
#
# Create a temporary directory where we store downloaded data or
# dumped data.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT and Maxwell 2D
#
# Launch AEDT and Maxwell 2D providing the version, path to the project and the graphical mode.

project_name = os.path.join(temp_folder.name, "Maxwell_circuit_example.aedt")
design_name = "1 Maxwell"
circuit_name = "2 Delta circuit"

m2d = ansys.aedt.core.Maxwell2d(
    version=AEDT_VERSION,
    new_desktop=False,
    design=design_name,
    project=project_name,
    solution_type="TransientXY",
    non_graphical=NG_MODE,
)

# ## Initialize dictionaries and define variables
#
# Initialize dictionaries that contain all design variables definitions.

voltage = "230V"
frequency = "50Hz"

transient_parameters = {
    "voltage": voltage,
    "frequency": frequency,
    "electric_period": "1 / frequency s",
    "stop_time": "2 * electric_period s",
    "time_step": "electric_period / 20 s",
}

circuit_parameters = {
    "voltage": voltage,
    "frequency": frequency,
    "resistance_value": "1Ohm",
}

for k, v in transient_parameters.items():
    m2d[k] = v

# ## Create geometry
#
# Create copper coils and vacuum region, assign mesh operations, and assign balloon boundary to the region edges.

coil1_id = m2d.modeler.create_circle(
    orientation="Z", origin=[0, 0, 0], radius=10, name="coil1", material="copper"
)
coil2_id = m2d.modeler.create_circle(
    orientation="Z", origin=[25, 0, 0], radius=10, name="coil2", material="copper"
)
coil3_id = m2d.modeler.create_circle(
    orientation="Z", origin=[50, 0, 0], radius=10, name="coil3", material="copper"
)

region = m2d.modeler.create_region(pad_value=[100, 300, 100, 300])

m2d.mesh.assign_length_mesh(
    assignment=[coil1_id, coil2_id, coil3_id, region], maximum_length=5
)

m2d.assign_balloon(assignment=region.edges)

# ## Assign excitations
#
# Assign external windings

wdg1 = m2d.assign_winding(
    assignment=["coil1"],
    is_solid=False,
    winding_type="External",
    name="winding1",
    current=0,
)
wdg2 = m2d.assign_winding(
    assignment=["coil2"],
    is_solid=False,
    winding_type="External",
    name="winding2",
    current=0,
)
wdg3 = m2d.assign_winding(
    assignment=["coil3"],
    is_solid=False,
    winding_type="External",
    name="winding3",
    current=0,
)

# ## Create simulation setup
#
# Create simulation setup defining stop time and time step

setup = m2d.create_setup()
setup["StopTime"] = "stop_time"
setup["TimeStep"] = "time_step"

# ## Create external circuit
#
# Create circuit design including all the windings of type ``External`` in the Maxwell design.

circuit = m2d.create_external_circuit(circuit_design=circuit_name)

# ## Define variables from dictionaries
#
# Define design variables from the created dictionaries.

for k, v in circuit_parameters.items():
    circuit[k] = v

windings = [
    circuit.modeler.schematic.components[k]
    for k in list(circuit.modeler.schematic.components.keys())
    if circuit.modeler.schematic.components[k].parameters["Info"] == "Winding"
]

# ## Finalize external circuit
#
# Draw other components: Resistances, voltage sources, and grounds

circuit.modeler.schematic_units = "mil"

resistors = []
v_sources = []
ground = []

for i in range(3):
    resistors[i] = circuit.modeler.schematic.create_resistor(
        name="R" + str(i + 1), value="resistance_value", location=[1000, i * 1000]
    )

    v_sources[i] = circuit.modeler.schematic.create_component(
        component_library="Sources",
        component_name="VSin",
        location=[2000, i * 1000],
        angle=90,
    )
    v_sources[i].set_property(name="Va", value="voltage")
    v_sources[i].set_property(name="VFreq", value="frequency")
    v_sources[i].set_property(name="Phase", value=str(i * 120) + "deg")
    ground[i] = circuit.modeler.schematic.create_gnd([2300, i * 1000], angle=90)

# ## Connect the components
#
# Connect components by drawing wires

windings[2].pins[1].connect_to_component(resistors[2].pins[0], use_wire=True)
windings[1].pins[1].connect_to_component(resistors[1].pins[0], use_wire=True)
windings[0].pins[1].connect_to_component(resistors[0].pins[0], use_wire=True)

resistors[2].pins[1].connect_to_component(v_sources[2].pins[1], use_wire=True)
resistors[1].pins[1].connect_to_component(v_sources[1].pins[1], use_wire=True)
resistors[0].pins[1].connect_to_component(v_sources[0].pins[1], use_wire=True)

circuit.modeler.schematic.create_wire(
    points=[
        resistors[2].pins[1].location,
        [1200, 2500],
        [-600, 2500],
        [-600, 0],
        windings[0].pins[0].location,
    ]
)
circuit.modeler.schematic.create_wire(
    points=[
        resistors[1].pins[1].location,
        [1200, 1500],
        [-300, 1500],
        [-300, 2000],
        windings[2].pins[0].location,
    ]
)
circuit.modeler.schematic.create_wire(
    points=[
        resistors[0].pins[1].location,
        [1200, 500],
        [-300, 500],
        [-300, 1000],
        windings[1].pins[0].location,
    ]
)

# ## Export and import the netlist
#
# Export the netlist file, and import it to Maxwell

netlist_file = os.path.join(temp_folder.name, "_netlist.sph")
circuit.export_netlist_from_schematic(netlist_file)

m2d.edit_external_circuit(
    netlist_file_path=netlist_file, schematic_design_name=circuit_name
)

# ## Analyze the setup
#
# Analyze the setup

setup.analyze(cores=NUM_CORES)

# ## Create rectangular plot
#
# Plot winding currents

m2d.post.create_report(
    expressions=["Current(winding1)", "Current(winding2)", "Current(winding3)"],
    domain="Sweep",
    primary_sweep_variable="Time",
    plot_name="Winding Currents",
)

# ## Release AEDT

m2d.save_project()
m2d.release_desktop()
# Wait 3 seconds to allow Electronics Desktop to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Cleanup
#
# All project files are saved in the folder ``temp_dir.name``.
# If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
