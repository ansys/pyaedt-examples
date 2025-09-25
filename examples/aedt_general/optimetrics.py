# # Optimetrics setup
#
# This example shows how to use PyAEDT to create a project in HFSS and create all optimetrics
# setups.
#
# Keywords: **AEDT**, **General**, **optimetrics**.

# ## Perform imports and define constants
# Import the required packages.

# +
import os
import tempfile
import time

import ansys.aedt.core
# -

# Define constants.

AEDT_VERSION = "2025.2"
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Initialize HFSS and create variables
#
# Initialize the ``Hfss`` object and create two needed design variables,
# ``w1`` and ``w2``.

# +
project_name = os.path.join(temp_folder.name, "optimetrics.aedt")

hfss = ansys.aedt.core.Hfss(
    project=project_name,
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
    solution_type="Modal",
)

hfss["w1"] = "1mm"
hfss["w2"] = "100mm"
# -

# ## Create waveguide with sheets on it
#
# Create one of the standard waveguide structures and parametrize it.
# You can also create rectangles of waveguide openings and assign ports later.

# +
wg1, p1, p2 = hfss.modeler.create_waveguide(
    [0, 0, 0],
    hfss.AXIS.Y,
    "WG17",
    wg_thickness="w1",
    wg_length="w2",
    create_sheets_on_openings=True,
)

model = hfss.plot(show=False)

model.show_grid = False
model.plot(os.path.join(hfss.working_directory, "Image.jpg"))
# -

# ## Create wave ports on sheets
#
# Create two wave ports on the sheets.

hfss.wave_port(p1, integration_line=hfss.AxisDir.ZPos, name="1")
hfss.wave_port(p2, integration_line=hfss.AxisDir.ZPos, name="2")

# ## Create setup and frequency sweep
#
# Create a setup and a frequency sweep to use as the base for optimetrics
# setups.

setup = hfss.create_setup()
hfss.create_linear_step_sweep(
    setup=setup.name,
    unit="GHz",
    start_frequency=1,
    stop_frequency=5,
    step_size=0.1,
    name="Sweep1",
    save_fields=True,
)

# ## Create optimetrics analyses
#
# ### Create parametric analysis
#
# Create a simple optimetrics parametrics analysis with output calculations.

sweep = hfss.parametrics.add("w2", 90, 200, 5)
sweep.add_variation("w1", 0.1, 2, 10)
sweep.add_calculation(calculation="dB(S(1,1))", ranges={"Freq": "2.5GHz"})
sweep.add_calculation(calculation="dB(S(1,1))", ranges={"Freq": "2.6GHz"})

# ### Create sensitivity analysis
#
# Create an optimetrics sensitivity analysis with output calculations.

sweep2 = hfss.optimizations.add(
    calculation="dB(S(1,1))", ranges={"Freq": "2.5GHz"}, optimization_type="Sensitivity"
)
sweep2.add_variation("w1", 0.1, 3, 0.5)
sweep2.add_calculation(calculation="dB(S(1,1))", ranges={"Freq": "2.6GHz"})

# ### Create an optimization analysis
#
# Create an optimization analysis based on goals and calculations.

sweep3 = hfss.optimizations.add(calculation="dB(S(1,1))", ranges={"Freq": "2.5GHz"})
sweep3.add_variation("w1", 0.1, 3, 0.5)
sweep3.add_goal(calculation="dB(S(1,1))", ranges={"Freq": "2.6GHz"})
sweep3.add_goal(calculation="dB(S(1,1))", ranges={"Freq": ("2.6GHz", "5GHz")})
sweep3.add_goal(
    calculation="dB(S(1,1))",
    ranges={"Freq": ("2.6GHz", "5GHz")},
    condition="Maximize",
)

# ### Create a DesignXplorer optimization
#
# Create a DesignXplorer optimization based on a goal and a calculation.

sweep4 = hfss.optimizations.add(
    calculation="dB(S(1,1))",
    ranges={"Freq": "2.5GHz"},
    optimization_type="DesignExplorer",
)
sweep4.add_goal(calculation="dB(S(1,1))", ranges={"Freq": "2.6GHz"})

# ### Create a Design of Experiments (DOE)
#
# Create a DOE based on a goal and a calculation.

sweep5 = hfss.optimizations.add(
    calculation="dB(S(1,1))", ranges={"Freq": "2.5GHz"}, optimization_type="DXDOE"
)

# ### Create another DOE
#
# Create another DOE based on a goal and a calculation.

region = hfss.modeler.create_region()
hfss.assign_radiation_boundary_to_objects(region)
hfss.insert_infinite_sphere(name="Infinite_1")
sweep6 = hfss.optimizations.add(
    calculation="RealizedGainTotal",
    solution=hfss.nominal_adaptive,
    ranges={"Freq": "5GHz", "Theta": ["0deg", "10deg", "20deg"], "Phi": "0deg"},
    context="Infinite_1",
)

# ## Release AEDT

hfss.save_project()
hfss.release_desktop()
time.sleep(3)  # Allow AEDT to shut down before cleaning the temporary project folder.

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes
# all temporary files, including the project folder.

temp_folder.cleanup()
