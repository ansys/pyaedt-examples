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
"""Utilities module.
"""

import requests


def download_file(url, local_filename):
    """Download a file from an URL into a local file."""
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=4096):
                f.write(chunk)
    return local_filename


import os

from jinja2 import Environment, FileSystemLoader

# Charger le template Jinja
file_loader = FileSystemLoader(os.path.dirname(os.path.abspath(__file__)))
env = Environment(loader=file_loader)
template = env.get_template("template.j2")

# Données pour le template
data = {
    "imports": "import os\nimport sys",
    "functions": [
        {"name": "my_function", "description": "Cette function fait quelque chose."},
    ],
    "environment_setup": "Création d'un répertoire temporaire...",
    "app_setup": "Configuration de l'application...",
    "processing": "Traitement des données...",
    "cleanup": "Nettoyage et suppression du répertoire temporaire...",
}

# Générer le fichier Markdown
output = template.render(**data)
with open("example.md", "w") as f:
    f.write(output)
# Données pour le template
data = {
    "imports": "import os\nimport sys",
    "functions": [
        {"name": "my_function", "description": "Cette function fait quelque chose."},
    ],
    "environment_setup": "Création d'un répertoire temporaire...",
    "download_required": True,  # ou False, en function de vos besoins
    "download_step": "Téléchargement des fichiers nécessaires...",
    "app_setup": "Configuration de l'application...",
    "processing": "Traitement des données...",
    "cleanup": "Nettoyage et suppression du répertoire temporaire...",
}
