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

from ansys.pyaedt.examples.constants import (
    EDB_APP_SETUP,
    EDB_IMPORTS,
    EDB_PREAMBLE,
    EDB_PROCESSING,
    EDB_TMP_DIR,
    EDB_VERSION,
    HEADER,
)
from ansys.pyaedt.examples.models import CodeCell, EDBModel, Header, TextCell
from pydantic import ValidationError
import pytest

CORRECT_INPUT = {
    "header_required": False,
    "header": Header(HEADER),
    "example_title": "Simple workflow using EDB",
    "example_preamble": TextCell(text=EDB_PREAMBLE),
    "step_imports": CodeCell(code=EDB_IMPORTS),
    "step_temp_dir": CodeCell(code=EDB_TMP_DIR),
    "download_required": False,
    "step_download": CodeCell(""),
    "edb_version": EDB_VERSION,
    "step_app_setup": CodeCell(code=EDB_APP_SETUP),
    "step_processing": EDB_PROCESSING,
}


def test_text_cell_validation_failure():
    """Test invalid text cell input."""
    input = """# Something
    is wrong
    # with what you do !"""

    with pytest.raises(ValidationError):
        TextCell(input)


def test_code_cell_validation_failure():
    """Test invalid code cell input."""
    input = """# +
    import os"""

    with pytest.raises(ValidationError):
        CodeCell(input)


def test_edb_model_success():
    """Test EDBModel with valid input."""
    input = CORRECT_INPUT.copy()

    EDBModel(**input)


def test_edb_model_with_invalid_code_cell():
    """Test EDBModel failure when used with invalid code cell."""
    input = CORRECT_INPUT.copy()
    input[
        "step_imports"
    ] = """# +
    import os"""

    with pytest.raises(ValidationError):
        EDBModel(**input)


def test_edb_model_with_invalid_text_cell():
    """Test EDBModel failure when used with invalid text cell."""
    input = CORRECT_INPUT.copy()
    input[
        "example_preamble"
    ] = """# Something
    is wrong
    # with what you do !"""

    with pytest.raises(ValidationError):
        EDBModel(**input)
