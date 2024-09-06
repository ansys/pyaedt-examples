# # Fields export in transient
#
# This example shows how to leverage PyAEDT to set up a Maxwell 3D transient analysis,
# compute the average value of the current density field over a specific coil surface
# and the magnitude of the current density field over all coil surfaces at each time step
# of the transient analysis.
#
# Keywords: **Maxwell 3D**, **transient**, **fields calculator**, **field export**.

# ## Perform required imports
#
# Perform required imports.

import os
import tempfile
import time

import ansys.aedt.core

# ## Define constants

AEDT_VERSION = "2024.2"
NUM_CORES = 4
NG_MODE = False  # Open Electronics UI when the application is launched.

# ## Create temporary directory and download files
#
# Create a temporary directory where we store downloaded data or
# dumped data.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Import project
#
# The files required to run this example will be downloaded into the temporary working folder.

project_path = ansys.aedt.core.downloads.download_file(
    source="maxwell_transient_fields",
    name="M3D_Transient_StrandedWindings.aedt",
    destination=temp_folder.name,
)

# ## Initialize and launch Maxwell 3D
#
# Initialize and launch Maxwell 3D, providing the version and the path of the project.

m3d = ansys.aedt.core.Maxwell3d(
    project=project_path, version=AEDT_VERSION, non_graphical=NG_MODE
)

# ## Create setup and validate
#
# Create the setup specifying general settings such as ``StopTime`` and ``TimeStep``
# and the save fields type.

setup = m3d.create_setup(name="Setup1")
setup.props["StopTime"] = "0.02s"
setup.props["TimeStep"] = "0.002s"
setup.props["SaveFieldsType"] = "Every N Steps"
setup.props["N Steps"] = "2"
setup.props["Steps From"] = "0s"
setup.props["Steps To"] = "0.02s"
setup.update()

# ## Plot model

model = m3d.plot(show=False)
model.plot(os.path.join(temp_folder.name, "Image.jpg"))

# ## Create field expressions
#
# Create a field expression to evaluate J normal to a surface using the advanced fields calculator.
# The expression is created as a dictionary and then provided as an argument to ``add_expression``.

my_expression = {
    "name": "Jn",
    "description": "J field normal to a surface",
    "design_type": ["Maxwell 3D"],
    "fields_type": ["Fields"],
    "primary_sweep": "Time",
    "assignment": "",
    "assignment_type": [""],
    "operations": [
        "NameOfExpression('<Jx,Jy,Jz>')",
        "Operation('Normal')",
        "Operation('Dot')",
    ],
    "report": ["Field_3D"],
}
m3d.post.fields_calculator.add_expression(my_expression, None)

# Calculate the average value of J normal using the advanced fields calculator.

my_expression = {
    "name": "Jn_avg",
    "description": "Average J field normal to a surface",
    "design_type": ["Maxwell 3D"],
    "fields_type": ["Fields"],
    "primary_sweep": "Time",
    "assignment": "Coil_A2_ObjectFromFace1",
    "assignment_type": [""],
    "operations": [
        "NameOfExpression('Jn')",
        "EnterSurface('assignment')",
        "Operation('SurfaceValue')",
        "Operation('Mean')",
    ],
    "report": ["Field_3D"],
}
m3d.post.fields_calculator.add_expression(my_expression, None)

# ## Analyze setup specifying setup name.

m3d.analyze_setup(name=setup.name, cores=NUM_CORES)

# ## Get the available report quantities
#
# Get available report quantities given a specific report category.
# In this case ``Calculator Expressions`` is the category.

report_types = m3d.post.available_report_types
quantity = m3d.post.available_report_quantities(
    report_category="Fields", quantities_category="Calculator Expressions"
)

# ## Compute the time steps of the analysis
#
# Create a fields report object given the nominal sweep.
# Get the report solution data in order to compute the time steps of the transient analysis.

sol = m3d.post.reports_by_category.fields(setup=m3d.nominal_sweep)
data = sol.get_solution_data()
time_steps = data.intrinsics["Time"]

# ## Create field plots over the coil surfaces and export field data
#
# Convert each time step into ``ms``.
# Create field plots over the surface of each coil by specifying the coil object,
# the quantity to plot and the time step.
# The average value of J normal is plotted on Coil_A2 surface for every time-step.
# The J field is plotted on the surface of each coil for every time-step.
# Export fields data in temporary directory as an ``.aedtplt``.

for time_step in time_steps:
    t = ansys.aedt.core.generic.constants.unit_converter(
        time_step,
        unit_system="Time",
        input_units=data.units_sweeps["Time"],
        output_units="ms",
    )
    m3d.post.create_fieldplot_surface(
        assignment=m3d.modeler.objects_by_name["Coil_A2"],
        quantity=quantity[0],
        plot_name="J_{}_ms".format(t),
        intrinsics={"Time": "{}ms".format(t)},
    )
    mean_j_field_export = m3d.post.export_field_plot(
        plot_name="J_{}_ms".format(t),
        output_dir=temp_folder.name,
        file_format="aedtplt",
    )
    m3d.post.create_fieldplot_surface(
        assignment=[
            o for o in m3d.modeler.solid_objects if o.material_name == "copper"
        ],
        quantity="Mag_J",
        plot_name="Mag_J_Coils_{}_ms".format(t),
        intrinsics={"Time": "{}ms".format(t)},
    )
    mag_j_field_export = m3d.post.export_field_plot(
        plot_name="Mag_J_Coils_{}_ms".format(t),
        output_dir=temp_folder.name,
        file_format="aedtplt",
    )


# ## Release AEDT

m3d.save_project()
m3d.release_desktop()
# Wait 3 seconds to allow Electronics Desktop to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Cleanup
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
