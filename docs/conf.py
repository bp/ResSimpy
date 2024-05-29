# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ResSimpy'
copyright = '2024, BP'
author = 'BP'
release = '2.2.2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

autoclass_content = "class"  # Alternatively, "both" to include init method
# autodoc_default_options = {
#     'members': None,
#     'inherited-members': None,
#     'private-members': None,
#     'show-inheritance': None,
# }
autosummary_generate = True  # Make _autosummary files and include them
autosummary_generate_overwrite = True

napoleon_use_rtype = False  # More legible
autodoc_member_order = 'bysource'
# napoleon_numpy_docstring = False  # Force consistency, leave only Google

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'autoclasstoc',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options custom autoclasstoc sections ------------------------------------

# See https://autoclasstoc.readthedocs.io/en/latest/advanced_usage.html

from autoclasstoc import PublicMethods


class CommomMethods(PublicMethods):
    key = "common-methods"
    title = "Commonly Used Methods:"

    def predicate(self, name, attr, meta):
        return super().predicate(name, attr, meta) and 'common' in meta


class OtherMethods(PublicMethods):
    key = "other-methods"
    title = "Methods:"

    def predicate(self, name, attr, meta):
        return super().predicate(name, attr, meta) and 'common' not in meta


autoclasstoc_sections = [
    "public-attrs",
    "common-methods",
    "other-methods",
]



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# autodoc Options
autodoc_mock_imports = ["numpy", "pandas", "resqpy"]