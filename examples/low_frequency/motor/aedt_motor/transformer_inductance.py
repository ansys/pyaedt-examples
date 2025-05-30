# # Transformer leakage inductance calculation
#
# This example shows how to use PyAEDT to create a Maxwell 2D
# magnetostatic analysis to calculate transformer leakage
# inductance and reactance.
# The analysis based on this document is from page 8 in Professor S. V.
# Kulkami's paper, [Basis of Finite Element Method](https://www.ee.iitb.ac.in/~fclab/FEM/FEM1.pdf).
#
# Keywords: **Maxwell 2D**, **transformer**, **motor**.

# ## Perform imports and define constants

# +
import os
import tempfile
import time

from ansys.aedt.core import Maxwell2d
# -

# Define constants,

AEDT_VERSION = "2025.1"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Initialize and launch Maxwell 2D
#
# Initialize and launch Maxwell 2D, providing the version, the path to the project, the design
# name, and the type.

# +

project_name = os.path.join(temp_folder.name, "Magnetostatic.aedt")
m2d = Maxwell2d(
    version=AEDT_VERSION,
    new_desktop=False,
    design="Transformer_leakage_inductance",
    project=project_name,
    solution_type="MagnetostaticXY",
    non_graphical=NG_MODE,
)
# -

# ## Initialize dictionaries
#
# Set modeler units and initialize dictionaries
# that contain all the definitions for the design variables.

# +
m2d.modeler.model_units = "mm"

dimensions = {
    "core_width": "1097mm",
    "core_height": "2880mm",
    "core_opening_x1": "270mm",
    "core_opening_x2": "557mm",
    "core_opening_y1": "540mm",
    "core_opening_y2": "2340mm",
    "core_opening_width": "core_opening_x2-core_opening_x1",
    "core_opening_height": "core_opening_y2-core_opening_y1",
    "LV_x1": "293mm",
    "LV_x2": "345mm",
    "LV_width": "LV_x2-LV_x1",
    "LV_mean_radius": "LV_x1+LV_width/2",
    "LV_mean_turn_length": "pi*2*LV_mean_radius",
    "LV_y1": "620mm",
    "LV_y2": "2140mm",
    "LV_height": "LV_y2-LV_y1",
    "HV_x1": "394mm",
    "HV_x2": "459mm",
    "HV_width": "HV_x2-HV_x1",
    "HV_mean_radius": "HV_x1+HV_width/2",
    "HV_mean_turn_length": "pi*2*HV_mean_radius",
    "HV_y1": "620mm",
    "HV_y2": "2140mm",
    "HV_height": "HV_y2-HV_y1",
    "HV_LV_gap_radius": "(LV_x2 + HV_x1)/2",
    "HV_LV_gap_length": "pi*2*HV_LV_gap_radius",
}

specifications = {
    "Amp_turns": "135024A",
    "Frequency": "50Hz",
    "HV_turns": "980",
    "HV_current": "Amp_turns/HV_turns",
}
# -

# ## Define variables from dictionaries
#
# Define design variables from the created dictionaries.

# +
m2d.variable_manager.set_variable(name="Dimensions")

for k, v in dimensions.items():
    m2d[k] = v

m2d.variable_manager.set_variable(name="Windings")

for k, v in specifications.items():
    m2d[k] = v
# -

# ## Create design geometries
#
# Create the transformer core, the HV and LV windings, and the region.

# +
core = m2d.modeler.create_rectangle(
    origin=[0, 0, 0],
    sizes=["core_width", "core_height", 0],
    name="core",
    material="steel_1008",
)

core_hole = m2d.modeler.create_rectangle(
    origin=["core_opening_x1", "core_opening_y1", 0],
    sizes=["core_opening_width", "core_opening_height", 0],
    name="core_hole",
)

m2d.modeler.subtract(blank_list=[core], tool_list=[core_hole], keep_originals=False)

lv = m2d.modeler.create_rectangle(
    origin=["LV_x1", "LV_y1", 0],
    sizes=["LV_width", "LV_height", 0],
    name="LV",
    material="copper",
)

hv = m2d.modeler.create_rectangle(
    origin=["HV_x1", "HV_y1", 0],
    sizes=["HV_width", "HV_height", 0],
    name="HV",
    material="copper",
)

region = m2d.modeler.create_region(pad_percent=[20, 10, 0, 10])

# ## Assign boundary condition
#
# Assign vector potential to zero on all region boundaries. This makes x=0 edge a symmetry boundary.

