# # Maxwell 3D: fields export in transient
# Description here!
# Keywords: time steps, field calculator

# ## Perform required imports
#
# Perform required imports.

import tempfile

import pyaedt
from pyaedt.generic.constants import unit_converter

# ## Define constants

AEDT_VERSION = "2024.1"
NG_MODE = False

# ## Create temporary directory and download files
#
# Create a temporary directory where we store downloaded data or
# dumped data.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Import project
#
# The files required to run this example will be downloaded to the temporary working folder.

project_path = pyaedt.downloads.download_file(
    source="maxwell_transient_fields",
    name="M3D_Transient_StrandedWindings.aedt",
    destination=temp_folder.name,
)

# ## Initialize and launch Maxwell 2D
#
# Initialize and launch Maxwell 2D, providing the version, path to the project, the design
# name and type.

m3d = pyaedt.Maxwell3d(
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

# ## Create field expressions
#
# Create a field expression to evaluate J field normal to a surface.

fields = m3d.ofieldsreporter
fields.CalcStack("clear")
fields.EnterQty("J")
# fields.EnterSurf("Coil_A2")
fields.CalcOp("Normal")
fields.CalcOp("Dot")
fields.AddNamedExpression("Jn", "Fields")

# Calculate the average value of the J field

fields.CopyNamedExprToStack("Jn")
fields.EnterSurf("Coil_A2")
fields.CalcOp("Mean")
fields.AddNamedExpression("J_avg", "Fields")

# ## Analyze setup specifying setup name.

m3d.analyze_setup(name=setup.name)

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

# ## Create a field plot over the coil surface and export field data
#
# Convert each time step into ``ms``.
# Create a field plot on the coil surface by specifying the coil object,
# the quantity to plot and the time step.
# Export fields data in temporary directory as an ``.aedtplt``.

for time_step in time_steps:
    t = unit_converter(
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
    field_export = m3d.post.export_field_plot(
        plot_name="J_{}_ms".format(t),
        output_dir=temp_folder.name,
        file_format="aedtplt",
    )

# ## Release AEDT and clean up temporary directory
#
# Release AEDT and remove both the project and temporary directory.

m3d.release_desktop()
temp_folder.cleanup()
