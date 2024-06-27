# Configuration file for the Sphinx_PyAEDT documentation builder.

# -- Project information -----------------------------------------------------
import datetime
from importlib import import_module
import json
import os
from pathlib import Path
from pprint import pformat
from docutils.nodes import document

# import re
import shutil
from typing import Any
from sphinx.application import Sphinx
import sys
import warnings

# from sphinx_gallery.sorting import FileNameSortKey
from ansys_sphinx_theme import (
    ansys_favicon,
    ansys_logo_white,
    ansys_logo_white_cropped,
    # get_version_match,
    latex,
    pyansys_logo_black,
    watermark,
)
from docutils import nodes
from docutils.parsers.rst import Directive
import numpy as np
import pyvista
from sphinx import addnodes
from sphinx.builders.latex import LaTeXBuilder
from sphinx.util import logging

LaTeXBuilder.supported_image_types = ["image/png", "image/pdf", "image/svg+xml"]

logger = logging.getLogger(__name__)
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

# os.environ["PYAEDT_NON_GRAPHICAL"] = "1"
# os.environ["PYAEDT_DOC_GENERATION"] = "1"

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


# Sphinx builder specific events hook


def check_example_error(app: Sphinx, pagename: str, templatename:str , context:dict[str, Any], doctree: document):
    """Log an error if the execution of an example as a notebook triggered an error.

    Since the documentation build might not stop if the execution of a notebook triggered
    an error, we use a flag to log that an error is spotted in the html page context.
    """
    # Check if the HTML contains an error message
    if pagename.startswith("examples") and not pagename.endswith("/index"):
        if any(
            map(
                lambda msg: msg in context["body"],
                [
                    "UsageError",
                    "NameError",
                    "DeadKernelError",
                    "NotebookError",
                    "CellExecutionError",
                ],
            )
        ):
            logger.error(f"An error was detected in file {pagename}")
            app.builder.config.html_context["build_error"] = True


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


def copy_examples(app: Sphinx):
    """Copy root directory examples files into the doc/source/examples directory.
    
    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx instance containing all the configuration for the documentation build.
    """
    destination_dir = Path(app.srcdir, "examples").resolve()
    logger.info(f"Copying examples from {EXAMPLES_DIRECTORY} to {destination_dir}.")

    if os.path.exists(destination_dir):
        size = directory_size(destination_dir)
        logger.info(f"Directory {destination_dir} ({size} MB) already exist, removing it.")
        shutil.rmtree(destination_dir, ignore_errors=True)
        logger.info(f"Directory removed.")

    shutil.copytree(EXAMPLES_DIRECTORY, destination_dir)
    logger.info(f"Copy performed")


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


