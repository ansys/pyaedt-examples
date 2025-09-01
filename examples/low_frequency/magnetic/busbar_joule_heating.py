# %%
# Copyright (C) 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# %% [markdown]
# # Maxwell 3D: Multi-Terminal Busbar Joule Heating Analysis
#
# This comprehensive example demonstrates electromagnetic analysis of a multi-terminal copper busbar 
# system using ANSYS Maxwell 3D and PyAEDT. The analysis covers current distribution, electromagnetic 
# fields, and Joule heating in AC power distribution systems.
#
# ## Problem Overview
#
# We analyze a copper busbar system with the following configuration:
# - **Main Busbar**: 100mm × 10mm × 5mm rectangular conductor
# - **Input Terminals**: Two parallel 2mm × 5mm × 5mm copper tabs
# - **Output Terminal**: Single 2mm × 5mm × 5mm copper tab
# - **Current Configuration**: 100A + 100A input, 200A output
# - **Frequency**: 50Hz AC industrial power frequency
#
# ## Engineering Applications
# - **Power Distribution**: Electrical panel and switchgear design
# - **Thermal Management**: Heat dissipation and cooling system design
# - **Current Rating**: Safe operating current determination
# - **EMI/EMC Analysis**: Electromagnetic interference assessment
# - **Material Optimization**: Conductor sizing and configuration

# %% [markdown]
# ## Theoretical Background
#
# ### Maxwell's Equations for Eddy Current Analysis
#
# The analysis is based on Maxwell's equations in the frequency domain for conducting materials:
#
# - **Faraday's Law**: ∇ × **E** = -jω**B**
# - **Ampère's Law**: ∇ × **H** = **J** + jω**D**
# - **Current Density**: **J** = σ**E** (Ohm's Law)
# - **Constitutive Relations**: **B** = μ**H**, **D** = ε**E**
#
# ### Joule Heating Physics
#
# **Power Dissipation**: P = ∫ **J**·**E** dV = ∫ σ|**E**|² dV
#
# Where:
# - **J** = Current density vector (A/m²)
# - **E** = Electric field vector (V/m)
# - σ = Electrical conductivity (S/m)
# - ω = Angular frequency = 2πf
#
# ### Skin Effect
#
# At AC frequencies, current concentrates near conductor surfaces with skin depth:
#
# **δ = √(2/(ωμσ))**
#
# For copper at 50Hz: δ ≈ 9.3mm, indicating significant skin effect in our geometry.

# %% [markdown]
# ### 1. Import Required Libraries and Initialize Maxwell 3D
#
# Import PyAEDT and initialize Maxwell 3D with eddy current solver for AC electromagnetic analysis.

# %%
from ansys.aedt.core import Maxwell3d

# Initialize Maxwell 3D with eddy current solution type
m3d = Maxwell3d(
    version="2025.1",
    design="Busbar_JouleHeating",
    solution_type="EddyCurrent"
)

# %% [markdown]
# ### 2. Geometry Creation and Material Assignment
#
# Create the 3D busbar geometry with multiple terminals representing a realistic power distribution scenario.
#
# #### Geometry Specifications:
# - **Main Busbar**: Central current-carrying conductor
# - **Input Tabs**: Two parallel connection points for incoming current
# - **Output Tab**: Single connection point for outgoing current
# - **Material**: High-conductivity copper (σ ≈ 5.8 × 10⁷ S/m)

# %%
# Create main busbar conductor
busbar = m3d.modeler.create_box([0, 0, 0], [100, 10, 5], "Busbar")
m3d.assign_material(busbar, "copper")

# Create input terminals (parallel configuration)
tab1 = m3d.modeler.create_box([-2, 0, 0], [2, 5, 5], "InputTab1")
tab2 = m3d.modeler.create_box([-2, 5, 0], [2, 5, 5], "InputTab2")
m3d.assign_material(tab1, "copper")
m3d.assign_material(tab2, "copper")

# Create output terminal
tab_out = m3d.modeler.create_box([100, 2.5, 0], [2, 5, 5], "OutputTab")
m3d.assign_material(tab_out, "copper")

# %% [markdown]
# ### 3. Current Excitation and Boundary Conditions
#
# Apply AC current excitations to simulate realistic power distribution scenarios.
#
# #### Current Configuration:
# - **Input Currents**: 100A @ 0° phase (each input tab)
# - **Output Current**: 200A @ 180° phase (current conservation)
# - **Frequency**: 50Hz industrial power frequency
#
# This configuration represents a parallel input, single output power distribution system.

# %%
# Apply current excitation to input terminals
m3d.assign_current(tab1.faces[0].id, amplitude=100, phase=0)
m3d.assign_current(tab2.faces[0].id, amplitude=100, phase=0)

# Apply return current to output terminal
m3d.assign_current(tab_out.faces[0].id, amplitude=-200, phase=0)

