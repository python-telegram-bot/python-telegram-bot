import os
import re
import sys
from pathlib import Path

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
from sphinx.application import Sphinx

sys.path.insert(0, os.path.abspath("../.."))

# -- General configuration ------------------------------------------------
# General information about the project.
project = "python-telegram-bot"
copyright = "2015-2023, Leandro Toledo"
author = "Leandro Toledo"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = "20.2"  # telegram.__version__[:3]
# The full version, including alpha/beta/rc tags.
release = "20.2"  # telegram.__version__

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = "6.1.3"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.linkcode",
    "sphinx.ext.extlinks",
    "sphinx_paramlinks",
    "sphinx_copybutton",
    "sphinxcontrib.mermaid",
    "sphinx_search.extension",
]

# For shorter links to Wiki in docstrings
extlinks = {"wiki": ("https://github.com/python-telegram-bot/python-telegram-bot/wiki/%s", "%s")}

# Use intersphinx to reference the python builtin library docs
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "APScheduler": ("https://apscheduler.readthedocs.io/en/3.x/", None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# Global substitutions
rst_prolog = (Path.cwd() / "../substitutions/global.rst").read_text(encoding="utf-8")

# -- Extension settings ------------------------------------------------
napoleon_use_admonition_for_examples = True

# Don't show type hints in the signature - that just makes it hardly readable
# and we document the types anyway
autodoc_typehints = "none"

# Fail on warnings & unresolved references etc
nitpicky = True

# Paramlink style
paramlinks_hyperlink_param = "name"

# Linkcheck settings
linkcheck_ignore = [
    # Let's not check issue/PR links - that's wasted resources
    r"http(s)://github\.com/python-telegram-bot/python-telegram-bot/(issues|pull)/\d+/?",
    # For some reason linkcheck has a problem with these two:
    re.escape("https://github.com/python-telegram-bot/python-telegram-bot/discussions/new"),
    re.escape("https://github.com/python-telegram-bot/python-telegram-bot/issues/new"),
    # Anchors are apparently inserted by GitHub dynamically, so let's skip checking them
    "https://github.com/python-telegram-bot/python-telegram-bot/tree/master/examples#",
    r"https://github\.com/python-telegram-bot/python-telegram-bot/wiki/[\w\-_,]+\#",
]
linkcheck_allowed_redirects = {
    # Redirects to the default version are okay
    r"https://docs\.python-telegram-bot\.org/.*": r"https://docs\.python-telegram-bot\.org/en/[\w\d\.]+/.*",
    # pre-commit.ci always redirects to the latest run
    re.escape(
        "https://results.pre-commit.ci/latest/github/python-telegram-bot/python-telegram-bot/master"
    ): r"https://results\.pre-commit\.ci/run/github/.*",
}


# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# Decides the language used for syntax highlighting of code blocks.
highlight_language = "python3"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "furo"

# Theme options are theme-specific and customize the look and feel of a theme
# further. For a list of options available for each theme, see the documentation.
html_theme_options = {
    "navigation_with_keys": True,
    "dark_css_variables": {
        "admonition-title-font-size": "0.95rem",
        "admonition-font-size": "0.92rem",
    },
    "light_css_variables": {
        "admonition-title-font-size": "0.95rem",
        "admonition-font-size": "0.92rem",
    },
    "announcement": "PTB has undergone significant changes in v20. Please read the documentation "
    "carefully and also check out the transition guide in the "
    '<a href="https://github.com/python-telegram-bot/python-telegram-bot/wiki/'
    'Transition-guide-to-Version-20.0">wiki</a>.',
    "footer_icons": [
        {
            # Telegram channel logo
            "name": "Telegram Channel",
            "url": "https://t.me/pythontelegrambotchannel/",
            # Following svg is from https://react-icons.github.io/react-icons/search?q=telegram
            "html": '<svg stroke="currentColor" fill="currentColor" stroke-width="0" '
            'viewBox="0 0 16 16" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">'
            '<path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8.287 5.906c-.778.324-2.334.994'
            "-4.666 2.01-.378.15-.577.298-.595.442-.03.243.275.339.69.47l.175.055c.408.133."
            "958.288 1.243.294.26.006.549-.1.868-.32 2.179-1.471 3.304-2.214 3.374-2.23.0"
            "5-.012.12-.026.166.016.047.041.042.12.037.141-.03.129-1.227 1.241-1.846 1.81"
            "7-.193.18-.33.307-.358.336a8.154 8.154 0 0 1-.188.186c-.38.366-.664.64.015 1.08"
            "8.327.216.589.393.85.571.284.194.568.387.936.629.093.06.183.125.27.187.331.23"
            "6.63.448.997.414.214-.02.435-.22.547-.82.265-1.417.786-4.486.906-5.751a1.426 "
            "1.426 0 0 0-.013-.315.337.337 0 0 0-.114-.217.526.526 0 0 0-.31-.093c-.3.005-.7"
            '63.166-2.984 1.09z"></path></svg>',
            "class": "",
        },
        {  # Github logo
            "name": "GitHub",
            "url": "https://github.com/python-telegram-bot/python-telegram-bot/",
            "html": '<svg stroke="currentColor" fill="currentColor" stroke-width="0" '
            'viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 '
            "2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.4"
            "9-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23"
            ".82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 "
            "0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.2"
            "7 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.5"
            "1.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 "
            '1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z">'
            "</path></svg>",
            "class": "",
        },
        {  # PTB website logo - globe
            "name": "python-telegram-bot website",
            "url": "https://python-telegram-bot.org/",
            "html": '<svg stroke="currentColor" fill="currentColor" stroke-width="0" '
            'viewBox="0 0 16 16" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">'
            '<path d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm7.5-6.923c-.67.204-1.335.82-1.887 '
            "1.855-.143.268-.276.56-.395.872.705.157 1.472.257 2.282.287V1.077zM4.249 3.53"
            "9c.142-.384.304-.744.481-1.078a6.7 6.7 0 0 1 .597-.933A7.01 7.01 0 0 0 3.051 "
            "3.05c.362.184.763.349 1.198.49zM3.509 7.5c.036-1.07.188-2.087.436-3.008a9.124 "
            "9.124 0 0 1-1.565-.667A6.964 6.964 0 0 0 1.018 7.5h2.49zm1.4-2.741a12.344 "
            "12.344 0 0 0-.4 2.741H7.5V5.091c-.91-.03-1.783-.145-2.591-.332zM8.5 5.09V7.5h"
            "2.99a12.342 12.342 0 0 0-.399-2.741c-.808.187-1.681.301-2.591.332zM4.51 8.5c.03"
            "5.987.176 1.914.399 2.741A13.612 13.612 0 0 1 7.5 10.91V8.5H4.51zm3.99 0v2.409"
            "c.91.03 1.783.145 2.591.332.223-.827.364-1.754.4-2.741H8.5zm-3.282 3.696c.12.31"
            "2.252.604.395.872.552 1.035 1.218 1.65 1.887 1.855V11.91c-.81.03-1.577.13-2.28"
            "2.287zm.11 2.276a6.696 6.696 0 0 1-.598-.933 8.853 8.853 0 0 1-.481-1.079 8.38 "
            "8.38 0 0 0-1.198.49 7.01 7.01 0 0 0 2.276 1.522zm-1.383-2.964A13.36 13.36 0 0 1"
            " 3.508 8.5h-2.49a6.963 6.963 0 0 0 1.362 3.675c.47-.258.995-.482 1.565-.667zm"
            "6.728 2.964a7.009 7.009 0 0 0 2.275-1.521 8.376 8.376 0 0 0-1.197-.49 8.853 "
            "8.853 0 0 1-.481 1.078 6.688 6.688 0 0 1-.597.933zM8.5 11.909v3.014c.67-.204 "
            "1.335-.82 1.887-1.855.143-.268.276-.56.395-.872A12.63 12.63 0 0 0 8.5 11.91zm"
            "3.555-.401c.57.185 1.095.409 1.565.667A6.963 6.963 0 0 0 14.982 8.5h-2.49a1"
            "3.36 13.36 0 0 1-.437 3.008zM14.982 7.5a6.963 6.963 0 0 0-1.362-3.675c-.47.25"
            "8-.995.482-1.565.667.248.92.4 1.938.437 3.008h2.49zM11.27 2.461c.177.334.339.6"
            "94.482 1.078a8.368 8.368 0 0 0 1.196-.49 7.01 7.01 0 0 0-2.275-1.52c.218.283.4"
            "18.597.597.932zm-.488 1.343a7.765 7.765 0 0 0-.395-.872C9.835 1.897 9.17 1.282 "
            '8.5 1.077V4.09c.81-.03 1.577-.13 2.282-.287z"></path></svg>',
            "class": "",
        },
    ],
}

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = f"python-telegram-bot<br> v{version}"

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = "ptb-logo_1024.png"

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = "ptb-logo_1024.ico"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = [
    "style_external_link.css",
    "style_mermaid_diagrams.css",
    "style_sidebar_brand.css",
    "style_general.css",
    "style_admonitions.css",
    "style_images.css",
]

html_permalinks_icon = "¶"  # Furo's default permalink icon is `#` which doesn't look great imo.

# Output file base name for HTML help builder.
htmlhelp_basename = "python-telegram-bot-doc"

# The base URL which points to the root of the HTML documentation. It is used to indicate the
# location of document using The Canonical Link Relation. Default: ''.
html_baseurl = "https://docs.python-telegram-bot.org"

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    "papersize": "a4paper",
    # The font size ('10pt', '11pt' or '12pt').
    #'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    "preamble": r"""\setcounter{tocdepth}{2}
\usepackage{enumitem}
\setlistdepth{99}""",
    # Latex figure (float) alignment
    #'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "python-telegram-bot.tex", "python-telegram-bot Documentation", author, "manual"),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
latex_logo = "ptb-logo_1024.png"

# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "python-telegram-bot", "python-telegram-bot Documentation", [author], 1)]

# rtd_sphinx_search_file_type = "un-minified"  # Configuration for furo-sphinx-search

# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "python-telegram-bot",
        "python-telegram-bot Documentation",
        author,
        "python-telegram-bot",
        "We have made you a wrapper you can't refuse",
        "Miscellaneous",
    ),
]

# -- script stuff --------------------------------------------------------

# Due to Sphinx behaviour, these imports only work when imported here, not at top of module.

# Not used but must be imported for the linkcode extension to find it
from docs.auxil.link_code import linkcode_resolve
from docs.auxil.sphinx_hooks import (
    autodoc_process_bases,
    autodoc_process_docstring,
    autodoc_skip_member,
)
from docs.auxil.tg_const_role import CONSTANTS_ROLE, TGConstXRefRole


def setup(app: Sphinx):
    app.connect("autodoc-skip-member", autodoc_skip_member)
    app.connect("autodoc-process-bases", autodoc_process_bases)
    app.connect("autodoc-process-docstring", autodoc_process_docstring)
    app.add_role_to_domain("py", CONSTANTS_ROLE, TGConstXRefRole())
