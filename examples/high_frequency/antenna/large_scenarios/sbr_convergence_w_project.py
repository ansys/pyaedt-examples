# # SBR Convergence
#
# This example runs a convergence test on SBR+ setup parameters mainly
# ray density and number of bounces. The goal is to assure final results
# are not affected by analysis settings. In this example total RCS is demonstrated
# but other results can be used as well.
#
# Keywords: **SBR+**, **Ray density**, **number of bounces**, **convergence**.

# ## Prerequisites
# This examples can either download an example project or connect to
# an already open SBR+ design.
# ### Perform imports
#
# Import the packages required to run this example.


import tempfile
import time

import matplotlib.pyplot as plt
import numpy as np
from ansys.aedt.core.examples.downloads import download_file
from ansys.aedt.core.hfss import Hfss

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.2"
NG_MODE = False
use_example_project = False

# ### Setup based on user selection
#
# Using the example project - create new desktop session
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in this notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.
#
# ### Download model
#
# The model used in this example will be downloaded from the
# [example-data](https://github.com/ansys/example-data)
# GitHub repository.


if use_example_project:
    temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
    print(f"Temporary folder: {temp_folder.name}")

    project_path = download_file("sbr_convergence", "trihedral_rcs.aedt", temp_folder.name)

    hfss = Hfss(
        project=project_path,
        version=AEDT_VERSION,
        non_graphical=NG_MODE,
        new_desktop=True,
    )
else:
    print("Connecting to existing AEDT session...")

    hfss = Hfss(
        version=AEDT_VERSION,
        non_graphical=NG_MODE,
        new_desktop=False,
    )

    print(f"Connected to project: {hfss.project_name}")
    print(f"Active design: {hfss.design_name}")

    if hfss.solution_type != "SBR+":
        raise ValueError(f"Active design '{hfss.design_name}' is not an SBR+ design. " f"Current solution type: {hfss.solution_type}. " f"Please activate an SBR+ design before running this script.")

    temp_folder = None


# ### User Parameters
#
# parameters for SBR+ setup

Setup_Frequency = ["10GHz"]
convergence_threshold = 0.5  # dB absolute error
enable_PTD = False
enable_UTD = False
convergence_method = "point_to_point"  # "average" or "point_to_point"
convergence_order = "bounces_first"  # "ray_density_first" or "bounces_first"


# ### Fixed starting values
#
# starting values for convergence test

starting_ray_density = 1
starting_bounce_number = 2


# ### PDT/UTD Settings

if enable_PTD and enable_UTD:
    ptd_utd_setting = "PDF Correction + UTD Rays"
elif enable_PTD and not enable_UTD:
    ptd_utd_setting = "PDF Correction"
elif not enable_PTD and enable_UTD:
    ptd_utd_setting = "UTD Rays"
else:
    ptd_utd_setting = "None"

print(f"PDF: {enable_PTD}, UTD: {enable_UTD} → Setting: '{ptd_utd_setting}'")
print(f"Convergence Method: {convergence_method}")
print(f"Convergence Order:  {convergence_order}")


# ### CONVERGENCE CHECK FUNCTION


def check_convergence(rcs_values, previous_rcs_values, iwavephi_values, threshold, method):
    """
    Check convergence based on selected method.
    Returns: (converged, max_change, mean_change, max_change_index)
    """
    if method == "average":
        current_avg = np.mean(rcs_values)
        previous_avg = np.mean(previous_rcs_values)
        change = np.abs(current_avg - previous_avg)
        print(f"  Previous Average RCS: {previous_avg:.4f} dBsm")
        print(f"  Current  Average RCS: {current_avg:.4f} dBsm")
        print(f"  Average change: {change:.4f} dB")
        return change < threshold, change, change, 0

    elif method == "point_to_point":
        absolute_changes = np.abs(rcs_values - previous_rcs_values)
        max_change = np.max(absolute_changes)
        max_change_index = np.argmax(absolute_changes)
        mean_change = np.mean(absolute_changes)
        print(f"  Max point change:  {max_change:.4f} dB at IWavePhi = {iwavephi_values[max_change_index]:.1f}°")
        print(f"  Mean point change: {mean_change:.4f} dB")
        return max_change < threshold, max_change, mean_change, max_change_index