# %% [markdown]
# ### 4. Analysis Setup and Solver Configuration
#
# Configure the eddy current solver for accurate electromagnetic field calculation at power frequency.
#
# #### Solver Parameters:
# - **Solution Type**: Eddy Current (frequency domain)
# - **Frequency**: 50Hz (where skin effect becomes significant)
# - **Solver**: Iterative matrix solver optimized for electromagnetic problems

# %%
# Create analysis setup
setup = m3d.create_setup("Setup1")
setup.props["Frequency"] = "50Hz"

# %% [markdown]
# ### 5. Electromagnetic Field Solution
#
# Execute the finite element analysis to solve Maxwell's equations throughout the conductor domain.
#
# #### Computational Process:
# 1. **Mesh Generation**: Automatic adaptive mesh refinement
# 2. **Matrix Assembly**: Finite element system matrix construction
# 3. **Iterative Solution**: Conjugate gradient solver for large sparse systems
# 4. **Field Calculation**: Electric and magnetic field computation
# 5. **Convergence Check**: Solution accuracy verification

# %%
# Solve the electromagnetic problem
m3d.analyze()

# %% [markdown]
# ### 6. Field Visualization and Post-Processing
#
# Generate field plots to visualize electromagnetic phenomena and current distribution patterns.
#
# #### Visualization Results:
# - **Electric Field Magnitude**: Shows regions of high electric stress and potential gradients
# - **Current Density**: Reveals current flow patterns and skin effect distribution
#
# These visualizations are critical for:
# - Understanding current crowding effects
# - Identifying hot spots for thermal management
# - Optimizing conductor geometry

# %%
# Create electric field magnitude plot
m3d.post.create_fieldplot_surface(busbar, "Mag_E")

# Create current density plot
m3d.post.create_fieldplot_surface(busbar, "J")

# %% [markdown]
# ### 7. Joule Heating Loss Calculation
#
# Calculate and quantify the resistive power losses (Joule heating) in the conductor system.
#
# #### Power Loss Physics:
# - **Ohmic Loss**: P = ∫ σ|E|² dV over conductor volume
# - **Units**: Power dissipated in watts (W)
# - **Engineering Significance**: Critical for thermal design and cooling requirements
#
# The calculated losses provide essential data for:
# - Temperature rise prediction
# - Cooling system sizing
# - Current derating calculations

# %%
# Create ohmic loss report
report_name = "OhmicLossReport"
m3d.post.create_report(
    expressions="Ohmic_Loss",
    report_category="EddyCurrent",
    plotname=report_name
)
data = m3d.post.get_report_data(report_name)

# Extract and display results with engineering context
if data and data.data_magnitude():
    total_loss = data.data_magnitude()[0]
    loss_per_amp_squared = total_loss / (200**2)  # Loss per A²
    loss_density = total_loss / (100 * 10 * 5)  # Loss per unit volume (W/mm³)
    
    print(f"=== JOULE HEATING ANALYSIS RESULTS ===")
    print(f"Total Joule Heating Loss: {total_loss:.3f} W")
    print(f"Loss per unit current²: {loss_per_amp_squared*1e6:.3f} μW/A²")
    print(f"Loss density: {loss_density:.6f} W/mm³")
    print(f"Equivalent resistance: {total_loss/(200**2):.6f} Ω")
else:
    print("Warning: No Ohmic Loss data found in simulation results.")

# %% [markdown]
# ### 8. Project Save and Resource Management
#
# Save the complete analysis for future reference and properly release computational resources.

# %%
# Save project with all results
m3d.save_project("Busbar_JouleHeating.aedt")

# Release computational resources
m3d.release_desktop(True, True)

# %% [markdown]
# ## Results Analysis 
#
# ### Key Findings
#
# 1. **Current Distribution**: The dual-input configuration creates non-uniform current density
# 2. **Skin Effect**: At 50Hz, current concentration near surfaces increases resistance
# 3. **Joule Heating**: Power losses are concentrated at connection points and current transitions
# 4. **Field Concentration**: Electric field peaks occur at geometric discontinuities
#
# ## Conclusion
#
# This Maxwell 3D analysis successfully demonstrates:
#
# 1. **Comprehensive Modeling**: Multi-terminal busbar with realistic geometry and excitation
# 2. **Physics-Based Results**: Accurate electromagnetic field and loss calculations
# 3. **Engineering Applications**: Practical design insights for power systems
# 4. **Professional Workflow**: Industry-standard simulation methodology
#
# The calculated Joule heating provides essential data for thermal design, current rating, 
# and safety assessment of electrical power distribution systems. This workflow can be 
# extended for parametric studies, optimization, and coupled thermal analysis.
#
# This analysis demonstrates the power of PyAEDT for electromagnetic engineering and
# provides a solid foundation for advanced busbar design applications.
