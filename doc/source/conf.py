# Configuration file for the Sphinx_PyAEDT documentation builder.

# -- Project information -----------------------------------------------------
import datetime
from importlib import import_module
import os
from pathlib import Path
from pprint import pformat
import re
import shutil
import traceback
from typing import Any
from sphinx.application import Sphinx
from sphinx.config import Config

from ansys_sphinx_theme import (
    ansys_favicon,
    ansys_logo_white,
    ansys_logo_white_cropped,
    latex,
    watermark,
)
from docutils import nodes
from docutils.parsers.rst import Directive
import numpy as np
import pyvista
from sphinx import addnodes
from sphinx.builders.latex import LaTeXBuilder
from sphinx.util import logging

os.environ["PYAEDT_NON_GRAPHICAL"] = "1"
os.environ["PYAEDT_DOC_GENERATION"] = "1"

LaTeXBuilder.supported_image_types = ["image/png", "image/pdf", "image/svg+xml"]

logger = logging.getLogger(__name__)
# NOTE: Uncomment to allow debug level logs
# logger.setLevel(logging.LEVEL_NAMES["DEBUG"])
path = Path(__file__).parent.parent.parent / "examples"
EXAMPLES_DIRECTORY = path.resolve()
REPOSITORY_NAME = "pyaedt-examples"
USERNAME = "ansys"
BRANCH = "main"
DOC_PATH = "doc/source"

project = "pyaedt-examples"
copyright = f"(c) 2021 - {datetime.datetime.now().year} ANSYS, Inc. All rights reserved"
author = "Ansys Inc."
cname = os.getenv("DOCUMENTATION_CNAME", "nocname.com")
release = version = "0.1.dev0"


# -- Connect functions (hooks) to Sphinx events  -----------------------------

class PrettyPrintDirective(Directive):
    """Renders a constant using ``pprint.pformat`` and inserts into the document."""

    required_arguments = 1

    def run(self):
        module_path, member_name = self.arguments[0].rsplit(".", 1)

        member_data = getattr(import_module(module_path), member_name)
        code = pformat(member_data, 2, width=68)

        literal = nodes.literal_block(code, code)
        literal["language"] = "python"

        return [addnodes.desc_name(text=member_name), addnodes.desc_content("", literal)]


# Sphinx generic event hooks


def directory_size(directory_path: Path):
    """Compute the size (in mega bytes) of a directory.
    
    Parameters
    ----------
    directory_path : pathlib.Path
        Path to the directory to evaluate.
    """
    res = 0
    for path, _, files in os.walk(directory_path):
        for f in files:
            fp = os.path.join(path, f)
            res += os.stat(fp).st_size
    # Convert in mega bytes
    res /= 1e6
    return res


def copy_examples_structure(app: Sphinx, config: Config):
    """Copy root directory examples structure into the doc/source/examples directory.

    Everything is copied except for python file. This is because we are manually
    converting them into notebook in another Sphinx hook and having both files in
    would raise a lot of sphinx warning while building the documentation.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx instance containing all the configuration for the documentation build.
    config : sphinx.config.Config
        Configuration file abstraction.
    """
    destination_dir = Path(app.srcdir, "examples").resolve()
    logger.info(f"Copying examples structures of {EXAMPLES_DIRECTORY} into {destination_dir}.")

    # NOTE: Only remove the examples directory if the workflow isn't tagged as coupling HTML and PDF build.
    if not bool(int(os.getenv("SPHINXBUILD_HTML_AND_PDF_WORKFLOW", "0"))):
        if os.path.exists(destination_dir):
            size = directory_size(destination_dir)
            logger.info(f"Directory {destination_dir} ({size} MB) already exist, removing it.")
            shutil.rmtree(destination_dir, ignore_errors=True)
            logger.info(f"Directory removed.")

    ignore_python_files = lambda _, files: [file for file in files if file.endswith(".py")]
    shutil.copytree(EXAMPLES_DIRECTORY, destination_dir, ignore=ignore_python_files, dirs_exist_ok=True)
    logger.info(f"Copy performed.")


