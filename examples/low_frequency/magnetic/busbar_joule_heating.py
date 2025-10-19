<<<<<<< Updated upstream
# # Busbar Joule Heating Analysis with Maxwell 3D
=======
# # Busbar Joule Heating Analysis
>>>>>>> Stashed changes
#
# This example demonstrates how to set up and solve a busbar Joule heating analysis using PyAEDT. 
# The analysis captures frequency-dependent phenomena including skin effect, current redistribution, 
# and AC losses in power electronics systems.
#
# 1. Import packages and instantiate the application.
# 2. Create busbar geometry with input/output terminals and assign materials.
# 3. Set up current excitations following Kirchhoff's laws and configure analysis.
# 4. Run eddy current analysis and extract engineering results.
#
<<<<<<< Updated upstream
# This example demonstrates how to set up and solve a busbar Joule heating analysis using Maxwell 3D and PyAEDT. We will learn the complete workflow including:
#
# - Geometry creation and material assignment
# - Current excitation setup following Kirchhoff's laws
# - Mesh configuration for AC analysis
# - Eddy current analysis execution
# - Post-processing for field visualization
# - Engineering metrics extraction
#
# ## Core Concepts and Principles
#
# **Busbar Joule heating analysis** is critical in power electronics and electrical distribution systems.
# At AC frequencies, the **skin effect** causes non-uniform current distribution, which increases
# resistance and power losses.
#
# Maxwell 3D's eddy current solver captures these frequency-dependent phenomena, enabling accurate prediction of:
# - Power losses and current density distributions
# - Thermal loads for thermal management
# - AC resistance vs DC resistance
# - Skin depth effects on current distribution
#
# This example demonstrates the complete electromagnetic analysis workflow for conductor systems.
#
# Keywords: **Maxwell 3D**, **Eddy Current**, **Joule Heating**, **Skin Effect**
=======
# Keywords: **Busbar**, **Joule heating**, **Eddy current**, **Skin effect**
>>>>>>> Stashed changes

# ## Prerequisites
#
# ### Perform imports

# +
import math
import os
import tempfile
import time

<<<<<<< Updated upstream
from ansys.aedt.core import Maxwell3d
# -

# ### Define constants
# Define geometric dimensions and electrical parameters for the busbar system.

AEDT_VERSION = "2025.2"
NG_MODE = False
PROJECT_NAME = "Busbar_JouleHeating_Simple.aedt"
=======
import ansys.aedt.core  # Interface to Ansys Electronics Desktop
# -

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.1"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.
>>>>>>> Stashed changes

# Geometry parameters (mm)
BUSBAR_L = 100.0
BUSBAR_W = 10.0
BUSBAR_H = 5.0
TAB_L = 5.0
TAB_W = 3.0
TAB_H = 3.0

# Electrical parameters
I1 = 100.0  # Input current 1 (A)
I2 = 100.0  # Input current 2 (A)
FREQ = 50  # Frequency (Hz)

# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

<<<<<<< Updated upstream
# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
project_path = os.path.join(temp_folder.name, PROJECT_NAME)

# ### Launch application
#
# Start Maxwell 3D with eddy current solution type and set model units.
=======
temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ### Launch application
#
# Launch Maxwell 3D for eddy current analysis of the busbar system.
>>>>>>> Stashed changes

project_name = os.path.join(temp_folder.name, "busbar_joule_heating.aedt")
m3d = ansys.aedt.core.Maxwell3d(
    project=project_name,
    design="BusbarJouleHeating",
    solution_type="Eddy Current",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)
m3d.modeler.model_units = "mm"

# ## Model Preparation
#
<<<<<<< Updated upstream
# Create the main busbar conductor and terminal tabs, then unite them into a single object.

# ### Create 3D model
#
print("\nCreating Geometry")
=======
# Create the busbar geometry, assign materials and boundary conditions,
# and configure the electromagnetic analysis setup.
>>>>>>> Stashed changes

# ### Create 3D model
#
# Build the busbar geometry including main conductor and terminal tabs.
# Main busbar
busbar = m3d.modeler.create_box(
    origin=[0, 0, 0], sizes=[BUSBAR_L, BUSBAR_W, BUSBAR_H], name="MainBusbar"
)
m3d.assign_material(busbar, "copper")

# Input tabs
input_tab1 = m3d.modeler.create_box(
    origin=[-TAB_L, 1.0, 0.0], sizes=[TAB_L, TAB_W, BUSBAR_H], name="InputTab1"
)
m3d.assign_material(input_tab1, "copper")

