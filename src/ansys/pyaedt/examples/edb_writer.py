# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Utils to write an EDB example.

If used as a python script, this file will generate a simple example.
"""

import os

from ansys.pyaedt.examples.constants import (
    EDB_APP_SETUP,
    EDB_IMPORTS,
    EDB_PREAMBLE,
    EDB_PROCESSING,
    EDB_TMP_DIR,
    EDB_VERSION,
    HEADER,
)
from ansys.pyaedt.examples.models import CodeCell, EDBModel, TextCell
from jinja2 import Environment, FileSystemLoader

PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
EXAMPLE_TITLE = "Simple workflow using EDB"


def write_example(example_path, data: EDBModel):
    """Write a new example using a template and user information."""

    file_loader = FileSystemLoader(os.path.join(PARENT_DIR, "templates"))
    env = Environment(loader=file_loader)
    template = env.get_template("template_edb.j2")

    output = template.render(data.model_dump())
    with open(example_path, "w") as f:
        f.write(output)


if __name__ == "__main__":

    # Data of a simple edb example
    data = {
        "header_required": False,
        "header": HEADER,
        "example_title": EXAMPLE_TITLE,
        "example_preamble": TextCell(EDB_PREAMBLE),
        "step_imports": CodeCell(EDB_IMPORTS),
        "step_temp_dir": CodeCell(EDB_TMP_DIR),
        "download_required": False,
        "step_download": CodeCell(""),
        "edb_version": EDB_VERSION,
        "step_app_setup": CodeCell(EDB_APP_SETUP),
        "step_processing": EDB_PROCESSING,
    }
    model_data = EDBModel(**data)

    example_path = os.path.join(PARENT_DIR, "simple_example.py")
    write_example(example_path, data=model_data)