def copy_script_examples(app: Sphinx, exception: None | Exception):
    """Copy root directory examples script into Sphinx application out directory.
    
    This is required to allow users to download python scripts in the admonition.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx instance containing all the configuration for the documentation build.
    exception : None or Exception
        Exception raised during the build process.
    """
    def extract_example_name(exception: Exception) -> str | None:
        """Extract the example file name from an exception if any."""
        exception_message = "".join(traceback.format_exception(exception))
        match = re.search(r"(examples[\\\/].*?\.ipynb):", exception_message)
        if match:
            return match.group(1).replace("\\", "/")

    if exception is not None:
        logger.warning("An error occurred during the build process, skipping the copy of script examples.")
        example_name = extract_example_name(exception)
        if example_name is not None:
            logger.warning(f"Error occurred in example {example_name}.")
        return

    destination_dir = Path(app.outdir, "examples").resolve()
    logger.info(f"Copying script examples into out directory {destination_dir}.")

    EXAMPLES = EXAMPLES_DIRECTORY.glob("**/*.py")
    for example in EXAMPLES:
        example_path = str(example).split("examples" + os.sep)[-1]
        out_example_path = destination_dir / example_path
        logger.debug(f"Example {example} is being copied into {out_example_path}.")

        if not out_example_path.parent.exists():
            out_example_path.parent.mkdir(parents=True)

        shutil.copyfile(example, out_example_path)

    logger.info(f"Copy performed.")


def adjust_image_path(app: Sphinx, docname, source):
    """Adjust the HTML label used to insert images in the examples.

    The following path makes the examples in the root directory work:
    # <img src="../../doc/source/_static/diff_via.png" width="500">
    However, examples fail when used through the documentation build because
    reaching the associated path should be "../../_static/diff_via.png".
    Indeed, the directory ``_static`` is automatically copied into the output directory
    ``_build/html/_static``.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx instance containing all the configuration for the documentation build.
    """
    # Get the full path to the document
    docpath = os.path.join(app.srcdir, docname)

    # Check if this is a PY example file
    if not os.path.exists(docpath + ".py") or not docname.startswith("examples"):
        return

    logger.info(f"Changing HTML image path in '{docname}.py' file.")
    source[0] = source[0].replace("../../doc/source/_static", "../../_static")


def check_pandoc_installed(app: Sphinx, config: Config):
    """Ensure that pandoc is installed
    
    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx instance containing all the configuration for the documentation build.
    config : sphinx.config.Config
        Configuration file abstraction.
    """
    import pypandoc

    try:
        pandoc_path = pypandoc.get_pandoc_path()
        pandoc_dir = os.path.dirname(pandoc_path)
        if pandoc_dir not in os.environ["PATH"].split(os.pathsep):
            logger.info("Pandoc directory is not in $PATH.")
            os.environ["PATH"] += os.pathsep + pandoc_dir
            logger.info(f"Pandoc directory '{pandoc_dir}' has been added to $PATH")
    except OSError:
        logger.error("Pandoc was not found, please add it to your path or install pypandoc-binary")


# NOTE: The list of skipped files requires to be updated every time a new example
# with GIF content is created or removed.
def skip_gif_examples_to_build_pdf(app: Sphinx):
    """Callback function for builder-inited event.

    Add examples showing GIF to the list of excluded files when building PDF files.

    Parameters
    ----------
    app :
        The application object representing the Sphinx process.
    """
    if app.builder.name == "latex":
        logger.info("Examples with animations are skipped when building with latex.")
        app.config.exclude_patterns.extend(
            [
                r".*Maxwell2D_Transient\.py",
                r".*Maxwell2D_DCConduction\.py",
                r".*Hfss_Icepak_Coupling\.py",
            ]
        )


def remove_examples(app: Sphinx, exception: None | Exception):
    """Remove the doc/source/examples directory created during documentation build.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx instance containing all the configuration for the documentation build.
    """
    # NOTE: Only remove the examples if the workflow isn't tagged as coupling HTML and PDF build.
    if not bool(int(os.getenv("SPHINXBUILD_HTML_AND_PDF_WORKFLOW", "0"))):
        destination_dir = Path(app.srcdir) / "examples"
        size = directory_size(destination_dir)
        logger.info(f"Removing directory {destination_dir} ({size} MB).")
        shutil.rmtree(destination_dir, ignore_errors=True)
        logger.info(f"Directory removed.")