def check_pandoc_installed(app: Sphinx):
    """Ensure that pandoc is installed
    
    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx instance containing all the configuration for the documentation build.
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
    destination_dir = Path(app.srcdir) / "examples"

    size = directory_size(destination_dir)
    logger.info(f"Removing directory {destination_dir} ({size} MB).")
    shutil.rmtree(destination_dir, ignore_errors=True)
    logger.info(f"Directory removed.")

def check_build_finished_without_error(app: Sphinx, exception: None | Exception):
    """Check that no error is detected along the documentation build process.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx instance containing all the configuration for the documentation build.
    exception : None or Exception
        Exception raised during the build process.
    """
    if app.builder.config.html_context.get("build_error", False):
        logger.info("Build failed due to an error in html-page-context")
        exit(1)

def remove_doctree(app: Sphinx, exception: None | Exception):
    """Remove the .doctree directory created during the documentation build.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx instance containing all the configuration for the documentation build.
    exception : None or Exception
        Exception raised during the build process.
    """
    # Keep the doctree to avoid creating it twice. This is typically helpful in CI/CD
    # where we want to build both HTML and PDF pages.
    if bool(int(os.getenv("SPHINXBUILD_KEEP_DOCTREEDIR", "0"))):
        logger.info(f"Keeping directory {app.doctreedir}.")
    else:
        size = directory_size(app.doctreedir)
        logger.info(f"Removing doctree {app.doctreedir} ({size} MB).")
        shutil.rmtree(app.doctreedir, ignore_errors=True)
        logger.info(f"Doctree removed.")


def setup(app):
    """Run different hook functions during the documentation build.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx instance containing all the configuration for the documentation build.
    """
    app.add_directive("pprint", PrettyPrintDirective)
    # Builder specific hook
    app.connect("html-page-context", check_example_error)
    # Builder inited hooks
    app.connect("builder-inited", copy_examples)
    app.connect("builder-inited", check_pandoc_installed)
    app.connect("builder-inited", skip_gif_examples_to_build_pdf)
    # Source read hook
    app.connect("source-read", adjust_image_path)
    # Build finished hooks
    app.connect("build-finished", remove_examples)
    app.connect("build-finished", remove_doctree)
    app.connect("build-finished", check_build_finished_without_error)

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

# numpydoc_validation_exclude = {  # set of regex
#     r"\.AEDTMessageManager.add_message$",  # bad SS05
#     r"\.Modeler3D\.create_choke$",  # bad RT05
#     r"HistoryProps.",  # bad RT05 because of the base class named OrderedDict
# }

# # Add any paths that contain templates here, relative to this directory.
# templates_path = ["_templates"]

# # disable generating the sphinx nested documentation
# if "PYAEDT_CI_NO_AUTODOC" in os.environ:
#     templates_path.clear()


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
    # "_build",
    # "sphinx_boogergreen_theme_1",
    # "Thumbs.db",
    # ".DS_Store",
    # "*.txt",
    "conf.py",
    # "constants.py",
]

# inheritance_graph_attrs = dict(rankdir="RL", size='"8.0, 10.0"', fontsize=14, ratio="compress")
# inheritance_node_attrs = dict(
#     shape="ellipse", fontsize=14, height=0.75, color="dodgerblue1", style="filled"
# )


# -- Options for HTML output -------------------------------------------------

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

# The master toctree document.
master_doc = "index"

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# Execute notebooks before conversion
nbsphinx_execute = "always"

# Allow errors to help debug.
nbsphinx_allow_errors = False

# NbSphinx customization
nbsphinx_thumbnails = {
    "examples/00-EDB/00_EDB_Create_VIA": "_static/thumbnails/diff_via.png",
}
nbsphinx_custom_formats = {
    ".py": ["jupytext.reads", {"fmt": ""}],
}

# Pyvista customization
# pyvista.set_error_output_file("errors.txt")
# Ensure that offscreen rendering is used for docs generation
# pyvista.OFF_SCREEN = True
# Preferred plotting style for documentation
# pyvista.set_plot_theme('document')
# must be less than or equal to the XVFB window size
pyvista.global_theme["window_size"] = np.array([1024, 768])

# Save figures in specified directory
pyvista.FIGURE_PATH = os.path.join(os.path.abspath("./images/"), "auto-generated/")
if not os.path.exists(pyvista.FIGURE_PATH):
    os.makedirs(pyvista.FIGURE_PATH)

# # suppress annoying matplotlib bug
# warnings.filterwarnings(
#     "ignore",
#     category=UserWarning,
#     message="Matplotlib is currently using agg so figures are not shown.",
# )

# necessary for pyvista when building the sphinx gallery
# pyvista.BUILDING_GALLERY = True

# jinja_contexts = {
#     "main_toctree": {
#         "run_examples": config["run_examples"],
#     },
# }
# def prepare_jinja_env(jinja_env) -> None:
#     """
#     Customize the jinja env.
#
#     Notes
#     -----
#     See https://jinja.palletsprojects.com/en/3.0.x/api/#jinja2.Environment
#     """
#     jinja_env.globals["project_name"] = project
#
#
# autoapi_prepare_jinja_env = prepare_jinja_env

# -- Options for HTML output -------------------------------------------------
html_short_title = html_title = "PyAEDT Examples"
html_theme = "ansys_sphinx_theme"
html_logo = pyansys_logo_black
html_favicon = ansys_favicon

# specify the location of your github repo
html_theme_options = {
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
