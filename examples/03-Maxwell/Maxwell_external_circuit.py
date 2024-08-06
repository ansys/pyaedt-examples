# # Maxwell 3D Transformer model with zigzag connection
#
# This example ...

# ## Perform required imports

# +
import tempfile, os

from pyaedt import Maxwell3d, MaxwellCircuit
import pyaedt

# -

# Set constant values

AEDT_VERSION = "2024.1"

# ## Create temporary directory
#
# Create temporary directory.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Initialize and launch Maxwell 2D
#
# Initialize and launch Maxwell 2D, providing the version, path to the project, the design
# name and type.

# +
non_graphical = False

project_name = "Transformer_zigzag"
design_name = "1 Eddy current"
solver = "EddyCurrent"
desktop_version = AEDT_VERSION

m3d = Maxwell3d(
    version=desktop_version,
    new_desktop=False,
    design=design_name,
    project=project_name,
    solution_type=solver,
    non_graphical=non_graphical,
)

mod = m3d.modeler

core_id = mod.create_udp(
    dll="RMxprt/TransCore.dll",
    parameters=[],
    library="syslib",
    name="transformer_core"
)
m3d.assign_material(assignment=core_id, material="steel_1008")

winding_size = [-5, 96]
lv_coil_pos = [0, -21, -48]
hv_coil_pos = [0, -31, -48]
a_offset = [-100, 0, 0]
c_offset = [100, 0, 0]

# Create LVB and HVB windings and terminals
lvb_terminal_id = mod.create_rectangle(orientation="YZ", origin=lv_coil_pos,
                                       sizes=winding_size, name="LVB_terminal")
lvb_winding_id = mod.create_rectangle(orientation="YZ", origin=lv_coil_pos, sizes=winding_size, name="LVB_winding")
mod.sweep_around_axis(assignment=lvb_winding_id, axis="Z")

hvb_terminal_id = mod.create_rectangle(orientation="YZ", origin=hv_coil_pos,
                                       sizes=winding_size, name="HVB_terminal")
hvb_winding_id = mod.create_rectangle(orientation="YZ", origin=hv_coil_pos, sizes=winding_size, name="HVB_winding")
mod.sweep_around_axis(assignment=hvb_winding_id, axis="Z")

lvb_winding_id.material_name = "copper"
hvb_winding_id.material_name = "copper"

# duplicate = lvb_winding_id.duplicate_along_line(a_offset)
# lva_winding_id = mod.objects[duplicate[0]]
# lva_winding_id.name = "LVA_winding"


# Duplicate LVB and HVB windings and terminals to create A and C
duplications = [
    (lvb_winding_id, a_offset, "lva_winding_id", "LVA_winding"),
    (lvb_winding_id, c_offset, "lvc_winding_id", "LVC_winding"),
    (lvb_terminal_id, a_offset, "lva_terminal_id", "LVA_terminal"),
    (lvb_terminal_id, c_offset, "lvc_terminal_id", "LVC_terminal"),
    (hvb_winding_id, a_offset, "hva_winding_id", "HVA_winding"),
    (hvb_winding_id, c_offset, "hvc_winding_id", "HVC_winding"),
    (hvb_terminal_id, a_offset, "hva_terminal_id", "HVA_terminal"),
    (hvb_terminal_id, c_offset, "hvc_terminal_id", "HVC_terminal"),
]

# Dictionary to hold the new objects
new_objects = {}

for obj, offset, var_name, new_name in duplications:
    duplicate = obj.duplicate_along_line(offset)
    new_obj = mod.objects[duplicate[0]]
    new_obj.name = new_name
    new_objects[var_name] = new_obj

# Access the new objects using the keys
lva_winding_id = new_objects["lva_winding_id"]
lvc_winding_id = new_objects["lvc_winding_id"]
lva_terminal_id = new_objects["lva_terminal_id"]
lvc_terminal_id = new_objects["lvc_terminal_id"]
hva_winding_id = new_objects["hva_winding_id"]
hvc_winding_id = new_objects["hvc_winding_id"]
hva_terminal_id = new_objects["hva_terminal_id"]
hvc_terminal_id = new_objects["hvc_terminal_id"]

lv_terminals = [lva_terminal_id, lvb_terminal_id, lvc_terminal_id]
hv_terminals = [hva_terminal_id, hvb_terminal_id, hvc_terminal_id]

windings = [lva_winding_id, lvb_winding_id, lvc_winding_id, hva_winding_id, hvb_winding_id, hvc_winding_id]

# Create region
mod.create_region(pad_value=50)

# Assign mesh operations
m3d.mesh.assign_length_mesh(assignment=core_id, maximum_length=50, name="core_inside")
m3d.mesh.assign_length_mesh(assignment=windings, maximum_length=50, name="windings_inside")

# Assign coils
lv_turns = 100
hv_turns = 500

for coil in lv_terminals:
    m3d.assign_coil(assignment=coil, conductors_number=lv_turns, name=coil.name)

for coil in hv_terminals:
    m3d.assign_coil(assignment=coil, conductors_number=hv_turns, name=coil.name)


m3d.assign_winding(
    assignment=None,
    winding_type="External",
    is_solid=False,
    name="LVA",
)

m3d.add_winding_coils(assignment="LVA", coils=["LVA_terminal"])

m3d.assign_winding(
    assignment=None,
    winding_type="External",
    is_solid=False,
    name="LVB",
)

solution_setup = m3d.create_setup(name="Setup1")

# Create external circuit
circuit = MaxwellCircuit(project=project_name, design="Circuit1")

circuit.schematic_units = "mil"
ind = circuit.modeler.schematic.create_inductor("Inductor1", 1.5, [-1000, 1000])
res = circuit.modeler.schematic.create_resistor("Resistor1", 10, [1000, 1000])
gnd = circuit.modeler.schematic.create_gnd([0.0, 0.0])
winding1 = circuit.modeler.schematic.create_winding("Winding1")

netlist_file = "C:\\export_netlist.sph"
circuit.export_netlist_from_schematic(netlist_file)

m3d.edit_external_circuit(netlist_file_path=netlist_file, schematic_design_name="Circuit1")