def remove_doctree(app: Sphinx, exception: None | Exception):
    """Remove the .doctree directory created during the documentation build.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx instance containing all the configuration for the documentation build.
    exception : None or Exception
        Exception raised during the build process.
    """
    # NOTE: Only remove the doctree if the workflow isn't tagged as coupling HTML and PDF build.
    if not bool(int(os.getenv("SPHINXBUILD_HTML_AND_PDF_WORKFLOW", "0"))):
        size = directory_size(app.doctreedir)
        logger.info(f"Removing doctree {app.doctreedir} ({size} MB).")
        shutil.rmtree(app.doctreedir, ignore_errors=True)
        logger.info(f"Doctree removed.")


def convert_examples_into_notebooks(app):
    """Convert light style script into notebooks and disable execution if needed."""
    import subprocess
    import nbformat

    DESTINATION_DIR = Path(app.srcdir, "examples").resolve()
    EXAMPLES = EXAMPLES_DIRECTORY.glob("**/*.py")
    STATIC_EXAMPLES_TO_NOT_EXECUTE = (
        "template.py",
        "gui_manipulation.py",
        "electrothermal.py",
        # TODO: Remove the following example when 2025.1 is released, currently the latest version is 24.1.
        "lumped_element.py",
        # TODO: Remove once EMIT examples are moved into extensions.
        "interference_type.py",
        "interference.py",
        "hfss_emit.py",
        "component_conversion.py"
    )

    unchanged_raw = os.environ.get('ON_CI_UNCHANGED_EXAMPLES', '')
    if unchanged_raw:
        UNCHANGED_EXAMPLES = [f.strip() for f in unchanged_raw.split(",")]
    EXAMPLES_TO_NOT_EXECUTE = list(set(STATIC_EXAMPLES_TO_NOT_EXECUTE) | set(UNCHANGED_EXAMPLES))

    # NOTE: Only convert the examples if the workflow isn't tagged as coupling HTML and PDF build.
    if not bool(int(os.getenv("SPHINXBUILD_HTML_AND_PDF_WORKFLOW", "0"))) or app.builder.name == "html":
        count = 0
        for example in EXAMPLES:
            count += 1
            example_path = str(example).split("examples" + os.sep)[-1]
            notebook_path = example_path.replace(".py", ".ipynb")
            output = subprocess.run(
                [
                    "jupytext",
                    "--to",
                    "ipynb",
                    str(example),
                    "--output",
                    str(DESTINATION_DIR / notebook_path),
                ],
                capture_output=True,
            )
            logger.debug(f"Converted {example} to {DESTINATION_DIR / notebook_path}")

            if output.returncode != 0:
                logger.error(f"Error converting {example} to script")
                logger.error(output.stderr)

            # Disable execution if required
            basename = os.path.basename(example)
            if basename in EXAMPLES_TO_NOT_EXECUTE:
                logger.warning(f"Disable execution of example {basename}.")
                with open(str(DESTINATION_DIR / notebook_path), "r") as f:
                    nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)
                if "nbsphinx" not in nb.metadata:
                    nb.metadata["nbsphinx"] = {}
                nb.metadata["nbsphinx"]["execute"] = "never"
                with open(str(DESTINATION_DIR / notebook_path), "w", encoding="utf-8") as f:
                    nbformat.write(nb, f)

        if count == 0:
            logger.warning("No python examples found to convert to scripts")
        else:
            logger.info(f"Converted {count} python examples to scripts")


def setup(app):
    """Run different hook functions during the documentation build."""
    app.add_directive("pprint", PrettyPrintDirective)
    # Configuration inited hooks
    app.connect("config-inited", check_pandoc_installed)
    app.connect("config-inited", copy_examples_structure)
    # Builder inited hooks
    app.connect("builder-inited", convert_examples_into_notebooks)
    app.connect("builder-inited", skip_gif_examples_to_build_pdf)
    # Source read hook
    app.connect("source-read", adjust_image_path)
    # Build finished hooks
    app.connect("build-finished", remove_examples)
    app.connect("build-finished", remove_doctree)
    app.connect("build-finished", copy_script_examples)


# -- General configuration ---------------------------------------------------

# Add any extension module names here as strings.
extensions = [
    "sphinx.ext.graphviz",
    "sphinx.ext.mathjax",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx_copybutton",
    "sphinx_design",
    "nbsphinx",
    "recommonmark",
    "numpydoc",
]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.11", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    "numpy": ("https://numpy.org/devdocs", None),
    "matplotlib": ("https://matplotlib.org/stable", None),
    "imageio": ("https://imageio.readthedocs.io/en/stable", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    "pytest": ("https://docs.pytest.org/en/stable", None),
}

