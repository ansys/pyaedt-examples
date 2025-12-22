# # Circuit-HFSS-Icepak coupling workflow
#
# This example shows how to create a two-way coupling
# between HFSS and Icepak.
#
# Consider a design where some components are simulated in
# HFSS with a full 3D model, while others are simulated in Circuit as lumped elements.
# The electrical simulation is done by placing the HFSS design into a Circuit design as
# a subcomponent and connecting the lumped components to its ports.
#
# The purpose of the workflow is to perform a thermal simulation
# of the Circuit-HFSS design, creating a two-way coupling with Icepak
# that allows running multiple iterations. The losses from both designs
# are accounted for.
# - EM losses are evaluated by the HFSS solver and fed into Icepak via a direct link.
# - Losses from the lumped components in the Circuit design are evaluated
# analytically and must be manually set into the Icepak boundary.
#
# On the back of the coupling, temperature information
# is handled differently for HFSS and Circuit.
#
# - For HFSS, a temperature map is exported from the Icepak design and used to create a
# 3D dataset. Then, the material properties in the HFSS design are updated based on this
# dataset.
# - For Circuit, the average temperature of the lumped components is extracted from the
# Icepak design and used to update the temperature-dependent characteristics of the
# lumped components in Circuit.
#
# The Circuit design in this example contains only a
# resistor component, with temperature-dependent resistance
# described by this formula: ``0.162*(1+0.004*(TempE-TempE0))``,
# where TempE is the current temperature and TempE0 is the
# ambient temperature. The HFSS design includes only a cylinder
# with temperature-dependent material conductivity, defined by
# a 2D dataset. The resistor and the cylinder have
# matching resistances.
#
# Keywords: **Multiphysics**, **HFSS**, **Icepak**, **Circuit**.

# ## Perform imports and define constants
#
# Perform required imports.

# +
import os
import tempfile
import time

import ansys.aedt.core as aedt
from ansys.aedt.core.examples.downloads import download_file
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

project_name = download_file(
    "circuit_hfss_icepak", "Circuit-HFSS-Icepak-workflow.aedtz", temp_folder.name
)

# ## Launch AEDT and initialize HFSS
#
# Launch AEDT and initialize HFSS. If there is an active HFSS design, the ``hfss``
# object is linked to it. Otherwise, a new design is created.

circuit = aedt.Circuit(
    project=project_name,
    new_desktop=True,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
)

# ## Set variable names
#
# Set the name of the resistor in Circuit.

resistor_body_name = "Circuit_Component"

# Set the name of the cylinder body in HFSS.

device3D_body_name = "Device_3D"

# ## Get HFSS design
#
# Get the HFSS design and prepare the material for the thermal link.

hfss = aedt.Hfss(project=circuit.project_name)

# ## Create a material
#
# Create a material to be used to set the temperature map on it.
# The material is created by duplicating the material assigned to the cylinder.

material_name = hfss.modeler.objects_by_name[device3D_body_name].material_name
new_material_name = material_name + "_dataset"
new_material = hfss.materials.duplicate_material(
    material=material_name, name=new_material_name
)

# ## Modify material properties
#
# Save the conductivity value. It is used later in the iterations.

old_conductivity = new_material.conductivity.value

# Assign the new material to the cylinder object in HFSS.

hfss.modeler.objects_by_name[device3D_body_name].material_name = new_material_name

# Because this material has a high conductivity, HFSS automatically deactivates ``solve_inside``.
# It must be turned back on to evaluate the losses inside the cylinder.

hfss.modeler.objects_by_name[device3D_body_name].solve_inside = True

# ## Get Icepak design

icepak = aedt.Icepak(project=circuit.project_name)

# ## Set parameters for iterations
#
# Set the initial temperature to a value closer to the final one, to speed up the convergence.

circuit["TempE"] = "300cel"

# Set the maximum number of iterations.

max_iter = 2

# Set the residual convergence criteria to stop the iterations.

temp_residual_limit = 0.02
loss_residual_limit = 0.02

# This variable is to contain iteration statistics.

stats = {}

# ## Start iterations
#
# Each ``for`` loop is a complete two-way iteration.
# The code is thoroughly commented.
# For a full understanding, read the inline comments carefully.

