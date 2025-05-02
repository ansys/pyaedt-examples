# # Motor creation and export
#
# This example uses PyAEDT to create a RMxprt project and export it to Maxwell 2D.
# It shows how to create an ASSM (Adjust-Speed Synchronous Machine) in RMxprt
# and how to access rotor and stator settings.
# It then exports the model to a Maxwell 2D design
# and the RMxprt settings to a JSON file to be reused.
#
# Keywords: **RMxprt**, **Maxwell 2D**

# ## Perform imports and define constants
#
# Perform required imports.

# +
import os
import tempfile
import time

import ansys.aedt.core
# -

# Define constants.

AEDT_VERSION = "2025.1"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT and RMxprt
#
# Launch AEDT and RMxprt after first setting up the project name.
# This example uses ASSM (Adjust-Speed Synchronous Machine) as the solution type.

project_name = os.path.join(temp_folder.name, "ASSM.aedt")
rmxprt = ansys.aedt.core.Rmxprt(
    version=AEDT_VERSION,
    new_desktop=True,
    close_on_exit=True,
    solution_type="ASSM",
    project=project_name,
    non_graphical=NG_MODE,
)

# ## Define global machine settings

rmxprt.general["Number of Poles"] = 4
rmxprt.general["Rotor Position"] = "Inner Rotor"
rmxprt.general["Frictional Loss"] = "12W"
rmxprt.general["Windage Loss"] = "0W"
rmxprt.general["Reference Speed"] = "1500rpm"
rmxprt.general["Control Type"] = "DC"
rmxprt.general["Circuit Type"] = "Y3"

# ## Define circuit settings

rmxprt.circuit["Trigger Pulse Width"] = "120deg"
rmxprt.circuit["Transistor Drop"] = "2V"
rmxprt.circuit["Diode Drop"] = "2V"

# ## Define stator
#
# Define stator and slot and winding settings.

rmxprt.stator["Outer Diameter"] = "122mm"
rmxprt.stator["Inner Diameter"] = "75mm"
rmxprt.stator["Length"] = "65mm"
rmxprt.stator["Stacking Factor"] = 0.95
rmxprt.stator.properties.properties["Steel Type"] = [
    "Material:=",
    "steel_1008",
]
rmxprt.stator["Number of Slots"] = 24
rmxprt.stator["Slot Type"] = 2

rmxprt.stator.properties.children["Slot"].properties["Auto Design"] = False
rmxprt.stator.properties.children["Slot"].properties["Hs0"] = "0.5mm"
rmxprt.stator.properties.children["Slot"].properties["Hs1"] = "1.2mm"
rmxprt.stator.properties.children["Slot"].properties["Hs2"] = "8.2mm"
rmxprt.stator.properties.children["Slot"].properties["Bs0"] = "2.5mm"
rmxprt.stator.properties.children["Slot"].properties["Bs1"] = "5.6mm"
rmxprt.stator.properties.children["Slot"].properties["Bs2"] = "7.6mm"

rmxprt.stator.properties.children["Winding"].properties["Winding Layers"] = 2
rmxprt.stator.properties.children["Winding"].properties["Parallel Branches"] = 1
rmxprt.stator.properties.children["Winding"].properties["Conductors per Slot"] = 52
rmxprt.stator.properties.children["Winding"].properties["Coil Pitch"] = 5
rmxprt.stator.properties.children["Winding"].properties["Number of Strands"] = 1

# ## Define rotor
#
# Define rotor and pole settings.

rmxprt.rotor["Outer Diameter"] = "74mm"
rmxprt.rotor["Inner Diameter"] = "26mm"
rmxprt.rotor["Length"] = "65mm"
rmxprt.rotor["Stacking Factor"] = 0.95
rmxprt.rotor["Steel Type"] = [
    "Material:=",
    "steel_1008",
]
rmxprt.rotor["Pole Type"] = 1

rmxprt.rotor.properties.children["Pole"].properties["Embrace"] = 0.7
rmxprt.rotor.properties.children["Pole"].properties["Offset"] = "0mm"
rmxprt.rotor.properties.children["Pole"].properties["Magnet Type"] = [
    "Material:=",
    "Alnico9",
]
rmxprt.rotor.properties.children["Pole"].properties["Magnet Thickness"] = "3.5mm"

# ## Create setup
#
# Create a setup and define the main settings.

setup = rmxprt.create_setup()
setup.props["RatedVoltage"] = "220V"
setup.props["RatedOutputPower"] = "550W"
setup.props["RatedSpeed"] = "1500rpm"
setup.props["OperatingTemperature"] = "75cel"

# ## Analyze setup.

setup.analyze(cores=NUM_CORES)

# ## Export to Maxwell
#
# After the project is solved, you can export it to either Maxwell 2D or Maxwell 3D.

m2d = rmxprt.create_maxwell_design(setup_name=setup.name, maxwell_2d=True)
m2d.plot(
    show=False,
    output_file=os.path.join(temp_folder.name, "Image.jpg"),
    plot_air_objects=True,
)

# ## Export RMxprt settings
#
# Export all RMxprt settings to a JSON file to reuse it for another
# project with the the import function.

config = rmxprt.export_configuration(os.path.join(temp_folder.name, "assm.json"))
rmxprt2 = ansys.aedt.core.Rmxprt(
    project="assm_test2",
    solution_type=rmxprt.solution_type,
    design="from_configuration",
)
rmxprt2.import_configuration(config)

# ## Save project
#
# Save the project containing the Maxwell design.

m2d.save_project(file_name=project_name)

# ## Release AEDT and clean up temporary directory
#
# Release AEDT and remove both the project and temporary directory.

m2d.release_desktop()
time.sleep(3)
temp_folder.cleanup()
