# # Maxwell 3D: Transformer

# This example shows how you can use PyAEDT to set core loss given a set
# of Power-Volume [kw/m^3] curves at different frequencies.

# ## Perform required imports
#
# Perform required imports.

import tempfile
import time

from pyaedt import Maxwell3d, downloads
from pyaedt.generic.constants import unit_converter
from pyaedt.generic.general_methods import read_csv_pandas

# ## Define constants

AEDT_VERSION = "2024.1"
NG_MODE = False

# ## Create temporary directory
#
# The temporary directory is used to run the example and save simulation data. If you run
# this example as a Jupyter Notebook you can recover the project data and results by copying
# the contents of the temporary folder to a local drive prior to executing the final cell of this
# notebook.
# The temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download .aedt file example
#
# The files required to run this example will be downloaded to the temporary working folder.

# +
aedt_file = downloads.download_file(
    source="core_loss_transformer",
    name="Ex2-PlanarTransformer_2023R2.aedtz",
    destination=temp_folder.name,
)
freq_curve_csv_25kHz = downloads.download_file(
    source="core_loss_transformer", name="mf3_25kHz.csv", destination=temp_folder.name
)
freq_curve_csv_100kHz = downloads.download_file(
    source="core_loss_transformer", name="mf3_100kHz.csv", destination=temp_folder.name
)
freq_curve_csv_200kHz = downloads.download_file(
    source="core_loss_transformer", name="mf3_200kHz.csv", destination=temp_folder.name
)
freq_curve_csv_400kHz = downloads.download_file(
    source="core_loss_transformer", name="mf3_400kHz.csv", destination=temp_folder.name
)
freq_curve_csv_700kHz = downloads.download_file(
    source="core_loss_transformer", name="mf3_700kHz.csv", destination=temp_folder.name
)
freq_curve_csv_1MHz = downloads.download_file(
    source="core_loss_transformer", name="mf3_1MHz.csv", destination=temp_folder.name
)

data = read_csv_pandas(input_file=freq_curve_csv_25kHz)
curves_csv_25kHz = list(zip(data[data.columns[0]], data[data.columns[1]]))
data = read_csv_pandas(input_file=freq_curve_csv_100kHz)
curves_csv_100kHz = list(zip(data[data.columns[0]], data[data.columns[1]]))
data = read_csv_pandas(input_file=freq_curve_csv_200kHz)
curves_csv_200kHz = list(zip(data[data.columns[0]], data[data.columns[1]]))
data = read_csv_pandas(input_file=freq_curve_csv_400kHz)
curves_csv_400kHz = list(zip(data[data.columns[0]], data[data.columns[1]]))
data = read_csv_pandas(input_file=freq_curve_csv_700kHz)
curves_csv_700kHz = list(zip(data[data.columns[0]], data[data.columns[1]]))
data = read_csv_pandas(input_file=freq_curve_csv_1MHz)
curves_csv_1MHz = list(zip(data[data.columns[0]], data[data.columns[1]]))
# -

# ## Launch AEDT and Maxwell 3D
#
# Create an instance of the ``Maxwell3d`` class named ``m3d`` by providing
# the project and design names, the version and the graphical mode.

m3d = Maxwell3d(
    project=aedt_file,
    design="02_3D eddycurrent_CmXY_for_thermal",
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=False,
)

# ## Set core loss at frequencies
#
# Create a new material, create a dictionary of Power-Volume [kw/m^3] points
# for a set of frequencies
# retrieved from datasheet provided by supplier and finally set Power-Ferrite core loss model.

mat = m3d.materials.add_material("newmat")
freq_25kHz = unit_converter(
    values=25, unit_system="Freq", input_units="kHz", output_units="Hz"
)
freq_100kHz = unit_converter(
    values=100, unit_system="Freq", input_units="kHz", output_units="Hz"
)
freq_200kHz = unit_converter(
    values=200, unit_system="Freq", input_units="kHz", output_units="Hz"
)
freq_400kHz = unit_converter(
    values=400, unit_system="Freq", input_units="kHz", output_units="Hz"
)
freq_700kHz = unit_converter(
    values=700, unit_system="Freq", input_units="kHz", output_units="Hz"
)
pv = {
    freq_25kHz: curves_csv_25kHz,
    freq_100kHz: curves_csv_100kHz,
    freq_200kHz: curves_csv_200kHz,
    freq_400kHz: curves_csv_400kHz,
    freq_700kHz: curves_csv_700kHz,
}
m3d.materials[mat.name].set_coreloss_at_frequency(
    points_at_frequency=pv,
    coefficient_setup="kw_per_cubic_meter",
    core_loss_model_type="Power Ferrite",
)
coefficients = m3d.materials[mat.name].get_core_loss_coefficients(
    points_at_frequency=pv, coefficient_setup="kw_per_cubic_meter"
)

# ## Release AEDT and clean up temporary directory
#
# Release AEDT and remove both the project and temporary directory.

m3d.release_desktop()
time.sleep(3)
temp_folder.cleanup()
