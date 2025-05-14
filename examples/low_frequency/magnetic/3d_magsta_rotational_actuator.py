# # 3D Rotational Actuator
#
# In this example the rotational position of the actuator is defined and controled by a global parameter named ``angle``.
# By leveraging the magnetostatics formulation we can sweep through the rotational motion 
# and calculate the change in coil inductance, and field in a non-linear core.
#
# The model also shows how to set up a custom non-linear material using BH curve data.
#
# Keywords: **Maxwell3D**, **3D**, **magnetostatic**, **rotational motion**, **parametric sweep**, **inductance**,
# **installation example**
#

# ## Prerequisites
#
# ### Perform imports

# +
import os
import tempfile
import time
import csv

import ansys.aedt.core  # Interface to Ansys Electronics Desktop
# -

# ### Define constants

AEDT_VERSION = "2025.1"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.


# ### Create temporary directory
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ### Launch Maxwell 3d
# Create an instance of the ``Maxwell3d`` class. The Ansys Electronics Desktop will be launched
# with an active Maxwell2D design. The ``m3d`` object is subsequently used to create and simulate the actuator model.

project_name = os.path.join(temp_folder.name, "rotational_actuator.aedt")
m3d = ansys.aedt.core.Maxwell3d(
    project=project_name,
    design="3d_magsta_actuator",
    solution_type="Magnetostatic",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# ## Model Preparation
#
# ### Declare and initialize design parameters
# The ``angle`` parameter will be used to sweep through the actuators rotational motion

m3d["angle"] = "29deg"

# ### Create 3D model
#
# #### Set model units
#

m3d.modeler.model_units = "mm"

# #### Create non-linear magnetic material with single valued BH curve
#
# Create list with  BH curve data

bh_curve = [[0.0, 0.0],
            [4000.0, 1.413],
            [8010.0, 1.594],
            [16010.0, 1.751],
            [24020.0, 1.839],
            [32030.0, 1.896],
            [40030.0, 1.936],
            [48040.0, 1.967],
            [64050.0, 2.008],
            [80070.0, 2.042],
            [96080.0, 2.073],
            [112100.0, 2.101],
            [128110.0, 2.127],
            [144120.0, 2.151],
            [176150.0, 2.197],
            [208180.0, 2.24],
            [272230.0, 2.325],
            [304260.0, 2.37],
            [336290.0, 2.42],
            [396000.0, 2.5]]

# Create custom material and add it to the AEDT library using the ``add_material`` method

arm_steel = m3d.materials.add_material(name="arm_steel")
arm_steel.conductivity = 2000000
arm_steel.permeability.value = bh_curve

# #### Create outer arm

outer_arm = m3d.modeler.create_cylinder(orientation=ansys.aedt.core.constants.AXIS.Z ,origin=[0,0,0],radius=104.5,height=25.4,num_sides=0, name="Outer_arm", material=arm_steel.name)
cylinder_tool = m3d.modeler.create_cylinder(orientation=ansys.aedt.core.constants.AXIS.Z ,origin=[0,0,0],radius=83.1,height=25.4,num_sides=0, name="Cylinder_tool")
m3d.modeler.subtract([outer_arm],[cylinder_tool], keep_originals=False)
box_1 = m3d.modeler.create_box(origin=[-13.9 ,0 ,0],sizes=[27.8,-40,25.4], name="Box1")
m3d.modeler.move(box_1,vector=[0,-45,0])
m3d.modeler.duplicate_and_mirror(assignment=box_1,origin=[0,0,0],vector=[0,1,0])
m3d.modeler.unite([outer_arm, box_1.name, box_1.name+"_1"])
cylinder_1 = m3d.modeler.create_cylinder(orientation=ansys.aedt.core.constants.AXIS.Z ,origin=[0,0,0],radius=53.75,height=25.4,num_sides=0, name="Cylinder1")
m3d.modeler.subtract([outer_arm],[cylinder_1], keep_originals=False)
outer_arm.color="(192 192 192)"

# #### Create inner arm

inner_arm = m3d.modeler.create_cylinder(orientation=ansys.aedt.core.constants.AXIS.Z ,origin=[0,0,0],radius=38.1,height=25.4,num_sides=0, name="Inner_arm", material=arm_steel.name)
shaft = m3d.modeler.create_cylinder(orientation=ansys.aedt.core.constants.AXIS.Z ,origin=[0,0,0],radius=25.4,height=25.4,num_sides=0, name="shaft")
m3d.modeler.subtract([inner_arm],[shaft], keep_originals=False)
box_2 = m3d.modeler.create_box(origin=[-12.7 ,0 ,0],sizes=[25.4,-20,25.4], name="Box2")
m3d.modeler.move(box_2,vector=[0,-35,0])
m3d.modeler.duplicate_and_mirror(assignment=box_2,origin=[0,0,0],vector=[0,1,0])
m3d.modeler.unite([inner_arm, box_2.name, box_2.name+"_1"])
finalpole2 = m3d.modeler.create_cylinder(orientation=ansys.aedt.core.constants.AXIS.Z ,origin=[0,0,0],radius=51.05,height=25.4,num_sides=0, name="finalpole2")
m3d.modeler.intersect(assignment=[inner_arm, finalpole2])
inner_arm.color="(192 192 192)"

# #### Create a local/relative coordinate system

m3d.modeler.create_coordinate_system(origin=[0 ,0 ,12.7],reference_cs="Global",name="RelativeCS1",mode="axis",x_pointing=[1 ,0 ,0],y_pointing=[0 ,1 ,0])

# #### Apply rotation on relative coordinate system

m3d.modeler.rotate(assignment=[inner_arm], axis="RelativeCS1" , angle="angle")

# #### Create coils

coil1 = m3d.modeler.create_rectangle(orientation=ansys.aedt.core.constants.AXIS.X,origin=[0,0,15.5],sizes=[17,24], name="coil1", material="copper")
coil1.color="(249 186 70)"
path_rectangle = m3d.modeler.create_rectangle(orientation=ansys.aedt.core.constants.AXIS.Y,origin=[-17,0,-15.5],sizes=[31,34], name="path")
m3d.modeler.uncover_faces([path_rectangle.faces[0]])
m3d.modeler.sweep_along_path(assignment=coil1, sweep_object=path_rectangle)
round = m3d.modeler.create_cylinder(orientation=ansys.aedt.core.constants.AXIS.Y ,origin=[0,0,0],radius=46.238512086788,height=17,num_sides=0, name="Round")
m3d.modeler.intersect(assignment=[coil1, round])
m3d.modeler.move(assignment=coil1,vector=[0,54.5,0])
m3d.modeler.duplicate_and_mirror(assignment=coil1,origin=[0,0,0],vector=[0,1,0])
m3d.modeler.section(assignment=coil1,plane='XY')
m3d.modeler.section(assignment=coil1.name + "_1",plane='XY')

# #### Create air region

bgnd = m3d.modeler.create_box(origin=[-250 ,-250 ,-250],sizes=[500,500,500], name="bgnd")
bgnd.transparency = 1

# #### Create Coil Terminals by Separating Sheet bodies

coil_terminal1 = coil1.name + "_1_Section1_Separate1"
coil_terminal2 = coil1.name + "_Section1"
m3d.modeler.separate_bodies(assignment=coil_terminal2)
m3d.modeler.delete(assignment=coil1.name + "_Section1_Separate1")
m3d.modeler.separate_bodies(assignment=coil1.name + "_1_Section1")
m3d.modeler.delete(assignment=coil1.name + "_1_Section1")

m3d.modeler.fit_all()

# ### Assign boundary conditions

m3d.assign_current(assignment=coil_terminal1, amplitude=675.5, solid=False, name="Current_1")
m3d.assign_current(assignment=coil_terminal2, amplitude=675.5, solid=False, name="Current_2")

# ### Define solution setup

m3d.assign_matrix(assignment=["Current_1", "Current_2"],matrix_name="Matrix1")
m3d.assign_torque(assignment=inner_arm.name, is_virtual=True, coordinate_system="Global", axis="Z", torque_name="Virtual_Torque")

setup = m3d.create_setup("MySetup")
print(setup.props)
setup.props["MaximumPasses"] = 10
setup.props["PercentRefinement"] = 30
setup.props["PercentError"] = 1
setup.props["MinimumPasses"] = 2
setup.props["RelativeResidual"] = 1e-3

parametric_sweep = m3d.parametrics.add(variable="angle",start_point="0", end_point="30", step="5",
                                       variation_type="LinearStep",name="ParametricSetup1")
parametric_sweep.add_calculation(calculation="Virtual_Torque.Torque")
parametric_sweep.add_calculation(calculation="Matrix1.L(Current_1, Current_1)")
parametric_sweep.add_calculation(calculation="Matrix1.L(Current_1, Current_2)")
parametric_sweep.add_calculation(calculation="Matrix1.L(Current_2, Current_1)")
parametric_sweep.add_calculation(calculation="Matrix1.L(Current_2, Current_2)")
parametric_sweep.props["ProdOptiSetupDataV2"]["SaveFields"] = True

#
# ### Run analysis
#

parametric_sweep.analyze(cores=NUM_CORES)

# ## Postprocess
#
# ### Create a Rectangular plot of Coil Inductance vs. Rotational Angle

m3d.post.create_report(
    expressions=["Matrix1.L(Current_1, Current_1)",
                 "Matrix1.L(Current_1, Current_2)"],
    variations={"angle": "All"},
    plot_name="Coil Inductance vs. Angle",
    primary_sweep_variable="angle",
    plot_type="Rectangular Plot",
)

# ### Create field plots on the surface of the actuator's arms

m3d.post.create_fieldplot_surface(
    assignment=[inner_arm, outer_arm], quantity="Mag_B", plot_name="Mag_B1", field_type="Fields")

m3d.post.create_fieldplot_surface(
    assignment=[inner_arm, outer_arm], quantity="B_Vector", plot_name="B_Vector1", field_type="Fields")#


# ## Finish
#
# ### Save the project

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
