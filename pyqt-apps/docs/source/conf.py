import sys
import os
import datetime
from importlib import metadata
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

sys.path.insert(0, os.path.abspath('../..'))
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

pkg_data = metadata.metadata("siriushla")
year = datetime.date.today().year
author = pkg_data["Author"]
name = pkg_data["Name"]
version = metadata.version("siriushla")

project = name
copyright = f'{year}, {author}'
author = author
release = version
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon'
]

source_suffix = ['.rst', '.md']
templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
autodoc_mock_imports = ["siriuspy", "pcaspy"]
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_context = {
    "display_github": True,
    "github_user": "lnls-sirius",
    "github_repo": "hla",
    "github_version": "master",
    "conf_py_path": "/pyqt-apps/docs/source/"
}