input_tab2 = m3d.modeler.create_box(
    origin=[-TAB_L, 6.0, 0.0], sizes=[TAB_L, TAB_W, BUSBAR_H], name="InputTab2"
)
m3d.assign_material(input_tab2, "copper")

# Output tab
output_tab = m3d.modeler.create_box(
    origin=[BUSBAR_L, 3.0, 0.0], sizes=[TAB_L, 4.0, BUSBAR_H], name="OutputTab"
)
m3d.assign_material(output_tab, "copper")

# Unite all parts
united = m3d.modeler.unite([busbar, input_tab1, input_tab2, output_tab])
conductor = m3d.modeler[united] if isinstance(united, str) else united
conductor.name = "CompleteBusbar"

# ### Assign boundary conditions
#
<<<<<<< Updated upstream
# Select terminal faces and assign current excitations following Kirchhoff's current law.

# +
print("\nSelecting Terminal Faces")
=======
# Set up current excitations on terminal faces following Kirchhoff's current law.
>>>>>>> Stashed changes

# Sort faces by x-coordinate to identify input and output terminals
faces_sorted = sorted(conductor.faces, key=lambda f: f.center[0])
left_x = faces_sorted[0].center[0]
right_x = faces_sorted[-1].center[0]

# Get faces at left and right ends
left_faces = [f for f in faces_sorted if abs(f.center[0] - left_x) < 1e-3]
right_faces = [f for f in faces_sorted if abs(f.center[0] - right_x) < 1e-3]

# Select terminal faces
input_face1 = left_faces[0].id
input_face2 = left_faces[1].id if len(left_faces) > 1 else left_faces[0].id
output_face = right_faces[0].id



# Assign current excitations (following Kirchhoff's current law)
current1 = m3d.assign_current(
    assignment=input_face1, amplitude=I1, phase=0, name="InputCurrent1"
)

current2 = m3d.assign_current(
    assignment=input_face2, amplitude=I2, phase=0, name="InputCurrent2"
)

current3 = m3d.assign_current(
    assignment=output_face, amplitude=-(I1 + I2), phase=0, name="OutputCurrent"
)

print(f"Input Current 1: {I1}A")
print(f"Input Current 2: {I2}A")
print(f"Output Current: {-(I1 + I2)}A")
print(f"Current balance: {I1 + I2 + (-(I1 + I2))} = 0A")

<<<<<<< Updated upstream
print("\nCreating Air Region")

air = m3d.modeler.create_air_region(
    x_pos=0, y_pos=50, z_pos=100, x_neg=0, y_neg=50, z_neg=100
)
print("Air region created with 50% padding")
# -

# ### Define solution setup
#
# Set up the eddy current analysis with frequency, convergence criteria, and mesh settings.

# +
print("\n Setting Up Analysis ")
=======
# Create air region for boundary conditions
air = m3d.modeler.create_air_region(
    x_pos=0, y_pos=50, z_pos=100, x_neg=0, y_neg=50, z_neg=100
)

# ### Define solution setup
#
# Configure eddy current analysis with frequency and convergence settings.
>>>>>>> Stashed changes

setup = m3d.create_setup("EddyCurrentSetup")
setup.props["Frequency"] = f"{FREQ}Hz"
setup.props["PercentError"] = 2
setup.props["MaximumPasses"] = 8
setup.props["MinimumPasses"] = 2
setup.props["PercentRefinement"] = 30

# Assign mesh for skin effect resolution
mesh = m3d.mesh.assign_length_mesh(
    assignment=conductor.name,
    maximum_length=3.0,  # 3mm elements for skin effect resolution
    name="ConductorMesh",
)
<<<<<<< Updated upstream
print("Mesh operation assigned")
# -

# ### Run analysis
#
# Execute the finite element solver with automatic adaptive mesh refinement.

print("\n Running Analysis ")
print("Starting solver... (this may take a few minutes)")
=======

# ### Run analysis
#
# Execute the eddy current solver.
>>>>>>> Stashed changes

validation = m3d.validate_simple()
m3d.analyze_setup(setup.name)

# ## Postprocess
#
<<<<<<< Updated upstream
# Get Ohmic loss (Joule heating) results from the electromagnetic field solution.

# ### Evaluate loss
#
# +
print("\n--- Extracting Results ---")
=======
# Extract and visualize the electromagnetic field results and calculate 
# engineering metrics for the busbar Joule heating analysis.

# ### Evaluate loss
#
# Extract Ohmic loss (Joule heating) from the field solution.
>>>>>>> Stashed changes