for cp_iter in range(1, max_iter + 1):
    stats[cp_iter] = {}

    # Step 1: Solve the HFSS design.
    #
    # Solve the HFSS design.
    hfss.analyze(cores=NUM_CORES)

    # Step 2: Refresh the dynamic link and solve the Circuit design.
    #
    # Find the HFSS subcomponent in Circuit.
    # This information is required by the ``refresh_dynamic_link()`` and ``push_excitations()`` methods.
    hfss_component_name = ""
    hfss_instance_name = ""
    for component in circuit.modeler.schematic.components.values():
        if (
            component.model_name is not None
            and hfss.design_name in component.model_name
        ):
            hfss_component_name = component.model_name
            hfss_instance_name = component.refdes
            break
    if not hfss_component_name or not hfss_instance_name:
        raise "Hfss component not found in Circuit design"

    # Refresh the dynamic link.
    circuit.modeler.schematic.refresh_dynamic_link(name=hfss_component_name)

    # Solve the Circuit design.
    circuit.analyze()

    # Step 3: Push the excitations. (HFSS design results are scaled automatically.)
    #
    # Push the excitations.
    circuit.push_excitations(instance=hfss_instance_name)

    # Step 4: Extract the resistor's power loss value from the Circuit design.
    #
    # Evaluate the power loss on the resistor.
    r_losses = circuit.post.get_solution_data(
        expressions="0.5*mag(I(I1)*V(V1))"
    ).get_expression_data()[1][0]

    # Save the losses in the stats.
    stats[cp_iter]["losses"] = r_losses

    # Step 5: Set the resistor's power loss value in the Icepak design (block thermal condition)
    #
    # Find the solid block boundary in Icepak.
    boundaries = icepak.boundaries
    boundary = None
    for bb in boundaries:
        if bb.name == "Block1":
            boundary = bb
            break
    if not boundary:
        raise "Block boundary not defined in Icepak design."

    # Set the resistor's power loss in the Block Boundary.
    boundary.props["Total Power"] = str(r_losses) + "W"

    # Step 6: Solve the Icepak design.
    #
    # Clear linked data. Otherwise, Icepak continues to run the simulation with the initial losses.
    icepak.clear_linked_data()

    # Solve the Icepak design.
    icepak.analyze(cores=NUM_CORES)

    # Step 7: Export the temperature map from the Icepak design and create a new 3D dataset with it.
    #
    # Export the temperature map to a file.
    fld_filename = os.path.join(
        icepak.working_directory, f"temperature_map_{cp_iter}.fld"
    )
    icepak.post.export_field_file(
        quantity="Temp",
        output_file=fld_filename,
        assignment="AllObjects",
        objects_type="Vol",
    )

    # Convert the FLD file into a dataset tab file compatible with the dataset import.
    # The existing header lines must be removed and replaced with a single header line
    # containing the value unit.
    with open(fld_filename, "r") as f:
        lines = f.readlines()

    _ = lines.pop(0)
    _ = lines.pop(0)
    lines.insert(0, '"X"    "Y" "Z" "cel"\n')

    basename, _ = os.path.splitext(fld_filename)
    tab_filename = basename + "_dataset.tab"

    with open(tab_filename, "w") as f:
        f.writelines(lines)

    # Import the 3D dataset.
    dataset_name = f"temp_map_step_{cp_iter}"
    hfss.import_dataset3d(
        input_file=tab_filename, name=dataset_name, is_project_dataset=True
    )

    # Step 8: Update material properties in the HFSS design based on the new dataset.
    #
    # Set the new conductivity value.
    new_material.conductivity.value = (
        f"{old_conductivity}*Pwl($TempDepCond,clp(${dataset_name},X,Y,Z))"
    )

    # Switch off the thermal modifier of the material, if any.
    new_material.conductivity.thermalmodifier = None

    # Step 9: Extract the average temperature of the resistor from the Icepak design.
    #
    # Get the mean temperature value on the high-resistivity object.
    mean_temp = icepak.post.get_scalar_field_value(
        quantity="Temp", scalar_function="Mean", object_name=resistor_body_name
    )

    # Save the temperature in the iteration statistics.
    stats[cp_iter]["temp"] = mean_temp

    # Step 10: Update the resistance value in the Circuit design.
    #
    # Set this temperature in Circuit in the ``TempE`` variable.
    circuit["TempE"] = f"{mean_temp}cel"

    # Save the project
    circuit.save_project()

    # Check the convergence of the iteration
    #
    # Evaluate the relative residuals on temperature and losses.
    # If the residuals are smaller than the threshold, set the convergence flag to ``True```.
    # Residuals are calculated starting from the second iteration.
    converged = False
    stats[cp_iter]["converged"] = converged
    if cp_iter > 1:
        delta_temp = abs(stats[cp_iter]["temp"] - stats[cp_iter - 1]["temp"]) / abs(
            stats[cp_iter - 1]["temp"]
        )
        delta_losses = abs(
            stats[cp_iter]["losses"] - stats[cp_iter - 1]["losses"]
        ) / abs(stats[cp_iter - 1]["losses"])
        if delta_temp <= temp_residual_limit and delta_losses <= loss_residual_limit:
            converged = True
            stats[cp_iter]["converged"] = converged
    else:
        delta_temp = None
        delta_losses = None

    # Save the relative residuals in the iteration stats.
    stats[cp_iter]["delta_temp"] = delta_temp
    stats[cp_iter]["delta_losses"] = delta_losses

    # Exit from the loop if the convergence is reached.
    if converged:
        break

# ## Print overall statistics
#
# Print the overall statistics for the multiphysics loop.

for i in stats:
    txt = "yes" if stats[i]["converged"] else "no"
    delta_temp = (
        f"{stats[i]['delta_temp']:.4f}"
        if stats[i]["delta_temp"] is not None
        else "None"
    )
    delta_losses = (
        f"{stats[i]['delta_losses']:.4f}"
        if stats[i]["delta_losses"] is not None
        else "None"
    )
    print(
        f"Step {i}: temp={stats[i]['temp']:.3f}, losses={stats[i]['losses']:.3f}, "
        f"delta_temp={delta_temp}, delta_losses={delta_losses}, "
        f"converged={txt}"
    )

# ## Release AEDT
#
# Release AEDT and close the example.

icepak.save_project()
icepak.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``. If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
