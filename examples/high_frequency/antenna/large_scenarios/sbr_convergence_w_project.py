# # SBR+ convergence analysis
#
# This example demonstrates how to perform a convergence study on SBR+ (Shooting and Bouncing Rays)
# setup parameters to ensure accurate and reliable radar cross-section (RCS) results.
#
# The Shooting and Bouncing Rays (SBR+) method is a high-frequency asymptotic technique used in HFSS
# for electrically large problems such as antenna placement and radar cross-section (RCS) analysis.
# Two key parameters affect solution accuracy:
#
# - **Ray Density Per Wavelength**: Controls how many rays are launched per wavelength. Higher values
#   provide more accurate results but increase computation time.
# - **Maximum Number of Bounces**: Defines how many times rays can reflect off surfaces before terminating.
#   More bounces capture multi-reflection effects but increase solve time.
#
# This example systematically varies these parameters to identify converged settings where further
# increases do not significantly change the RCS results. The workflow demonstrates best practices
# for ensuring your SBR+ analysis is properly converged.
#
# Keywords: **HFSS**, **SBR+**, **Radar cross-section**, **Convergence study**, **Ray tracing**.

# ## Prerequisites
#
# ### Perform imports

import tempfile
import time

import matplotlib.pyplot as plt
import numpy as np
from ansys.aedt.core.examples.downloads import download_file
from ansys.aedt.core.hfss import Hfss

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.2"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Model preparation
#
# ### Download the model
#
# The model used in this example will be downloaded from the
# [example-data](https://github.com/ansys/example-data)
# GitHub repository. The model is a trihedral corner reflector,
# a common radar calibration target with well-known RCS characteristics.

project_path = download_file("sbr_convergence", "trihedral_rcs.aedt", temp_folder.name)

# ### Launch HFSS and open project
#
# Launch HFSS and open the project containing the trihedral reflector geometry.

