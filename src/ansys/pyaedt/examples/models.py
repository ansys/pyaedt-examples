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
"""Models used to store data related to writing PyAEDT examples.
"""
from typing import Union

from ansys.pyaedt.examples.constants import EDB_APP_SETUP, EDB_IMPORTS, EDB_TMP_DIR, EDB_VERSION
from pydantic import BaseModel, field_validator


class CodeCell(BaseModel):
    """Notebook code cell"""

    code: str

    def __init__(self, code: str = None, **data):
        code_value = code if code is not None else data.get("code")
        super().__init__(code=code_value)

    @field_validator("code")
    def multiple_blocs(cls, v):
        if v.startswith("# +") and not v.endswith("# -"):
            raise ValueError("multiple blocks must begin with '# +' and end with '# -'")
        return v


class TextCell(BaseModel):
    """Notebook text cell"""

    text: str

    def __init__(self, text: str = None, **data):
        text_value = text if text is not None else data.get("text")
        super().__init__(text=text_value)

    @field_validator("text")
    def must_start_with_hash(cls, v):
        lines = v.split("\n")
        for line in lines:
            if line == "#":
                continue
            if not line.startswith("# "):
                raise ValueError("each line of a text cell must be '#' or start with '# '")
        return v


class Header(BaseModel):
    """Notebook text cell"""

    text: str

    def __init__(self, text: Optional[str] = None, **data):
        text_value = text if text is not None else data.get("text", None)
        super().__init__(text=text_value)

    @field_validator("text")
    def must_start_with_hash_if_not_none(cls, v):
        if v is not None:
            lines = v.split("\n")
            for line in lines:
                if line == "#":
                    continue
                if not line.startswith("# "):
                    raise ValueError("each line of a text cell must be '#' or start with '# '")
        return v


class EDBModel(BaseModel):
    """Store AEDT properties."""

    header_required: bool = False
    header: Union[TextCell, str] = ""
    example_title: str = "Simple workflow using EDB"
    example_preamble: TextCell = TextCell("# This example contains multiple steps...")
    step_imports: CodeCell = CodeCell(EDB_IMPORTS)
    step_temp_dir: CodeCell = CodeCell(EDB_TMP_DIR)
    download_required: bool = False
    step_download: CodeCell = CodeCell("")
    edb_version: str = EDB_VERSION
    step_app_setup: CodeCell = CodeCell(EDB_APP_SETUP)
    step_processing: str = ""


if __name__ == "__main__":
    model = EDBModel()
