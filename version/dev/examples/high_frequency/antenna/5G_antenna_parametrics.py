# # Create a 5G Antenna Layout Component
#
# This example uses PyEDB to create a microstrip antenna array in EDB and then
# imports it into HFSS as a 3D layout component.

# ## Prerequisites
#
# ### Perform imports

# +
import os
import tempfile
import time

import ansys.aedt.core
import pyedb

# -

# ### Define constants
# These constants keep the example configuration in one place.

AEDT_VERSION = "2026.1"
NG_MODE = False  # Set to ``True`` to run AEDT without the user interface.

# ### Create a temporary directory
#
# Create a temporary working directory. The generated project files are stored in
# ``temp_folder.name``.
#
# > **Note:** The final section removes the temporary folder. If you want to keep
# > the AEDT project or intermediate data, copy them before running the cleanup step.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")


# ## Build the EDB model
#
# ### Create helper classes for the geometry
#
# The ``Patch``, ``Line``, and ``LinearArray`` classes make it easier to define
# the array geometry before passing the polygon points to ``pyedb.Edb``.

# +
class Patch:
    def __init__(self, width: float = 0.0, height: float = 0.0, position: float = 0.0):
        self.width = width
        self.height = height
        self.position = position

    @property
    def points(self):
        return [
            [self.position, -self.height / 2],
            [self.position + self.width, -self.height / 2],
            [self.position + self.width, self.height / 2],
            [self.position, self.height / 2],
        ]


class Line:
    def __init__(self, length=0.0, width=0.0, position=0.0):
        self.length = length
        self.width = width
        self.position = position

    @property
    def points(self):
        return [
            [self.position, -self.width / 2],
            [self.position + self.length, -self.width / 2],
            [self.position + self.length, self.width / 2],
            [self.position, self.width / 2],
        ]


class LinearArray:
    def __init__(self, nb_patch=1, array_length=10e-3, array_width=5e-3):
        self.nbpatch = nb_patch
        self.length = array_length
        self.width = array_width

    @property
    def points(self):
        return [
            [-1e-3, -self.width / 2 - 1e-3],
            [self.length + 1e-3, -self.width / 2 - 1e-3],
            [self.length + 1e-3, self.width / 2 + 1e-3],
            [-1e-3, self.width / 2 + 1e-3],
        ]


# -

# ### Launch EDB
#
# Use ``pyedb.Edb`` to create a new EDB project.

# +
aedb_path = os.path.join(temp_folder.name, "linear_array.aedb")

# Create the EDB database.
edb = pyedb.Edb(edbpath=aedb_path, version=AEDT_VERSION)
# -

# ### Define the stackup
#
# Add a custom high-conductivity copper material and then build the layer stack
# from top to bottom using the ``pyedb.Edb.stackup`` API.

edb.materials.add_conductor_material(name="copper_high_cond", conductivity=60000000)
edb.materials.add_dielectric_material(name="Duroid (tm)", permittivity=2.2, dielectric_loss_tangent=0.0009)

edb.stackup.add_layer_top(name="TOP",
                          layer_type="signal",
                          thickness="35um",
                          material="copper_high_cond")
edb.stackup.add_layer_below(name="Substrat",
                            base_layer_name="TOP",
                            layer_type="dielectric",
                            thickness="0.5mm",
                            material="Duroid (tm)")
edb.stackup.add_layer_below(name="GND",
                            base_layer_name="Substrat",
                            layer_type="signal",
                            thickness="35um",
                            material="copper")

# ### Create the first patch and feed line
#
# Use the ``Patch`` and ``Line`` helpers to define the first radiating element and
# its feed line.
#
# <img src="_static/5G_antenna_parametrics/array_params.svg" width="600">
#
# Define the geometry dimensions:

# +
w1 = 1.4e-3
h1 = 1.2e-3
initial_position = 0.0
l1 = 2.4e-3
trace_w = 0.3e-3

first_patch = Patch(width=w1, height=h1, position=initial_position)
edb.modeler.create_polygon(first_patch.points, layer_name="TOP", net_name="Array_antenna")
first_line = Line(length=l1, width=trace_w, position=first_patch.width)
edb.modeler.create_polygon(first_line.points, layer_name="TOP", net_name="Array_antenna")
# -

# Use the ``LinearArray`` helper to generate the remaining antenna elements.

# +
w2 = 2.29e-3
h2 = 3.3e-3
l2 = 1.9e-3
trace_w2 = 0.2e-3
rf_pin_location = [first_patch.width / 4.0, 0]

patch = Patch(width=w2, height=h2)
line = Line(length=l2, width=trace_w2)
linear_array = LinearArray(nb_patch=8, array_width=patch.height)

current_patch = 1
current_position = first_line.position + first_line.length

while current_patch <= linear_array.nbpatch:
    patch.position = current_position
    edb.modeler.create_polygon(patch.points, layer_name="TOP", net_name="Array_antenna")
    current_position = current_position + patch.width
    if current_patch < linear_array.nbpatch:
        line.position = current_position
        edb.modeler.create_polygon(line.points, layer_name="TOP", net_name="Array_antenna")
        current_position = current_position + line.length
    current_patch += 1

