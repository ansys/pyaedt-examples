# # Maxwell 2D external circuit example
#
# This example shows how to create a delta circuit as an external circuit and connect it with a Maxwell 2D design.

# ## Perform required imports

import tempfile
import time

import pyaedt

# Set constant values

AEDT_VERSION = "2024.1"
NG_MODE = False

# ## Create temporary directory
#
# Create temporary directory.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Initialize dictionaries
#
# Initialize dictionaries that contain all the definitions for the design variables.

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

# ## Initialize and launch Maxwell 2D
#
# Initialize and launch Maxwell 2D, providing the version, path to the project, the design
# name and type.

project_name = "Maxwell_circuit_example"
design_name = "1 Maxwell"
circuit_name = "2 Delta circuit"
solver = "TransientXY"

maxwell = pyaedt.Maxwell2d(
    version=AEDT_VERSION,
    new_desktop=False,
    design=design_name,
    project=project_name,
    solution_type=solver,
    non_graphical=NG_MODE,
)

# ## Define variables from dictionaries
#
# Define design variables from the created dictionaries.

for k, v in transient_parameters.items():
    maxwell[k] = v

# ## Create geometry
#
# Create copper coils and vacuum region, assign mesh operations, and assign balloon boundary to the region edges.

coil1_id = maxwell.modeler.create_circle(orientation='Z', origin=[0, 0, 0], radius=10, name="coil1", material="copper")
coil2_id = maxwell.modeler.create_circle(orientation='Z', origin=[25, 0, 0], radius=10, name="coil2", material="copper")
coil3_id = maxwell.modeler.create_circle(orientation='Z', origin=[50, 0, 0], radius=10, name="coil3", material="copper")

region = maxwell.modeler.create_region(pad_value=[100, 300, 100, 300])

maxwell.mesh.assign_length_mesh(assignment=[coil1_id, coil2_id, coil3_id, region], maximum_length=5)

maxwell.assign_balloon(assignment=region.edges)

# ## Assign excitations
#
# Assign external windings

maxwell.assign_winding(assignment=["coil1"], is_solid=False, winding_type="External", name="winding1", current=0)
maxwell.assign_winding(assignment=["coil2"], is_solid=False, winding_type="External", name="winding2", current=0)
maxwell.assign_winding(assignment=["coil3"], is_solid=False, winding_type="External", name="winding3", current=0)

# ## Create simulation setup
#
# Create simulation setup

setup = maxwell.create_setup()
setup["StopTime"] = "stop_time"
setup["TimeStep"] = "time_step"

# ## Create external circuit
#
# Create circuit design with the windings

circuit = maxwell.create_external_circuit(circuit_design=circuit_name)

# ## Define variables from dictionaries
#
# Define design variables from the created dictionaries.

for k, v in circuit_parameters.items():
    circuit[k] = v

windings = [circuit.modeler.schematic.components[k] for k in list(circuit.modeler.schematic.components.keys())
        if circuit.modeler.schematic.components[k].parameters["Info"] == "Winding"]

# ## Finalize external circuit
#
# Draw rest of the components: Resistances, voltage sources, and grounds

circuit.modeler.schematic_units = "mil"

resistors = [None]*3
v_sources = [None]*3
ground = [None]*3

for i in range(3):
    resistors[i] = circuit.modeler.schematic.create_resistor(name="R"+str(i+1), value="resistance_value",
                                                             location=[1000, i*1000])

    v_sources[i] = circuit.modeler.schematic.create_component(component_library="Sources", component_name="VSin",
                                                              location=[2000, i*1000], angle=90)
    v_sources[i].set_property(name="Va", value="voltage")
    v_sources[i].set_property(name="VFreq", value="frequency")
    v_sources[i].set_property(name="Phase", value=str(i*120)+"deg")
    ground[i] = circuit.modeler.schematic.create_gnd([2300, i*1000], angle=90)

# ## Connect the components
#
# Draw wires

windings[2].pins[1].connect_to_component(resistors[2].pins[0], use_wire=True)
windings[1].pins[1].connect_to_component(resistors[1].pins[0], use_wire=True)
windings[0].pins[1].connect_to_component(resistors[0].pins[0], use_wire=True)

resistors[2].pins[1].connect_to_component(v_sources[2].pins[1], use_wire=True)
resistors[1].pins[1].connect_to_component(v_sources[1].pins[1], use_wire=True)
resistors[0].pins[1].connect_to_component(v_sources[0].pins[1], use_wire=True)

circuit.modeler.schematic.create_wire(points=[resistors[2].pins[1].location, [1200, 2500], [-600, 2500],
                                              [-600, 0], windings[0].pins[0].location])
circuit.modeler.schematic.create_wire(points=[resistors[1].pins[1].location, [1200, 1500], [-300, 1500],
                                              [-300, 2000], windings[2].pins[0].location])
circuit.modeler.schematic.create_wire(points=[resistors[0].pins[1].location, [1200, 500], [-300, 500],
                                              [-300, 1000], windings[1].pins[0].location])

# ## Export and import the netlist
#
# Export the netlist file, and import it to Maxwell

netlist_file = temp_dir.name + project_name + "_netlist.sph"
circuit.export_netlist_from_schematic(netlist_file)

maxwell.edit_external_circuit(netlist_file_path=netlist_file, schematic_design_name=circuit_name)

# ## Analyze the setup
#
# Analyze the setup

setup.analyze()

# ## Create rectangular plot
#
# Plot winding currents

maxwell.post.create_report(
    expressions=["Current(winding1)","Current(winding2)","Current(winding3)"],
    domain="Sweep",
    primary_sweep_variable="Time",
    plot_name="Winding Currents",
)

# ## Release AEDT and clean up temporary directory
#
# Release AEDT and remove both the project and temporary directory.

maxwell.release_desktop(close_projects=True, close_desktop=True)
time.sleep(3)
temp_dir.cleanup()