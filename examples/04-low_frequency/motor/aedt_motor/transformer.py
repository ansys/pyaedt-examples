# # Transformer

# This example shows how to use PyAEDT to set core loss given a set
# of power-volume [kw/m^3] curves at different frequencies.
#
# Keywords: **Maxwell 3D**, **Transformer**.

# ## Perform imports and define constants
#
# Perform required imports.

import os
import tempfile
import time

from ansys.aedt.core import Maxwell3d, downloads
from ansys.aedt.core.generic.constants import unit_converter
from ansys.aedt.core.generic.general_methods import read_csv_pandas

# Define constants.

AEDT_VERSION = "2024.2"
NG_MODE = False

# ## Create temporary directory
#
# Create a temporary directory where downloaded data or
# dumped data can be stored.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Download AEDT file example
#
# Download the files required to run this example to the temporary working folder.

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
# the project and design names, the version, and the graphical mode.

m3d = Maxwell3d(
    project=aedt_file,
    design="02_3D eddycurrent_CmXY_for_thermal",
    version=AEDT_VERSION,
    new_desktop=True,
    non_graphical=False,
)

# ## Set core loss at frequencies
#
# Create a new material, create a dictionary of power-volume [kw/m^3] points
# for a set of frequencies retrieved from datasheet provided by a supplier,
# and finally set the Power-Ferrite core loss model.

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

# ## Plot model

model = m3d.plot(show=False)
model.plot(os.path.join(temp_folder.name, "Image.jpg"))


# ## Release AEDT

m3d.save_project()
m3d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
