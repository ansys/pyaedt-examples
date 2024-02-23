import os

from ansys.pyaedt.examples.constants import (
    EDB_APP_SETUP,
    EDB_IMPORTS,
    EDB_TMP_DIR,
    EDB_VERSION,
    HEADER,
)
from ansys.pyaedt.examples.edb_writer import EXAMPLE_TITLE, write_example
from ansys.pyaedt.examples.models import CodeCell, EDBModel, TextCell

EXAMPLE_PREAMBLE = "# Here is a simple workflow without processings"
EXPECTED_RESULT = f"""# ## {EXAMPLE_TITLE}
#
{EXAMPLE_PREAMBLE}

# ## Perform required imports and create a temporary folder.
#
# Perform imports required to run the example and create a temporary folder in which to save files.
{EDB_IMPORTS}

{EDB_TMP_DIR}

# ## Create an instance of the Electronics Database using the `pyaedt.Edb` class.
#
# > Note that units are SI.

# Select EDB version (change it manually if needed, e.g. "2023.2")
edb_version = {EDB_VERSION}
print(f"EDB version: {{edb_version}}")

{EDB_APP_SETUP}



# ## Save and clean up
#
# The following commands save and close the EDB. After that, the temporary
# directory containing the project is deleted. To keep this project, save it to
# another folder of your choice prior to running the following cell.

# +
edb.save_edb()
edb.close_edb()
print("EDB saved correctly to {{}}. You can import in AEDT.".format(aedb_path))

# Removing the temporary directory
temp_dir.cleanup()
# -"""


def test_edb_writer(common_temp_dir):
    """"""
    example_path = os.path.join(common_temp_dir, "dummy_example.py")
    data = {
        "header_required": False,
        "header": HEADER,
        "example_title": "Simple workflow using EDB",
        "example_preamble": TextCell(EXAMPLE_PREAMBLE),
        "step_imports": CodeCell(EDB_IMPORTS),
        "step_temp_dir": CodeCell(EDB_TMP_DIR),
        "download_required": False,
        "step_download": CodeCell(""),
        "edb_version": EDB_VERSION,
        "step_app_setup": CodeCell(EDB_APP_SETUP),
        "step_processing": "",
    }

    model_data = EDBModel(**data)
    write_example(example_path, model_data)

    with open(example_path, "r") as file:
        example_content = file.read()

    assert EXPECTED_RESULT == example_content