m2d.assign_vector_potential(assignment=region.edges, boundary="VectorPotential1")
# -

# ## Create initial mesh settings
#
# Assign a relatively dense mesh to all objects to ensure that the energy is calculated accurately.

m2d.mesh.assign_length_mesh(
    assignment=["core", "Region", "LV", "HV"],
    maximum_length=50,
    maximum_elements=None,
    name="all_objects",
)

# ## Define excitations
#
# Assign the same current in amp-turns but in opposite directions to the HV and LV windings.

m2d.assign_current(assignment=lv, amplitude="Amp_turns", name="LV")
m2d.assign_current(assignment=hv, amplitude="Amp_turns", name="HV", swap_direction=True)

# ## Create and analyze setup
#
# Create and analyze the setup. Set the number of minimum passes to 3 to ensure accuracy.

m2d.create_setup(name="Setup1", MinimumPasses=3)
m2d.analyze_setup(use_auto_settings=False, cores=NUM_CORES)

# ## Calculate transformer leakage inductance and reactance
#
# Calculate transformer leakage inductance from the magnetic energy with PyAEDT advanced fields calculator.

# +
leakage_inductance = {
    "name": "Leakage_inductance",
    "description": "Leakage inductance from the magnetic energy",
    "design_type": ["Maxwell 2D"],
    "fields_type": ["Fields"],
    "primary_sweep": "Distance",
    "assignment": "",
    "assignment_type": ["Line"],
    "operations": [
        "Fundamental_Quantity('Energy')",
        "EnterSurface('HV')",
        "Operation('SurfaceValue')",
        "Operation('Integrate')",
        "Scalar_Function(FuncValue='HV_mean_turn_length')",
        "Operation('*')",
        "Fundamental_Quantity('Energy')",
        "EnterSurface('LV')",
        "Operation('SurfaceValue')",
        "Operation('Integrate')",
        "Scalar_Function(FuncValue='LV_mean_turn_length')",
        "Operation('*')",
        "Fundamental_Quantity('Energy')",
        "EnterSurface('Region')",
        "Operation('SurfaceValue')",
        "Operation('Integrate')",
        "Scalar_Function(FuncValue='HV_LV_gap_length')",
        "Operation('*')",
        "Operation('+')",
        "Operation('+')",
        "Scalar_Constant(2)",
        "Operation('*')",
        "Scalar_Function(FuncValue='HV_current')",
        "Scalar_Function(FuncValue='HV_current')",
        "Operation('*')",
        "Operation('/')",
    ],
    "report": ["Data Table", "Rectangular Plot"],
}
m2d.post.fields_calculator.add_expression(leakage_inductance, None)

leakage_reactance = {
    "name": "Leakage_reactance",
    "description": "Leakage reactance from the magnetic energy",
    "design_type": ["Maxwell 2D"],
    "fields_type": ["Fields"],
    "primary_sweep": "Distance",
    "assignment": "",
    "assignment_type": ["Line"],
    "operations": [
        "NameOfExpression('Leakage_inductance')",
        "Scalar_Constant(2)",
        "Scalar_Constant(3.14159)",
        "Scalar_Function(FuncValue='Frequency')",
        "Operation('*')",
        "Operation('*')",
        "Operation('*')",
    ],
    "report": ["Data Table", "Rectangular Plot"],
}
m2d.post.fields_calculator.add_expression(leakage_reactance, None)

m2d.post.create_report(
    expressions=["Leakage_inductance", "Leakage_reactance"],
    report_category="Fields",
    primary_sweep_variable="core_width",
    plot_type="Data Table",
    plot_name="Transformer Leakage Inductance",
)
# -

# ## Print leakage inductance and reactance values in AEDT Message Manager

m2d.logger.clear_messages()
m2d.logger.info(
    "Leakage_inductance =  {:.4f}H".format(
        m2d.post.get_scalar_field_value(quantity="Leakage_inductance")
    )
)
m2d.logger.info(
    "Leakage_reactance =  {:.2f}Ohm".format(
        m2d.post.get_scalar_field_value(quantity="Leakage_reactance")
    )
)

# ## Plot energy in the simulation domain
#
# Most of the energy is confined in the air between the HV and LV windings.

energy_field_overlay = m2d.post.create_fieldplot_surface(
    assignment=m2d.modeler.object_names,
    quantity="energy",
    plot_name="Energy",
)

# ## Release AEDT

m2d.save_project()
m2d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
