# # Frequency Selective Surface
#
# This example shows how to use PyAEDT to model and simulate a frequency-selective
# surface (FSS) by applying the periodic (Floquet) boundary condition at
# the boundaries of a unit cell.
#
# Keywords: **HFSS**, **FSS**, **Floquet**.

# ## Prerequisites
#
# ### Perform imports

import os
import tempfile
import time
from pathlib import Path
import ansys.aedt.core
from ansys.aedt.core.downloads import download_file

# ### Define constants
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2025.1"
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
temp_path = Path(temp_folder.name)

# ## Launch Electronics Desktop (AEDT)

# ### Launch HFSS
#
# Create an HFSS design.

project_name = temp_path / "FSS.aedt"
hfss = ansys.aedt.core.Hfss(
    version=AEDT_VERSION, 
    project=str(project_name), 
    design="SquarePatch",
    non_graphical=NG_MODE,
    solution_type="Modal",
)

# ### Define a parameter
#
# Parameters can be defined in HFSS to run parametric studies. In this example,
# ``"patch_dim"`` will be used to modify the size of a square conducting
# patch in the center of the FSS.

hfss["patch_dim"] = "10mm"

# The parameter is assigned to the HFSS design as shown here.
# <img src="_static/design_param.svg" width="400">

# ## Model Preparation
#
# ### Define the unit cell
#
# The FSS unit cell will be defined from a 3D component.
# The 3D component is downloaded from the 
# [example data repository](https://github.com/ansys/example-data/tree/main/pyaedt) 
# and inserted into the HFSS design.

# 1. Download the component.

component_path = Path(download_file("fss_3d_component", destination=str(temp_path)))

# 2. Get the file name of the 3D component.
#    > **Note:** It should be the only file in the ``component_path`` folder.

unit_cell_path = component_path.glob("*.a3dcomp")[0]

# 3. Insert the component in HFSS

comp = hfss.modeler.insert_3d_component(str(unit_cell_path))

# You can retrieve the names of all 3D components defined in the HFSS design
# as shown below. In this case, only one component has been defined.

component_names = hfss.modeler.user_defined_component_names

# You can also get the name of each component from the
# ``name`` property.
#
# Check that they are the same.

# +
same = comp.name == component_names[0]
if same and len(component_names) == 1:
    msg = f"The single 3D component in this HFSS design is named '{comp.name}',\n"
    msg += "...proceed to the next step."
    
else:
    msg ="Something went wrong!"
print(msg)
# -

# ### Set component parameters
# The 3D component is a parameteric model. 
#
# <img src="_static/comp3d.svg" width="500">
#
# The HFSS parameter ``patch_dim`` can be assigned to
# the component parameter ``a`` to modify the size of the patch
# in the unit cell.
#
# > **Note:** Multiple instances of a 3D component can be used having different
# > parameter values for each instance. For example, consider
# > creating a "super-cell" having multiple component instances to improve the bandwidth
# > of the FSS.

comp.parameters["a"] = "patch_dim"

# ### Extend the solution domain
#
# Extend the solution domain in the $+z$ direction avoid evanescent
# fields from interacting with the Floquet port. 
#
# Placing the Floquet port too close to the 3D structure can result
# in evanescent fields on the Floquet port surface which would
# lead to erroneous results.
#
# The unit cell model is extended away from the 
# patch by ``z_extent``. The phase reference
# will later be moved back to the surface of the FSS by deembedding the
# port solution.
#
# <img src="_static/deembed.svg" width="400">

# +
period_x, period_y, z_dim = hfss.modeler.get_bounding_dimension()

z_extent = 3 * period_x   
region = hfss.modeler.create_air_region(
    z_pos=z_extent,
    is_percentage=False,
)

[x_min, y_min, z_min, x_max, y_max, z_max] = region.bounding_box
# -

# ### Assign boundary conditions and sources
#
# Assign the lattice pair periodic boundary conditions.

# +
boundaries = hfss.auto_assign_lattice_pairs(assignment=region.name)

msg = "The periodic boundary conditions are: "
msg += str(boundaries)
print(msg)
# -

# The Floquet port is asigned to the top surface of the solution domain
# where the plane
# wave is incident on the FSS. The periodicity of the FSS is defined
# via the arguments
# - ``lattice_origin``
# - ``lattice_a_end``
# - ``lattice_b_end``
#
# The phase reference is set to the surface of the FSS
# with deembedding.

floquet_boundary = hfss.create_floquet_port(
                               assignment=region.top_face_z,
                               lattice_origin=[0, 0, z_max],
                               lattice_a_end=[0, y_max, z_max],
                               lattice_b_end=[x_max, 0, z_max],
                               name="port_z_max",
                               deembed_distance=z_extent,
                               )

# ### Define solution setup
#
# The solution setup specifies details used to run
# the finite element analysis in HFSS. In thise example adaptive mesh
# refinement runs at 10 GHz while all other settings are set to
# default values. 
#
# The frequency sweep is used to specify the range over which scattering
# parameters will be calculated.

setup = hfss.create_setup("MySetup")
setup.props["Frequency"] = "10GHz"
setup.props["MaximumPasses"] = 10
hfss.create_linear_count_sweep(
    setup=setup.name,
    units="GHz",
    start_frequency=6,
    stop_frequency=15,
    num_of_freq_points=51,
    name="sweep1",
    sweep_type="Interpolating",
    interpolation_tol=6,
    save_fields=False,
)

# ### Run analysis
#
# Save the project and run the analysis.

hfss.save_project()
hfss.analyze()

# ## Postprocess
#
# Create S-parameter reports.

# +
all_quantities = hfss.post.available_report_quantities()
str_mag = []
str_ang = []

variation = {"Freq": ["All"]}

for i in all_quantities:
    str_mag.append("mag(" + i + ")")
    str_ang.append("ang_deg(" + i + ")")

mag_plot = hfss.post.create_report(
                    expressions=str_mag,
                    variations=variation,
                    plot_name="magnitude_plot",
                    )
phase_plot = hfss.post.create_report(
                    expressions=str_ang,
                    variations=variation,
                    plot_name="phase_plot",
                    )
# -

plot_data = hfss.get_traces_for_plot(category="phase(Z(")
report = hfss.post.create_report(plot_data)
solution = report.get_solution_data()
plt = solution.plot(solution.expressions)

# ## Release AEDT

help(hfss.post.create_report)

hfss.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell removes
# all temporary files, including the project folder.

temp_folder.cleanup()
