# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'swingmusic'
copyright = '2025, Mungai Njoroge'
author = 'Mungai Njoroge'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.githubpages',
    'sphinx.ext.autosummary',
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "myst_parser",
    "sphinx_design"
]

# extension config
myst_enable_extensions = ["colon_fence"]
autosummary_generate = True  # Turn on sphinx.ext.autosummary
todo_include_todos = True

# design config
templates_path = ['_templates']
exclude_patterns = []
language = 'en'


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = 'furo'
html_static_path = ['_static']

autodoc_default_options = {
    'member-order': 'bysource'
}

add_module_names = False