# ### Convergence Sweep Function
#
# Run a convergence sweep for either ray_density or bounce_number.
#
# #### Parameters
#
# sweep_param      : "ray_density" or "bounce_number" - which parameter to sweep
#
# fixed_param_name : name of the fixed parameter for printing
#
# fixed_param_value: value of the fixed parameter
#
# start_value      : starting value for the sweep
#
# max_value        : maximum value before stopping
#
# #### Returns
#
# converged_value  : the value at which convergence was reached
#
# param_values     : list of all tested values
#
# average_rcs_list : list of average RCS for each iteration
#
# all_rcs_curves   : list of all RCS curves
#
# all_iwavephi     : list of all IWavePhi arrays


def run_convergence_sweep(hfss, sweep_param, fixed_param_name, fixed_param_value, Setup_Frequency, ptd_utd_setting, convergence_threshold, convergence_method, start_value, max_value):

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

        hfss.analyze_setup("SBR")

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


# ### Run Convergence Study
#
# The study is run in two sequential steps based on the convergence order.

print("=" * 70)
print("SBR+ CONVERGENCE STUDY - Sequential Parameter Convergence")
print("=" * 70)

# ### starting Convergence Study
#


if convergence_order == "ray_density_first":
    print("\n" + "=" * 70)
    print(f"STEP 1: CONVERGING RAY DENSITY (Bounces fixed at {starting_bounce_number})")
    print("=" * 70)
    converged_ray_density, ray_densities, avg_rcs_ray, all_rcs_ray, all_phi_ray = run_convergence_sweep(
        hfss=hfss,
        sweep_param="ray_density",
        fixed_param_name="bounce_number",
        fixed_param_value=starting_bounce_number,
        Setup_Frequency=Setup_Frequency,
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
        fixed_param_name="ray_density",
        fixed_param_value=converged_ray_density,
        Setup_Frequency=Setup_Frequency,
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
        fixed_param_name="ray_density",
        fixed_param_value=starting_ray_density,
        Setup_Frequency=Setup_Frequency,
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
        fixed_param_name="bounce_number",
        fixed_param_value=converged_bounce_number,
        Setup_Frequency=Setup_Frequency,
        ptd_utd_setting=ptd_utd_setting,
        convergence_threshold=convergence_threshold,
        convergence_method=convergence_method,
        start_value=starting_ray_density,
        max_value=20,
    )

# ### Final Summary
# printing results of convergence
#

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

# ### Plotting
# plotting the results outside of AEDT

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

colors1 = plt.cm.viridis(np.linspace(0, 1, len(ray_densities)))
for i, (rd, rcs_curve, iwavephi) in enumerate(zip(ray_densities, all_rcs_ray, all_phi_ray)):
    axes[0, 0].plot(iwavephi, rcs_curve, color=colors1[i], linewidth=2, label=f"Ray Density = {rd}")
axes[0, 0].set_xlabel("IWavePhi Angle (degrees)", fontsize=11)
axes[0, 0].set_ylabel("RCS (dBsm)", fontsize=11)
axes[0, 0].set_title(f"Ray Density Convergence - RCS Curves", fontsize=12)
axes[0, 0].legend(loc="best", fontsize=9)
axes[0, 0].grid(True, alpha=0.3)


axes[0, 1].plot(ray_densities, avg_rcs_ray, "bo-", linewidth=2, markersize=8)
axes[0, 1].set_xlabel("Ray Density Per Wavelength", fontsize=11)
axes[0, 1].set_ylabel("Average RCS (dBsm)", fontsize=11)
axes[0, 1].set_title("Ray Density - Average RCS Convergence", fontsize=12)
axes[0, 1].grid(True, alpha=0.3)


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

hfss.save_project()
hfss.release_desktop(close_desktop=False, close_projects=False)

# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes
# all temporary files, including the project folder.

if use_example_project and temp_folder is not None:
    temp_folder.cleanup()