toc_object_entries_show_parents = "hide"

html_show_sourcelink = True

# numpydoc configuration
numpydoc_use_plots = True
numpydoc_show_class_members = False
numpydoc_xref_param_type = True
numpydoc_validate = True
numpydoc_validation_checks = {
    # general
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    # Return
    "RT04",  # Return value description should start with a capital letter"
    "RT05",  # Return value description should finish with "."
    # Summary
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    "SS03",  # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    "SS05",  # Summary must start with infinitive verb, not third person
    # Parameters
    "PR10",  # Parameter "{param_name}" requires a space before the colon
    # separating the parameter name and type",
}

# Copy button customization ---------------------------------------------------
# exclude traditional Python prompts from the copied code
copybutton_prompt_text = r">>> ?|\.\.\. "
copybutton_prompt_is_regexp = True

# The language for content autogenerated.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "conf.py",
]

# -- Options for HTML output -------------------------------------------------

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

# The master toctree document.
master_doc = "index"

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# NbSphinx customization

# Execute notebooks before conversion
nbsphinx_execute = "always"

# Allow errors to help debug
nbsphinx_allow_errors = False

# Define static thumbnails
nbsphinx_thumbnails = {}


# Define custom notebook format
nbsphinx_custom_formats = {
    ".py": ["jupytext.reads", {"fmt": ""}],
}

# Define prolog and epilog

nbsphinx_prolog = """

.. admonition:: Download this example

    Download this example as a `Jupyter Notebook <{examples_url}/version/dev/{notebook_path}>`_
    or as a `Python script <{examples_url}/version/dev/{python_script_path}>`_.

----
""".format(
    examples_url=f"https://{cname}",
    notebook_path="{{ env.docname }}.ipynb",
    python_script_path="{{ env.docname }}.py",
)

nbsphinx_epilog = """
----

.. admonition:: Download this example

    Download this example as a `Jupyter Notebook <{examples_url}/version/dev/{notebook_path}>`_
    or as a `Python script <{examples_url}/version/dev/{python_script_path}>`_.

""".format(
    examples_url=f"https://{cname}",
    notebook_path="{{ env.docname }}.ipynb",
    python_script_path="{{ env.docname }}.py",
)

# Pyvista customization

# Must be less than or equal to the XVFB window size
pyvista.global_theme["window_size"] = np.array([1024, 768])

# Save figures in specified directory
pyvista.FIGURE_PATH = os.path.join(os.path.abspath("./images/"), "auto-generated/")
if not os.path.exists(pyvista.FIGURE_PATH):
    os.makedirs(pyvista.FIGURE_PATH)

# -- Options for HTML output -------------------------------------------------
html_short_title = html_title = "PyAEDT Examples"
html_theme = "ansys_sphinx_theme"
html_favicon = ansys_favicon

html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": USERNAME,
    "github_repo": REPOSITORY_NAME,
    "github_version": BRANCH,
    "doc_path": DOC_PATH,
}

# specify the location of your github repo
html_theme_options = {
    "logo": "ansys",
    "github_url": f"https://github.com/{USERNAME}/{REPOSITORY_NAME}",
    "show_prev_next": False,
    "collapse_navigation": True,
    "use_edit_page_button": True,
    "show_breadcrumbs": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
        ("PyAEDT", "https://aedt.docs.pyansys.com/"),
    ],
    "icon_links": [
        {
            "name": "Support",
            "url": f"https://github.com/{USERNAME}/{REPOSITORY_NAME}/discussions",
            "icon": "fa fa-comment fa-fw",
        },
    ],
}

html_static_path = ["_static"]

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    "css/custom.css",
    "css/highlight.css",
]

# -- Options for LaTeX output ------------------------------------------------
# additional logos for the latex coverpage
latex_additional_files = [watermark, ansys_logo_white, ansys_logo_white_cropped]

# change the preamble of latex with customized title page
# variables are the title of pdf, watermark
latex_elements = {"preamble": latex.generate_preamble(html_title)}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        f"{project}.tex",
        f"{project} documentation",
        author,
        "manual",
    ),
]