setup_sweep = f"{setup.name} : LastAdaptive"
solution_data = m3d.post.get_solution_data(
    expressions=["SolidLoss"],
    report_category="EddyCurrent",
    setup_sweep_name=setup_sweep,
)
total_loss = solution_data.data_magnitude()[0]
<<<<<<< Updated upstream
print(f"\nOhmic Loss (Joule heating): {total_loss:.6f} W")
# -

# ### Visualize fields
#
# Generate 3D field plots showing current density, electric field, and power loss distributions.

# +
print("\n Creating Field Plots ")
=======
print(f"Ohmic Loss (Joule heating): {total_loss:.6f} W")

# ### Visualize fields
#
# Create field plots to visualize current density, electric field, and power loss distributions.
>>>>>>> Stashed changes

j_plot = m3d.post.create_fieldplot_surface(
    assignment=conductor.name, quantity="Mag_J", plot_name="Current_Density_Magnitude"
)

e_plot = m3d.post.create_fieldplot_surface(
    assignment=conductor.name, quantity="Mag_E", plot_name="Electric_Field_Magnitude"
)

joule_plot = m3d.post.create_fieldplot_volume(
    assignment=conductor.name,
    quantity="Ohmic_Loss",
    plot_name="Joule_Heating_Distribution",
)

<<<<<<< Updated upstream
# Calculate engineering metrics
# Compute key parameters including resistance, loss density, skin depth, and current density.

=======
# ### Calculate engineering metrics
#
# Compute key electrical parameters including resistance, loss density, and skin depth.
>>>>>>> Stashed changes
print("\nANALYSIS RESULTS")

# Basic electrical parameters
total_current = I1 + I2
busbar_volume = BUSBAR_L * BUSBAR_W * BUSBAR_H

# Ohmic Loss
print(f"Ohmic Loss (Joule heating): {total_loss:.6f} W")

# Loss density
loss_density = total_loss / busbar_volume
print(f"Loss density: {loss_density:.8f} W/mm³")

# Equivalent DC resistance
resistance = total_loss / (total_current**2)
resistance_micro = resistance * 1e6
print(f"Equivalent DC resistance: {resistance_micro:.2f} µΩ")

# Skin depth calculation
mu0 = 4 * math.pi * 1e-7
sigma_cu = 5.8e7
omega = 2 * math.pi * FREQ
skin_depth_m = math.sqrt(2 / (omega * mu0 * sigma_cu))
skin_depth_mm = skin_depth_m * 1000
print(f"Skin depth at {FREQ} Hz: {skin_depth_mm:.3f} mm")

current_density = total_current / (BUSBAR_W * BUSBAR_H)
print(f"Average current density: {current_density:.2f} A/mm²")

power_per_amp_squared = total_loss / (total_current**2)
print(f"Power per A²: {power_per_amp_squared*1e6:.2f} µW/A²")

# Comparison with conductor thickness
if BUSBAR_H < 2 * skin_depth_mm:
    print(
        f"Note: Busbar thickness ({BUSBAR_H}mm) < 2×skin depth ({2*skin_depth_mm:.1f}mm)"
    )
    print(f"      Skin effect is significant - current distribution is non-uniform")
else:
    print(
        f"Note: Busbar thickness ({BUSBAR_H}mm) > 2×skin depth ({2*skin_depth_mm:.1f}mm)"
    )
    print(f"      Current flows mainly near surfaces due to skin effect")

print("\n--- Field Plot Information ---")
print("Current density magnitude (|J|): Shows current distribution")
print("Electric field magnitude (|E|): Shows electric field intensity")
print("Joule heating distribution: Shows power loss density")
# -

# ## Finish
#
# ### Save the project

<<<<<<< Updated upstream
print(f"\n--- Saving Project ---")
m3d.save_project(project_path)
print(f"Project saved to: {project_path}")

m3d.release_desktop(close_projects=True, close_desktop=True)
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()

# ## Conclusion
# This example demonstrated the complete workflow for busbar Joule heating analysis using Maxwell 3D
# and PyAEDT. The analysis captured frequency-dependent phenomena including skin effect, current
# redistribution, and AC losses. Key outputs included power loss calculations, field visualizations,
# and technical metrics essential for thermal management and design optimization.
# The example demonstrates:
# Eddy current distribution in a busbar at AC frequency
# Joule heating due to AC resistance and skin effect
# Non-uniform current density due to skin effect
# Relationship between frequency, skin depth, and power loss
=======
m3d.save_project()
m3d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
>>>>>>> Stashed changes
