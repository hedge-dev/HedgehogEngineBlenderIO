# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join("..", "build_files", "extensions")))

# Sphinx errors out on single threaded builds see T86621
sys.setrecursionlimit(2000)


# -- Local Vars --------------------------------------------------------------

heio_version = "1.0.2"

# -- Project information -----------------------------------------------------

project = f'Hedgehog Engine Blender I/O {heio_version}'
author = 'Justin113D, hedge-dev'

version = heio_version
release = heio_version


# -- General configuration ---------------------------------------------------

extensions = [
	"404",
	"reference",
	"sphinx_design",
    "sphinx.ext.todo",
	"sphinx.ext.autosectionlabel",
    "sphinxext.opengraph"
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["../build_files/templates"]

# A string of reStructuredText that will be included at the end of every
# source file that is read. This is a possible place to add substitutions
# that should be available in every file.
rst_epilog = f"""
.. |HEIO_VERSION| replace:: {heio_version}
.. |TODO| replace:: The documentation here is incomplete, you can help by contributing.
"""
# TODO contributing page

# If set to a major.minor version string like "1.1", Sphinx will compare it
# with its version and refuse to build if it is too old.
needs_sphinx = "3.3"

# The default language to highlight source code in.
highlight_language = "python3"

# If true, figures, tables and code-blocks are automatically numbered if they have a caption.
numfig = False

# if set to 0, figures, tables and code-blocks are continuously numbered starting at 1.
numfig_secnum_depth = 0

# -- Options for HTML output -------------------------------------------------

html_theme = 'furo'

# A dictionary of options that influence the look and feel of
# the selected theme. These are theme-specific.
html_theme_options = {}

# A list of paths that contain custom themes, either as subdirectories
# or as zip files. Relative paths are taken as relative to
# the configuration directory.
html_theme_path = []


html_theme_options = {
    "source_edit_link": "https://github.com/hedge-dev/HedgehogEngineBlenderIO/edit/dev/manual/source/{filename}",
    "light_css_variables": {
        "color-brand-primary": "#265787",
        "color-brand-content": "#265787",
    },
}

html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "sidebar/scroll-end.html",
    ]
}

# The "title" for HTML documentation generated with Sphinx"s own templates.
# This is appended to the <title> tag of individual pages, and
# used in the navigation bar as the "topmost" element.
html_title = f"HEIO {heio_version} Manual"

# The base URL which points to the root of the HTML documentation.
# It is used to indicate the location of document using
# The Canonical Link Relation.
html_baseurl = "https://hedge-dev.github.io/HedgehogEngineBlenderIO/"

# If given, this must be the name of an image file
# (path relative to the configuration directory) that is the logo of the docs,
# or URL that points an image file for the logo.
html_logo = "../build_files/theme/heio-logo.svg"

# If given, this must be the name of an image file
# (path relative to the configuration directory) that is the favicon of
# the docs, or URL that points an image file for the favicon.
html_favicon = "../build_files/theme/favicon.png"

html_css_files = [
    "css/theme_overrides.css",
]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["../build_files/theme"]

# If this is not None, a "Last updated on:" timestamp is inserted at
# every page bottom, using the given strftime() format.
# The empty string is equivalent to "%b %d, %Y"
# (or a locale-dependent equivalent).
html_last_updated_fmt = "%Y-%m-%d"

# Additional templates that should be rendered to HTML pages,
# must be a dictionary that maps document names to template names.
html_additional_pages = {
    "404": "404.html",
}

# If true, the reST sources are included in the HTML build as _sources/name.
html_copy_source = False

# If true (and html_copy_source is true as well), links to the reST sources
# will be added to the sidebar.
html_show_sourcelink = False

# If nonempty, an OpenSearch description file will be output,
# and all pages will contain a <link> tag referring to it.
# Ed. Note: URL has to be adapted, when versioning is set up.
html_use_opensearch = "https://hedge-dev.github.io/HedgehogEngineBlenderIO/"

# If true, "(C) Copyright …" is shown in the HTML footer.
html_show_copyright = True

# If true, "Created using Sphinx" is shown in the HTML footer.
html_show_sphinx = False

# If true, the text around the keyword is shown as summary of each search result.
html_show_search_summary = True


# -- Options for HTML help output --------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "HEIO Reference Manual"


# -- Extension configuration -------------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
# if not release.endswith("release"):
todo_include_todos = True
# todo_link_only = True

autosectionlabel_prefix_document = True

ogp_site_url = "https://hedge-dev.github.io/HedgehogEngineBlenderIO/"
ogp_site_name = "Hedgehog Engine Blender I/O Manual"
ogp_image = "_images/heio-logo.png"
ogp_type = "website"
ogp_enable_meta_description = True
ogp_custom_meta_tags = [
    "<meta name=\"theme-color\" content=\"#21BFB7\" />",
    "<meta name=\"twitter:card\" content=\"summary_large_image\" />",
]