linear_array.length = current_position
# -

# Add the ground reference conductor.
edb.modeler.create_polygon(linear_array.points, layer_name="GND", net_name="GND")

# Add point terminals that define the feed and its reference.
pos_term = edb.excitation_manager.create_point_terminal(
    x=rf_pin_location[0],
    y=rf_pin_location[1],
    layer="TOP",
    net="Array_antenna",
)
ref_term = edb.excitation_manager.create_point_terminal(
    x=rf_pin_location[0],
    y=rf_pin_location[1],
    layer="GND",
    net="GND",
)
pos_term.reference_terminal = ref_term

# Display the layout.

edb.nets.plot()

# Save and close the EDB project before importing it into HFSS as a layout component.

edb.save()
edb.close()
print(f"EDB saved to {aedb_path}. It is ready to be imported into AEDT.")

# ## Open the layout component in HFSS
#
# Create an ``ansys.aedt.core.Hfss`` instance. When ``non_graphical=False``, the
# AEDT user interface opens so you can monitor each step interactively.

h3d = ansys.aedt.core.Hfss(
    project="Demo_3DComp",
    design="Linear_Array",
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
    close_on_exit=True,
    solution_type="Terminal",
)

# Set the model units to ``mm``.

h3d.modeler.model_units = "mm"

# ## Import the EDB as a 3D layout component
#
# The linear array can be inserted into the HFSS 3D Modeler. Combining layout
# components with 3D geometry is useful for mesh fusion and for simulating larger
# assemblies.
#
# The following image shows the imported layout component in the HFSS 3D user interface.
#
# <img src="_static/5G_antenna_parametrics/layout_component_in_3d.svg" width="800">

component = h3d.modeler.insert_layout_component(aedb_path)

# ### Assign a radiation boundary
#
# The 3D domain includes the air volume surrounding the antenna. This antenna is
# simulated from 20 GHz to 50 GHz.
#
# Assign a radiation boundary to the outer faces of the air region. A common rule
# of thumb is to place this boundary about one quarter wavelength from the radiator:
#
# $$ \lambda / 4 = \frac{c_0}{4f} \approx 2.8\,\text{mm} $$

# +
h3d.modeler.fit_all()

h3d.modeler.create_air_region(2.8, 2.8, 2.8, 2.8, 2.8, 2.8, is_percentage=False)
h3d.assign_radiation_boundary_to_objects("Region")
# -

# ### Set up the analysis
#
# HFSS adapts the finite element mesh iteratively. Use ``MaximumPasses`` to limit
# the number of adaptive refinements. The default convergence target is:
#
# $$ \max(|\Delta S|) < 0.02 $$

setup = h3d.create_setup()
setup.props["Frequency"] = "20GHz"
setup.props["MaximumPasses"] = 10

# Define the frequency sweep.

sweep1 = setup.add_sweep(name="20GHz_to_50GHz")
sweep1.props["RangeStart"] = "20GHz"
sweep1.props["RangeEnd"] = "50GHz"
sweep1.update()

# Solve the project.

h3d.analyze()

# ## Plot S-parameter results outside AEDT
#
# Plot the first available trace with Matplotlib.

trace = h3d.get_traces_for_plot()
solution = h3d.post.get_solution_data(trace[0])
solution.plot()

# ## Create a 2D far-field report in AEDT
#
# Create a far-field report for the realized gain.

# +
variations = {}
variations["Freq"] = ["20GHz"]
variations["Theta"] = ["All"]
variations["Phi"] = ["All"]
h3d.insert_infinite_sphere(name="3D")

new_report = h3d.post.reports_by_category.far_field("db(RealizedGainTotal)", h3d.nominal_adaptive, "3D")
new_report.variations = variations
new_report.primary_sweep = "Theta"
new_report.create("Realized2D")
# -

# ## Create a 3D far-field report in AEDT
#
# Reuse the same report object and switch it to a 3D polar plot.

new_report.report_type = "3D Polar Plot"
new_report.secondary_sweep = "Phi"
new_report.create("Realized3D")

# ## Plot far-field data outside AEDT
#
# Retrieve the far-field data and plot it outside AEDT.

solutions_custom = new_report.get_solution_data()
solutions_custom.plot_3d()

# ## Plot the electric field on selected nets and layers
#
# Create a field plot for the electric-field magnitude in AEDT.

h3d.post.create_fieldplot_layers_nets(
    [["TOP", "Array_antenna"]],
    "Mag_E",
    intrinsics={"Freq": "20GHz", "Phase": "0deg"},
    plot_name="E_Layers",
)

# ## Save and clean up
#
# ### Save the project

h3d.save_project(os.path.join(temp_folder.name, "test_layout.aedt"))
h3d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ### Clean up
#
# All generated project files are stored in ``temp_folder.name``. If you are
# running this example as a notebook and want to keep those files, copy them
# before executing the cleanup step below.

temp_folder.cleanup()
