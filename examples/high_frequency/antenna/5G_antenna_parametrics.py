# # EDB: Layout Components
#
# This example shows how you can use EDB to create a parametric component using
# 3D Layout and use it in HFSS 3D.

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
# Constants help ensure consistency and avoid repetition throughout the example.

AEDT_VERSION = "2026.1"
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")


# ## Model Preparation
#
# ### Create primitive data classes to simplify geometry creation
#
# The ``Line``, ``Patch`` and ``Array`` classes wrap geometry
# operations and properties into simple Python classes that help
# simplify the creation of the microstrip
# array with the ``pyedb.Edb`` class.

# +
class Patch:
    def __init__(self, width:float =0.0, height:float=0.0, position:float=0.0):
        self.width = width
        self.height = height
        self.position = position

    @property
    def points(self):
        return [
            [self.position, -self.height/2],
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
            [-1e-3, - self.width / 2 - 1e-3],
            [self.length + 1e-3, -self.width / 2- 1e-3],
            [self.length + 1e-3, self.width /2 + 1e-3],
            [-1e-3, self.width / 2 + 1e-3],
        ]


# -

# ### Launch EDB
#
# The ``pyedb.Edb`` class can be used open an existing Edb instance or instantiate
# a new EDB project.

# +
aedb_path = os.path.join(temp_folder.name, "linear_array.aedb")

# Create an instance of the Edb class.
edb = pyedb.Edb(edbpath=aedb_path, version=AEDT_VERSION)
# -

# ### Build the stackup

# +
layers = {
    "materials": {"copper_high_cond": {"conductivity": 60000000}},
    "layers": {
        "TOP": {"type": "signal", "thickness": "35um", "material": "copper_high_cond"},
        "Substrat": {"type": "dielectric", "thickness": "0.5mm", "material": "Duroid (tm)"},
        "GND": {"type": "signal", "thickness": "35um", "material": "copper"},
        "Gap": {"type": "dielectric", "thickness": "0.05mm", "material": "Air"},
    },
}

edb.stackup.load(layers)
# -

# ### Create a patch antenna and feed line
#
# Instances of the ``Patch`` and ``Line``classes are used to define the geometry. These
# classes provide for parameterization of the array layout.
#
# <img src="_static\5G_antenna_parametrics\array_params.svg" width="600">
#
# Define parameters:

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

# Now use the ``LinearArray`` class to create the array.

# +
w2 = 2.29e-3
h2 = 3.3e-3
l2 = 1.9e-3
trace_w2 = 0.2e-3
rf_pin_location = [first_patch.width/4.0, 0]

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

# Add the ground conductor.
edb.modeler.create_polygon(linear_array.points, layer_name="GND", net_name="GND")

# Add the connector pin to use to assign the port.



pos_term = edb.excitation_manager.create_point_terminal(x=rf_pin_location[0],
                                                        y=rf_pin_location[1],
                                                        layer="TOP",
                                                        net="Array_antenna")
ref_term = edb.excitation_manager.create_point_terminal(x=rf_pin_location[0],
                                                        y=rf_pin_location[1],
                                                        layer="GND",
                                                        net="GND")
pos_term.reference_terminal = ref_term


# Display the model using the ``Edb.nets.plot()`` method.

edb.nets.plot()

# The EDB is complete. Now close the EDB and import it into HFSS as a "Layout Component".

edb.save()
edb.close()
print("EDB saved correctly to {}. You can import in AEDT.".format(aedb_path))

# ## Open the component in Electronics Desktop
#
# First create an instance of the ``pyaedt.Hfss`` class. If you set
# > ``non_graphical = False
#
# then AEDT user interface will be visible after the following cell is executed.
# It is now possible to monitor the progress in the UI as each of the following cells is executed.
# All commands can be run without the UI by changing the value of ``non_graphical``.

h3d = ansys.aedt.core.Hfss(
    project="Demo_3DComp",
    design="Linear_Array",
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=NG_MODE,
    close_on_exit=True,
    solution_type="Terminal",
)

# Set units to ``mm``.

h3d.modeler.model_units = "mm"

# ## Import the EDB as a 3D component
#
# The linear array can be imported into the 3D CAD interface of HFSS.
# The ability to combine layout components with 3D components enables mesh
# fusion and is very useful for building and simulating large assemblies.
#
# The following image shows the 3D layout component in the 3D CAD UI of HFSS.
#
# <img src="_static\5G_antenna_parametrics\layout_component_in_3d.svg" width="800">

component = h3d.modeler.insert_layout_component(aedb_path, parameter_mapping=True)

# ## Expose the component parameters
#
# If a layout component is parametric, you can expose and change parameters in HFSS

# +


w1_name = f"w1_{h3d.modeler.user_defined_component_names[0]}"
h3d[w1_name] = 0.0015
# -

# ### Radiation Boundary Assignment
#
# The 3D domain includes the air volume surrounding the antenna.
# This antenna will be simulted from 20 GHz - 50 GHz.
#
# A "radiation boundary" will be assigned to the outer boundaries of the domain.
# This boundary should be roughly one quarter wavelength away from the radiating structure:
#
# $$ \lambda/4 = \frac{c_0}{4 f} \approx 2.8mm $$

# +
h3d.modeler.fit_all()

h3d.modeler.create_air_region(2.8, 2.8, 2.8, 2.8, 2.8, 2.8, is_percentage=False)
h3d.assign_radiation_boundary_to_objects("Region")
# -

# ### Set up analysis
#
# The finite element mesh is adapted iteratively.
# The maximum number of adaptive passes is set using the ``MaximumPasses`` property.
# This model converges such that the $S_{11}$ is independent of the mesh.
# The default accuracy setting is:
# $$ \max(|\Delta S|) < 0.02 $$

setup = h3d.create_setup()
setup.props["Frequency"] = "20GHz"
setup.props["MaximumPasses"] = 10

# Specify properties of the frequency sweep:

sweep1 = setup.add_sweep(name="20GHz_to_50GHz")
sweep1.props["RangeStart"] = "20GHz"
sweep1.props["RangeEnd"] = "50GHz"
sweep1.update()

# Solve the project

h3d.analyze()

# ## Plot results outside AEDT
#
# Plot results using Matplotlib.

trace = h3d.get_traces_for_plot()
solution = h3d.post.get_solution_data(trace[0])
solution.plot()

# ## Plot far fields in AEDT
#
# Plot radiation patterns in AEDT.

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

# ## Plot far fields in AEDT
#
# Plot radiation patterns in AEDT

new_report.report_type = "3D Polar Plot"
new_report.secondary_sweep = "Phi"
new_report.create("Realized3D")

# ## Plot far fields outside AEDT
#
# Plot radiation patterns outside AEDT

solutions_custom = new_report.get_solution_data()
solutions_custom.plot_3d()

# ## Plot E Field on nets and layers
#
# Plot E Field on nets and layers in AEDT

h3d.post.create_fieldplot_layers_nets(
    [["TOP", "Array_antenna"]],
    "Mag_E",
    intrinsics={"Freq": "20GHz", "Phase": "0deg"},
    plot_name="E_Layers",
)

# ## Finish
#
# ### Save the project

h3d.save_project(os.path.join(temp_folder.name, "test_layout.aedt"))
h3d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ### Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
