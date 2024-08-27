# # Create and export motor
#
# This example uses PyAEDT to create a RMxprt project and export to Maxwell 2D.
# It shows how to create an ASSM (Adjust-Speed Syncronous Machine) in RMxprt
# and how to access rotor and stator settings.
# The model is then exported in a Maxwell 2d design
# and the RMxprt settings are exported in a json file to be reused.
#
# Keywords: **RMxprt**, **Maxwell2D**

# ## Perform required imports
#
# Perform required imports.

import os
import tempfile
import time

import ansys.aedt.core

# ## Define constants
#
# Define constants.

AEDT_VERSION = "2024.2"

# ## Create temporary directory and download files
#
# Create a temporary directory where we store downloaded data or
# dumped data.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT and Rmxprt
#
# Launch AEDT and Rmxprt after first setting up the project name.
# As a solution type the example uses an ASSM (Adjust-Speed Syncronous Machine).

project_name = os.path.join(temp_folder.name, "ASSM.aedt")
app = ansys.aedt.core.Rmxprt(
    version=AEDT_VERSION,
    new_desktop=True,
    close_on_exit=True,
    solution_type="ASSM",
    project=project_name
)

# ## Define Machine settings
#
# Define global machine settings.

app.general["Number of Poles"] = 4
app.general["Rotor Position"] = "Inner Rotor"
app.general["Frictional Loss"] = "12W"
app.general["Windage Loss"] = "0W"
app.general["Reference Speed"] = "1500rpm"
app.general["Control Type"] = "DC"
app.general["Circuit Type"] = "Y3"

# ## Define circuit settings
#
# Define circuit settings.

app.circuit["Trigger Pulse Width"] = "120deg"
app.circuit["Transistor Drop"] = "2V"
app.circuit["Diode Drop"] = "2V"

# ## Stator
#
# Define stator, slot and windings settings.

app.stator["Outer Diameter"] = "122mm"
app.stator["Inner Diameter"] = "75mm"
app.stator["Length"] = "65mm"
app.stator["Stacking Factor"] = 0.95
app.stator["Steel Type"] = "steel_1008"
app.stator["Number of Slots"] = 24
app.stator["Slot Type"] = 2

app.stator.properties.children["Slot"].props["Auto Design"] = False
app.stator.properties.children["Slot"].props["Hs0"] = "0.5mm"
app.stator.properties.children["Slot"].props["Hs1"] = "1.2mm"
app.stator.properties.children["Slot"].props["Hs2"] = "8.2mm"
app.stator.properties.children["Slot"].props["Bs0"] = "2.5mm"
app.stator.properties.children["Slot"].props["Bs1"] = "5.6mm"
app.stator.properties.children["Slot"].props["Bs2"] = "7.6mm"

app.stator.properties.children["Winding"].props["Winding Layers"] = 2
app.stator.properties.children["Winding"].props["Parallel Branches"] = 1
app.stator.properties.children["Winding"].props["Conductors per Slot"] = 52
app.stator.properties.children["Winding"].props["Coil Pitch"] = 5
app.stator.properties.children["Winding"].props["Number of Strands"] = 1

# ## Rotor
#
# Define rotor and pole settings.

app.rotor["Outer Diameter"] = "74mm"
app.rotor["Inner Diameter"] = "26mm"
app.rotor["Length"] = "65mm"
app.rotor["Stacking Factor"] = 0.95
app.rotor["Steel Type"] = "steel_1008"
app.rotor["Pole Type"] = 1

app.rotor.properties.children["Pole"].props["Embrace"] = 0.7
app.rotor.properties.children["Pole"].props["Offset"] = "0mm"
app.rotor.properties.children["Pole"].props["Magnet Type"] = ["Material:=", "Alnico9"]
app.rotor.properties.children["Pole"].props["Magnet Thickness"] = "3.5mm"

# ## Setup
#
# Create a setup and define main settings.

setup = app.create_setup()
setup.props["RatedVoltage"] = "220V"
setup.props["RatedOutputPower"] = "550W"
setup.props["RatedSpeed"] = "1500rpm"
setup.props["OperatingTemperature"] = "75cel"

# ## Analyze setup
#
# Analyze setup.

setup.analyze()

# ## Export to Maxwell
#
# After the project is solved, it can be exported either to Maxwell 2D or Maxwell 3D.

m2d = app.create_maxwell_design(setup_name=setup.name, maxwell_2d=True)
m2d.plot(show=False, output_file=os.path.join(temp_folder.name, "Image.jpg"), plot_air_objects=True)

# ## RMxprt settings export
#
# All RMxprt settings can be exported in a json file and reused for another
# project with import function.

config = app.export_configuration(os.path.join(temp_folder.name, "assm.json"))
app2 = ansys.aedt.core.Rmxprt(project="assm_test2",solution_type=app.solution_type, design="from_configuration")
app2.import_configuration(config)

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