hfss = Hfss(
    project=project_path,
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Convergence study parameters
#
# ### Setup parameters
#
# Define the analysis frequency and convergence criteria.
# The convergence threshold determines when two successive results
# are considered "close enough" that further refinement is unnecessary.

setup_frequency = ["10GHz"]  # Analysis frequency
convergence_threshold = 0.5  # Maximum allowed change in dB (convergence criterion)

# ### Advanced SBR+ options
#
# Configure advanced ray tracing options:
#
# - **PDF (Physical Theory of Diffraction)**: Improves accuracy for diffraction effects at edges.
# - **UTD (Uniform Theory of Diffraction)**: Adds rays to capture diffraction phenomena.
#
# These options can improve accuracy but increase computation time.

enable_ptd = False
enable_utd = False

# ### Convergence methodology
#
# Define how convergence is assessed:
#
# - **Convergence Method**:
#   - ``"average"``: Checks if the average RCS across all angles has converged.
#   - ``"point_to_point"``: Checks if the maximum change at any single angle is below threshold (more stringent).
#
# - **Convergence Order**:
#   - ``"ray_density_first"``: First converge ray density, then bounce number.
#   - ``"bounces_first"``: First converge bounce number, then ray density.

convergence_method = "point_to_point"  # "average" or "point_to_point"
convergence_order = "bounces_first"  # "ray_density_first" or "bounces_first"

# ### Starting values
#
# Define initial values for the convergence sweep.
# The algorithm will increment these values until convergence is achieved.

starting_ray_density = 1
starting_bounce_number = 2

# ### Configure PDF/UTD settings
#
# Map the boolean flags to the appropriate HFSS setup string.

if enable_ptd and enable_utd:
    ptd_utd_setting = "PDF Correction + UTD Rays"
elif enable_ptd and not enable_utd:
    ptd_utd_setting = "PDF Correction"
elif not enable_ptd and enable_utd:
    ptd_utd_setting = "UTD Rays"
else:
    ptd_utd_setting = "None"

print(f"PDF: {enable_ptd}, UTD: {enable_utd} → Setting: '{ptd_utd_setting}'")
print(f"Convergence Method: {convergence_method}")
print(f"Convergence Order:  {convergence_order}")

# ## Convergence analysis functions
#
# ### Define convergence check function
#
# This function compares RCS results from successive iterations
# to determine if the solution has converged.
#
# Two methods are available:
# - **Average**: Compares the average RCS across all angles.
# - **Point-to-point**: Compares RCS at each angle individually (more conservative).


def check_convergence(rcs_values, previous_rcs_values, iwavephi_values, threshold, method):
    if method == "average":
        current_avg = np.mean(rcs_values)
        previous_avg = np.mean(previous_rcs_values)
        change = np.abs(current_avg - previous_avg)
        print(f"  Previous Average RCS: {previous_avg:.4f} dBsm")
        print(f"  Current  Average RCS: {current_avg:.4f} dBsm")
        print(f"  Average change: {change:.4f} dB")
        return change < threshold, change, change, 0

    else:
        absolute_changes = np.abs(rcs_values - previous_rcs_values)
        max_change = np.max(absolute_changes)
        max_change_index = np.argmax(absolute_changes)
        mean_change = np.mean(absolute_changes)
        print(f"  Max point change:  {max_change:.4f} dB at IWavePhi = {iwavephi_values[max_change_index]:.1f}°")
        print(f"  Mean point change: {mean_change:.4f} dB")
        return max_change < threshold, max_change, mean_change, max_change_index


# ### Define convergence sweep function
#
# This function runs a convergence sweep for either ray density or bounce number.
#
# The workflow used to retrieve solution data from
# HFSS is comprised of the following steps:
#
# | Step | Description | Method |
# |---|---|---|
# | 1. | Create an SBR+ setup with<br>specified parameters | ``hfss.create_setup()`` |
# | 2. | Run the analysis | ``hfss.analyze_setup()`` |
# | 3. | Retrieve solution data | ``hfss.post.get_solution_data()`` |
# | 4. | Check convergence criteria | ``check_convergence()`` |
#
# **Parameters:**
#
# - ``sweep_param``: Parameter to sweep (``"ray_density"`` or ``"bounce_number"``)
# - ``fixed_param_value``: Value of the fixed parameter
# - ``Setup_Frequency``: Analysis frequency list
# - ``ptd_utd_setting``: PDF/UTD configuration string
# - ``convergence_threshold``: Maximum allowed change in dB
# - ``convergence_method``: Method for checking convergence
# - ``start_value``: Starting value for the sweep
# - ``max_value``: Maximum value before stopping
#
# **Returns:**
#
# - ``converged_value``: The value at which convergence was reached
# - ``param_values``: List of all tested values
# - ``average_rcs_list``: List of average RCS for each iteration
# - ``all_rcs_curves``: List of all RCS curves
# - ``all_iwavephi``: List of all IWavePhi arrays


def run_convergence_sweep(hfss, sweep_param, fixed_param_value, Setup_Frequency, ptd_utd_setting, convergence_threshold, convergence_method, start_value, max_value):

    param_values = []
    average_rcs_list = []
    all_rcs_curves = []
    all_iwavephi = []

    current_value = start_value
    previous_rcs_values = None
    converged = False
    converged_value = max_value

    while not converged:

        if sweep_param == "ray_density":
            ray_density = current_value
            bounce_number = fixed_param_value
            print(f"\nTesting Ray Density: {current_value} (Bounces fixed at {fixed_param_value})")
        else:
            ray_density = fixed_param_value
            bounce_number = current_value
            print(f"\nTesting Bounce Number: {current_value} (Ray Density fixed at {fixed_param_value})")

        if "SBR" in hfss.setup_names:
            hfss.delete_setup("SBR")

        setup1 = hfss.create_setup(name="SBR")
        setup1.props["RayDensityPerWavelength"] = ray_density
        setup1.props["MaxNumberOfBounces"] = bounce_number
        setup1["RangeType"] = "SinglePoints"
        setup1["RangeStart"] = Setup_Frequency[0]
        setup1.props["ComputeFarFields"] = True
        setup1.props["PTDUTDSimulationSettings"] = ptd_utd_setting
        setup1.update()

        hfss.analyze_setup("SBR", cores=NUM_CORES)

        sweep_names = hfss.existing_analysis_sweeps
        solution_data = hfss.post.get_solution_data(expressions="dB(MonostaticRCSTotal)", setup_sweep_name=sweep_names[0], primary_sweep_variable="IWavePhi")

        iwavephi_values = solution_data.primary_sweep_values
        rcs_values = solution_data.data_real()
        average_rcs = np.mean(rcs_values)

        param_values.append(current_value)
        average_rcs_list.append(average_rcs)
        all_rcs_curves.append(rcs_values.copy())
        all_iwavephi.append(iwavephi_values.copy())

        print(f"  Average RCS: {average_rcs:.4f} dBsm")

        if previous_rcs_values is not None:
            converged, max_change, mean_change, max_idx = check_convergence(rcs_values, previous_rcs_values, iwavephi_values, convergence_threshold, convergence_method)
            if converged:
                print(f"\n*** {sweep_param.upper().replace('_', ' ')} CONVERGED at {current_value} ***")
                converged_value = current_value

        previous_rcs_values = rcs_values.copy()
        current_value += 1

        if current_value > max_value:
            print(f"\nReached maximum limit ({max_value})")
            converged_value = current_value - 1
            break

    return converged_value, param_values, average_rcs_list, all_rcs_curves, all_iwavephi


# ## Run convergence study
#
# The convergence study is performed in two sequential steps based on the convergence order.
# First, one parameter is converged while the other is held fixed. Then the second parameter
# is converged using the converged value of the first parameter.

print("=" * 70)
print("SBR+ CONVERGENCE STUDY - Sequential Parameter Convergence")
print("=" * 70)

# ### Execute convergence iterations
#
# Run the convergence sweeps in the order specified by ``convergence_order``.

if convergence_order == "ray_density_first":
    print("\n" + "=" * 70)
    print(f"STEP 1: CONVERGING RAY DENSITY (Bounces fixed at {starting_bounce_number})")
    print("=" * 70)
    converged_ray_density, ray_densities, avg_rcs_ray, all_rcs_ray, all_phi_ray = run_convergence_sweep(
        hfss=hfss,
        sweep_param="ray_density",
        fixed_param_value=starting_bounce_number,
        Setup_Frequency=setup_frequency,
        ptd_utd_setting=ptd_utd_setting,
        convergence_threshold=convergence_threshold,
        convergence_method=convergence_method,
        start_value=starting_ray_density,
        max_value=20,
    )
    print("\n" + "=" * 70)
    print(f"STEP 2: CONVERGING BOUNCE NUMBER (Ray Density fixed at {converged_ray_density})")
    print("=" * 70)
    converged_bounce_number, bounce_numbers, avg_rcs_bounce, all_rcs_bounce, all_phi_bounce = run_convergence_sweep(
        hfss=hfss,
        sweep_param="bounce_number",
        fixed_param_value=converged_ray_density,
        Setup_Frequency=setup_frequency,
        ptd_utd_setting=ptd_utd_setting,
        convergence_threshold=convergence_threshold,
        convergence_method=convergence_method,
        start_value=starting_bounce_number,
        max_value=10,
    )
else:
    print("\n" + "=" * 70)
    print(f"STEP 1: CONVERGING BOUNCE NUMBER (Ray Density fixed at {starting_ray_density})")
    print("=" * 70)
    converged_bounce_number, bounce_numbers, avg_rcs_bounce, all_rcs_bounce, all_phi_bounce = run_convergence_sweep(
        hfss=hfss,
        sweep_param="bounce_number",
        fixed_param_value=starting_ray_density,
        Setup_Frequency=setup_frequency,
        ptd_utd_setting=ptd_utd_setting,
        convergence_threshold=convergence_threshold,
        convergence_method=convergence_method,
        start_value=starting_bounce_number,
        max_value=10,
    )
    print("\n" + "=" * 70)
    print(f"STEP 2: CONVERGING RAY DENSITY (Bounces fixed at {converged_bounce_number})")
    print("=" * 70)
    converged_ray_density, ray_densities, avg_rcs_ray, all_rcs_ray, all_phi_ray = run_convergence_sweep(
        hfss=hfss,
        sweep_param="ray_density",
        fixed_param_value=converged_bounce_number,
        Setup_Frequency=setup_frequency,
        ptd_utd_setting=ptd_utd_setting,
        convergence_threshold=convergence_threshold,
        convergence_method=convergence_method,
        start_value=starting_ray_density,
        max_value=20,
    )

# ## Final Summary

print("\n" + "=" * 70)
print("CONVERGENCE STUDY COMPLETE")
print("=" * 70)
print(f"Convergence Order:      {convergence_order}")
print(f"Convergence Method:     {convergence_method}")
print(f"Convergence Threshold:  {convergence_threshold} dB")
print(f"PDF/UTD Setting:        {ptd_utd_setting}")
print(f"Converged Ray Density:  {converged_ray_density}")
print(f"Converged Bounce Number:{converged_bounce_number}")
print(f"Total simulations run:  {len(ray_densities) + len(bounce_numbers)}")
print(f"  - Ray density sweep:  {len(ray_densities)} simulations")
print(f"  - Bounce number sweep:{len(bounce_numbers)} simulations")
print("=" * 70)

# ## Plotting
#
# Plotting the results outside of AEDT.

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Ray Density - RCS Curves
colors1 = plt.cm.viridis(np.linspace(0, 1, len(ray_densities)))
for i, (rd, rcs_curve, iwavephi) in enumerate(zip(ray_densities, all_rcs_ray, all_phi_ray)):
    axes[0, 0].plot(iwavephi, rcs_curve, color=colors1[i], linewidth=2, label=f"Ray Density = {rd}")
axes[0, 0].set_xlabel("IWavePhi Angle (degrees)", fontsize=11)
axes[0, 0].set_ylabel("RCS (dBsm)", fontsize=11)
axes[0, 0].set_title(f"Ray Density Convergence - RCS Curves", fontsize=12)
axes[0, 0].legend(loc="best", fontsize=9)
axes[0, 0].grid(True, alpha=0.3)

# Plot 2: Ray Density - Average RCS
axes[0, 1].plot(ray_densities, avg_rcs_ray, "bo-", linewidth=2, markersize=8)
axes[0, 1].set_xlabel("Ray Density Per Wavelength", fontsize=11)
axes[0, 1].set_ylabel("Average RCS (dBsm)", fontsize=11)
axes[0, 1].set_title("Ray Density - Average RCS Convergence", fontsize=12)
axes[0, 1].grid(True, alpha=0.3)

# Plot 3: Bounce Number - RCS Curves
colors2 = plt.cm.plasma(np.linspace(0, 1, len(bounce_numbers)))
for i, (bn, rcs_curve, iwavephi) in enumerate(zip(bounce_numbers, all_rcs_bounce, all_phi_bounce)):
    axes[1, 0].plot(iwavephi, rcs_curve, color=colors2[i], linewidth=2, label=f"Bounces = {bn}")
axes[1, 0].set_xlabel("IWavePhi Angle (degrees)", fontsize=11)
axes[1, 0].set_ylabel("RCS (dBsm)", fontsize=11)
axes[1, 0].set_title(f"Bounce Number Convergence - RCS Curves", fontsize=12)
axes[1, 0].legend(loc="best", fontsize=9)
axes[1, 0].grid(True, alpha=0.3)

# Plot 4: Bounce Number - Average RCS
axes[1, 1].plot(bounce_numbers, avg_rcs_bounce, "ro-", linewidth=2, markersize=8)
axes[1, 1].set_xlabel("Number of Bounces", fontsize=11)
axes[1, 1].set_ylabel("Average RCS (dBsm)", fontsize=11)
axes[1, 1].set_title("Bounce Number - Average RCS Convergence", fontsize=12)
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# ## Advanced post-processing
#
# For more advanced RCS analysis and visualization, you can use PyAEDT's ``get_rcs_data()`` method.
# This method exports RCS simulation data into a standardized metadata format and returns
# a ``MonostaticRCSExporter`` object for further processing.
#
# ### Using the radar explorer toolkit
#
# For advanced RCS analysis and visualization capabilities, install the radar explorer toolkit:
#
# ```bash
# pip install ansys-aedt-toolkits-radar-explorer
# ```
#
# The radar explorer toolkit provides powerful features for RCS data analysis:
#
# - **Interactive 3D RCS pattern visualization** with customizable viewing angles
# - **Polar and Cartesian plot formats** for different analysis perspectives
# - **Multi-frequency RCS comparison** to analyze frequency-dependent behavior
# - **Export capabilities** for various formats (CSV, JSON, images)
# - **Advanced filtering and data manipulation** tools
# - **Statistical analysis** of RCS patterns
#
# ### Example: Visualizing RCS data with the toolkit
#
# Here's a complete example showing how to export RCS data from HFSS and visualize it
# using the radar explorer toolkit. For more examples, visit the
# [radar explorer toolkit documentation](https://aedt.radar.explorer.toolkit.docs.pyansys.com/version/stable/examples/index.html).
#
# ```python
# # Export RCS data using PyAEDT's get_rcs_data method
# rcs_exporter = hfss.get_rcs_data(
#     setup_name="SBR",
#     frequencies=["10GHz"],
# )
#
# # Import the radar explorer toolkit
# from ansys.aedt.toolkits.radar_explorer.core import MonostaticRCSData, MonostaticRCSPlotter
#
# # Load the RCS data
# rcs_data = MonostaticRCSData(rcs_exporter)
#
# # Create a plotter instance
# plotter = MonostaticRCSPlotter(rcs_data)
#
# plotter.plot_3d()
# ```
#
# For more examples and detailed documentation, visit:
# https://aedt.radar.explorer.toolkit.docs.pyansys.com/version/stable/examples/index.html

# ## Finish
#
# ### Save the project

hfss.save_project()
hfss.release_desktop()

# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``. If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes all temporary files, including the project folder.

temp_folder.cleanup()
