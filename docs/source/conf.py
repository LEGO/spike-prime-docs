# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "SPIKE™ Prime protocol"
copyright = "2024, LEGO® Education"
author = "LEGO® Education"
release = "0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

keep_warnings = True
primary_domain = "std"

import sys, os

sys.path.append(os.path.abspath("ext"))

extensions = [
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.githubpages",
    "sphinx_rtd_theme",
    "role_enum",
    "directive_message",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

html_theme_options = {
    "prev_next_buttons_location": None,
    "collapse_navigation": False,
}

html_copy_source = False
