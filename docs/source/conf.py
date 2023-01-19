import collections.abc
import inspect
import os
import re
import subprocess
import sys
import typing
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple, Union

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
from docutils.nodes import Element
from sphinx.application import Sphinx
from sphinx.domains.python import PyXRefRole
from sphinx.environment import BuildEnvironment
from sphinx.util import logging

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
version = "20.0"  # telegram.__version__[:3]
# The full version, including alpha/beta/rc tags.
release = "20.0"  # telegram.__version__

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = "5.1.1"

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

# get the sphinx(!) logger
# Makes sure logs render in red and also plays nicely with e.g. the `nitpicky` option.
sphinx_logger = logging.getLogger(__name__)

CONSTANTS_ROLE = "tg-const"
import telegram  # We need this so that the `eval` below works


class TGConstXRefRole(PyXRefRole):
    """This is a bit of Sphinx magic. We add a new role type called tg-const that allows us to
    reference values from the `telegram.constants.module` while using the actual value as title
    of the link.

    Example:

        :tg-const:`telegram.constants.MessageLimit.MAX_TEXT_LENGTH` renders as `4096` but links to the
        constant.
    """

    def process_link(
        self,
        env: BuildEnvironment,
        refnode: Element,
        has_explicit_title: bool,
        title: str,
        target: str,
    ) -> Tuple[str, str]:
        title, target = super().process_link(env, refnode, has_explicit_title, title, target)
        try:
            # We use `eval` to get the value of the expression. Maybe there are better ways to
            # do this via importlib or so, but it does the job for now
            value = eval(target)
            # Maybe we need a better check if the target is actually from tg.constants
            # for now checking if it's an Enum suffices since those are used nowhere else in PTB
            if isinstance(value, Enum):
                # Special casing for file size limits
                if isinstance(value, telegram.constants.FileSizeLimit):
                    return f"{int(value.value / 1e6)} MB", target
                return repr(value.value), target
            # Just for (Bot API) versions number auto add in constants:
            if isinstance(value, str) and target in (
                "telegram.constants.BOT_API_VERSION",
                "telegram.__version__",
            ):
                return value, target
            if isinstance(value, tuple) and target in (
                "telegram.constants.BOT_API_VERSION_INFO",
                "telegram.__version_info__",
            ):
                return repr(value), target
            sphinx_logger.warning(
                f"%s:%d: WARNING: Did not convert reference %s. :{CONSTANTS_ROLE}: is not supposed"
                " to be used with this type of target.",
                refnode.source,
                refnode.line,
                refnode.rawsource,
            )
            return title, target
        except Exception as exc:
            sphinx_logger.exception(
                "%s:%d: WARNING: Did not convert reference %s due to an exception.",
                refnode.source,
                refnode.line,
                refnode.rawsource,
                exc_info=exc,
            )
            return title, target


def autodoc_skip_member(app, what, name, obj, skip, options):
    """We use this to not document certain members like filter() or check_update() for filters.
    See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#skipping-members"""

    included = {"MessageFilter", "UpdateFilter"}  # filter() and check_update() only for these.
    included_in_obj = any(inc in repr(obj) for inc in included)

    if included_in_obj:  # it's difficult to see if check_update is from an inherited-member or not
        for frame in inspect.stack():  # From https://github.com/sphinx-doc/sphinx/issues/9533
            if frame.function == "filter_members":
                docobj = frame.frame.f_locals["self"].object
                if not any(inc in str(docobj) for inc in included) and name == "check_update":
                    return True
                break

    if name == "filter" and obj.__module__ == "telegram.ext.filters":
        if not included_in_obj:
            return True  # return True to exclude from docs.


# ------------------------------------------------------------------------------------------------
# This part is for getting the [source] links on the classes, methods etc link to the correct
# files & lines on github. Can be simplified once https://github.com/sphinx-doc/sphinx/issues/1556
# is closed

line_numbers = {}
file_root = Path(inspect.getsourcefile(telegram)).parent.parent.resolve()
import telegram.ext  # Needed for checking if an object is a BaseFilter

keyword_args = [
    ":keyword _sphinx_paramlinks_telegram.Bot.{method}.read_timeout: Value to pass to :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to {read_timeout}.",
    ":kwtype _sphinx_paramlinks_telegram.Bot.{method}.read_timeout: {read_timeout_type}, optional",
    ":keyword _sphinx_paramlinks_telegram.Bot.{method}.write_timeout: Value to pass to :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to {write_timeout}.",
    ":kwtype _sphinx_paramlinks_telegram.Bot.{method}.write_timeout: :obj:`float` | :obj:`None`, optional",
    ":keyword _sphinx_paramlinks_telegram.Bot.{method}.connect_timeout: Value to pass to :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.",
    ":kwtype _sphinx_paramlinks_telegram.Bot.{method}.connect_timeout: :obj:`float` | :obj:`None`, optional",
    ":keyword _sphinx_paramlinks_telegram.Bot.{method}.pool_timeout: Value to pass to :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.",
    ":kwtype _sphinx_paramlinks_telegram.Bot.{method}.pool_timeout: :obj:`float` | :obj:`None`, optional",
    ":keyword _sphinx_paramlinks_telegram.Bot.{method}.api_kwargs: Arbitrary keyword arguments to be passed to the Telegram API.",
    ":kwtype _sphinx_paramlinks_telegram.Bot.{method}.api_kwargs: :obj:`dict`, optional",
    "",
]

write_timeout_sub = [":attr:`~telegram.request.BaseRequest.DEFAULT_NONE`", "``20``"]
read_timeout_sub = [
    ":attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.",
    "``2``. :paramref:`timeout` will be added to this value",
]
read_timeout_type = [":obj:`float` | :obj:`None`", ":obj:`float`"]


def find_insert_pos_for_kwargs(lines: List[str]) -> int:
    """Finds the correct position to insert the keyword arguments and returns the index."""
    for idx, value in reversed(list(enumerate(lines))):  # reversed since :returns: is at the end
        if value.startswith(":returns:"):
            return idx
    else:
        return False


def is_write_timeout_20(obj: object) -> int:
    """inspects the default value of write_timeout parameter of the bot method."""
    sig = inspect.signature(obj)
    return 1 if (sig.parameters["write_timeout"].default == 20) else 0


def check_timeout_and_api_kwargs_presence(obj: object) -> int:
    """Checks if the method has timeout and api_kwargs keyword only parameters."""
    sig = inspect.signature(obj)
    params_to_check = (
        "read_timeout",
        "write_timeout",
        "connect_timeout",
        "pool_timeout",
        "api_kwargs",
    )
    return all(
        param in sig.parameters and sig.parameters[param].kind == inspect.Parameter.KEYWORD_ONLY
        for param in params_to_check
    )


class AdmonitionInserter:
    """Class for inserting admonitions into docs of Telegram classes."""

    # We cannot move this code to a separate module within docs because there is no way
    # to import it.  This class is simply a way of encapsulating the code and providing a better
    # overview of conf.py.

    ADMONITION_TYPES = ("use_in", "available_in", "returned_in")

    FORWARD_REF_PATTERN = re.compile(r"^ForwardRef\('(?P<class_name>\w+)'\)$")
    """ A pattern to find a class name in a ForwardRef typing annotation.
    Class name (in a named group) is surrounded by parentheses and single quotes.
    Note that since we're analyzing argument by argument, the pattern can be strict, with
    start and end markers.
    """

    METHODS_FOR_BOT_AND_APPBUILDER = {
        telegram.Bot: tuple(
            m[0]
            for m in inspect.getmembers(telegram.Bot, inspect.isfunction)  # not .ismethod
            if not m[0].startswith("_")
            and m[0].islower()  # islower() to avoid camelCase methods
            and m[0] in telegram.Bot.__dict__  # method is not inherited from TelegramObject
        ),
        telegram.ext.ApplicationBuilder: tuple(
            m[0]
            for m in inspect.getmembers(telegram.ext.ApplicationBuilder, inspect.isfunction)
            if not m[0].startswith("_") and m[0] in telegram.ext.ApplicationBuilder.__dict__
        ),
    }
    """Relevant methods to be mentioned in 'Returned in' and 'Use in' admonitions:
    Bot methods(public, not aliases, not inherited from TelegramObject) and ApplicationBuilder
    methods.
    """

    def __init__(self):
        self.admonitions: Dict[str, Dict[str, str]] = {
            # dynamically determine which method to use to create a sub dictionary
            admonition_type: getattr(self, f"_create_{admonition_type}")()
            for admonition_type in self.ADMONITION_TYPES
        }
        """Dictionary with admonitions. Contains sub-dictionaries, one per admonition type. 
        Each sub-dictionary matches class names to texts of admonitions, e.g.:
        ```
        {
        "use_in": {"<class 'telegram._chatinvitelink.ChatInviteLink'": 
        <"Use in" admonition for ChatInviteLink>, ...},
        "available_in": {"<class 'telegram._chatinvitelink.ChatInviteLink'": 
        <"Available in" admonition">, ...},
        "returned_in": {...}
        }
        ```
        """

    def insert_admonitions_for_class(
        self,
        name: str,
        docstring_lines: List[str],
    ):
        """Inserts admonitions into docstring lines for a class with the given name.

        **Modifies lines in place**.
        """
        # A better way would be to copy the lines and return them, but that will not work with
        # autodoc_process_docstring()

        for admonition_type in self.ADMONITION_TYPES:

            # If there is no admonition of the given type for the given class,
            # continue to the next admonition type, maybe the class is listed there.
            if name not in self.admonitions[admonition_type]:
                continue

            insert_idx = self._find_insert_pos_for_admonition(docstring_lines)
            admonition_lines = self.admonitions[admonition_type][name].splitlines()

            for idx in range(insert_idx, insert_idx + len(admonition_lines)):
                docstring_lines.insert(idx, admonition_lines[idx - insert_idx])

    def _create_available_in(self) -> Dict[str, str]:
        """Creates a dictionary with 'Available in' admonitions for classes that are available
        in attributes of other classes.
        """

        # Generate a mapping of class names to ReST links to attributes in other classes that
        # correspond to instances of a given class
        # i.e. {"telegram._files.sticker.Sticker": {":attr:`telegram.Message.sticker`", ...}}
        attrs_for_class_name = defaultdict(set)

        # The following regex is supposed to capture a class name in a line like this:
        # media (:obj:`str` | :class:`telegram.InputFile`): Audio file to send.

        attr_docstr_pattern = re.compile(
            r"^\s*(?P<attr_name>[a-z_]+)"  # Any number of spaces, named group for attribute
            r"\s?\("  # Optional whitespace, opening parenthesis
            r".*"  # Any number of characters (that could denote a built-in type)
            r":class:`.+`"  # Marker of a classref, class name in backticks
            r".*\):"  # Any number of characters, closing parenthesis, colon.
            # The ^ colon above is important because it makes sure that the class is mentioned in
            # the attribute description, not in free text.
            r"\s.*$",  # Whitespace, any number of characters, end of string (end of line)
            re.VERBOSE,
        )

        # for properties: there is no attr name in docstring.  Just check if there's a class name.
        prop_docst_pattern = re.compile(r":class:`.+`.*:")

        single_class_name_pattern = re.compile(r":class:`~?(?P<class_name>[\w.]*)`")

        classes_to_inspect = inspect.getmembers(telegram, inspect.isclass) + inspect.getmembers(
            telegram.ext, inspect.isclass
        )

        for _, inspected_class in classes_to_inspect:
            # We need to make "<class 'telegram._files.sticker.StickerSet'>" into
            # "telegram.StickerSet" because that's the way the classes are mentioned in
            # docstrings
            name_of_inspected_class_in_docstr = (
                str(inspected_class).removeprefix("<class '").removesuffix("'>")
            )
            # removing things like "_files.sticker"
            name_of_inspected_class_in_docstr = ".".join(
                n
                for n in name_of_inspected_class_in_docstr.split(".")
                if n in ("telegram", "ext") or not n.islower()
            )

            # Parsing part of the docstring with attributes (parsing of properties follows later)
            docstring_lines = inspect.getdoc(inspected_class).splitlines()
            lines_with_attrs = []
            for idx, line in enumerate(docstring_lines):
                if line.strip() == "Attributes:":
                    lines_with_attrs = docstring_lines[idx + 1 :]

            for line in lines_with_attrs:
                line_match = attr_docstr_pattern.match(line)
                if not line_match:
                    continue

                target_attr = line_match.group("attr_name")
                # a typing description of one attribute can contain multiple classes
                for match in single_class_name_pattern.finditer(line):
                    name_of_class_in_attr = match.group("class_name")
                    full_class_name = self._resolve_full_class_name(name_of_class_in_attr)
                    if full_class_name is None:
                        continue

                    # Writing to dictionary: matching the class found in the docstring to the
                    # attribute of the class being inspected.
                    # Key is the class in the attribute docstring, value is the attribute of the
                    # class currently being inspected.
                    attrs_for_class_name[full_class_name].add(
                        f":attr:`{name_of_inspected_class_in_docstr}.{target_attr}`"
                    )

            # Properties need to be parsed separately because they act like attributes but not
            # listed as attributes.
            properties = inspect.getmembers(inspected_class, lambda o: isinstance(o, property))
            for prop_name, _ in properties:
                # Make sure this property is really defined in the class being inspected.
                # A property can be inherited from a parent class, then a link to it will not work.
                if prop_name not in inspected_class.__dict__:
                    continue

                # 1. Can't use typing.get_type_hints because double-quoted type hints
                #    (like "Application") will throw a NameError
                # 2. Can't use inspect.signature because return annotations of properties can be
                #    hard to parse (like "(self) -> BD").
                # 3. fget is used to access the actual function under the property wrapper
                docstring = inspect.getdoc(getattr(inspected_class, prop_name).fget)
                if docstring is None:
                    continue

                first_line = docstring.splitlines()[0]
                if not prop_docst_pattern.match(first_line):
                    continue

                for match in single_class_name_pattern.finditer(first_line):
                    name_of_class_in_prop = match.group("class_name")
                    if "telegram" not in name_of_class_in_prop:
                        continue

                    # Writing to dictionary: matching the class found in the docstring to the
                    # property of the class being inspected.
                    # The class in the property docstring is the key, and the property of the
                    # class currently being inspected is the value.
                    attrs_for_class_name[self._resolve_full_class_name(name_of_class_in_prop)].add(
                        f":attr:`{name_of_inspected_class_in_docstr}.{prop_name}`"
                    )

        return self._generate_admonitions(attrs_for_class_name, admonition_type="available_in")

    def _create_returned_in(self) -> Dict[str, str]:
        """Creates a dictionary with 'Returned in' admonitions for classes that are returned
        in Bot's and ApplicationBuilder's methods.
        """

        # Generate a mapping of class names to ReST links to Bot methods which return it,
        # i.e. {"<class 'telegram._message.Message'>": {:meth:`telegram.Bot.send_message`, ...}}
        methods_for_class_name = defaultdict(set)

        for klass, methods in self.METHODS_FOR_BOT_AND_APPBUILDER.items():
            for method in methods:

                sig = inspect.signature(getattr(klass, method))
                ret_annot = sig.return_annotation
                returned_classes = typing.get_args(ret_annot)

                method_link = self._generate_link_to_method(method, klass)

                # If we do get_args() when return annotation has one single class
                # (e.g. <class 'telegram._message.Message'>), get_args() returns an empty tuple.
                if not returned_classes:
                    methods_for_class_name[self._resolve_arg(ret_annot)].add(method_link)
                    continue

                for ret_cls in returned_classes:
                    methods_for_class_name[self._resolve_arg(ret_cls)].add(method_link)

        return self._generate_admonitions(methods_for_class_name, admonition_type="returned_in")

    def _create_use_in(self) -> Dict[str, str]:
        """Creates a dictionary with 'Use in' admonitions for classes whose instances are
        accepted as arguments for Bot's and ApplicationBuilder's methods.
        """

        # Generate a mapping of class names to links to Bot methods which accept them as arguments,
        # i.e. {"<class 'telegram._inline.inlinequeryresult.InlineQueryResult'>":
        # {:meth:`telegram.Bot.answer_inline_query`, ...}}
        methods_for_class_name = defaultdict(set)  # using set because there can be repetitions

        for klass, relevant_methods_for_class in self.METHODS_FOR_BOT_AND_APPBUILDER.items():
            for method in relevant_methods_for_class:
                method_link = self._generate_link_to_method(method, klass)

                sig = inspect.signature(getattr(klass, method))
                parameters = sig.parameters

                for param in parameters.values():
                    annotation = param.annotation

                    if isinstance(annotation, (type, str)):
                        methods_for_class_name[self._resolve_arg(annotation)].add(method_link)

                    elif isinstance(annotation, typing.TypeVar):
                        bound = annotation.__bound__  # gets access to the "bound=..." parameter
                        methods_for_class_name[self._resolve_arg(bound)].add(method_link)

                    elif typing.get_origin(annotation) in (
                        dict,
                        type,
                        collections.Sequence,
                        collections.Callable,
                        Union,
                    ):
                        for arg in typing.get_args(annotation):
                            methods_for_class_name[self._resolve_arg(arg)].add(method_link)
                    else:
                        raise NotImplementedError(
                            f"Unable to process annotation {annotation} of type {type(annotation)}"
                            f" (origin {typing.get_origin(annotation)}, attrs {vars(annotation)}, "
                            f"get_args {typing.get_args(annotation)})."
                        )

        return self._generate_admonitions(methods_for_class_name, admonition_type="use_in")

    @staticmethod
    def _find_insert_pos_for_admonition(lines: List[str]) -> int:
        """Finds the correct position to insert the class admonition and returns the index.
        If no key phrases are found, the admonition will be inserted at the very end.
        """
        for idx, value in list(enumerate(lines)):
            # The space after ":param" is important because a docstring can contain ":paramref:"
            # in its plain text in the beginning of a line (e.g. ExtBot)
            if value.startswith(".. version") or value.startswith(":param "):
                return idx
        return len(lines) - 1

    def _generate_admonitions(
        self,
        attrs_or_methods_for_class_name: Dict[str, Set[str]],
        admonition_type: str,
    ) -> Dict[str, str]:
        """Generates admonitions of a given type.
        Takes a dictionary of class names matched to ReST links to methods or attributes, e.g.:

        ```
        {"<class 'telegram._files.sticker.StickerSet'>":
        [":meth: `telegram.Bot.get_sticker_set`", ...]}.
        ```

        Returns a dictionary of class names matched to full admonitions, e.g.
        for `admonition_type` "returned_in" (note that title and CSS class are generated
        automatically):

        ```
        {"<class 'telegram._files.sticker.StickerSet'>":
        ".. admonition:: Returned in: :class: returned-in :meth: `telegram.Bot.get_sticker_set`"}.
        ```
        """
        #

        if admonition_type not in self.ADMONITION_TYPES:
            raise TypeError(f"Admonition type {admonition_type} not supported.")

        admonition_for_class_name = {}

        for class_name, attrs in attrs_or_methods_for_class_name.items():
            attrs = sorted(attrs)

            # for admonition type "use_in" the title will be "Use in" and CSS class "use-in".
            admonition = f"""

.. admonition:: {admonition_type.title().replace("_", " ")}
    :class: {admonition_type.replace("_", "-")}
    """
            if len(attrs) > 1:
                for target_attr in attrs:
                    admonition += "\n    * " + target_attr
            else:
                admonition += f"\n    {attrs[0]}"

            admonition += "\n    "  # otherwise an unexpected unindent warning will be issued
            admonition_for_class_name[class_name] = admonition

        return admonition_for_class_name

    @staticmethod
    def _generate_link_to_method(method_name: str, base_class: type):
        """Generates a ReST link to a Bot method."""
        if base_class == telegram.Bot:
            return f":meth:`telegram.Bot.{method_name}`"
        elif base_class == telegram.ext.ApplicationBuilder:
            return f":meth:`telegram.ext.ApplicationBuilder.{method_name}`"
        else:
            raise NotImplementedError(f"Base class {base_class} not supported")

    def _resolve_arg(self, arg: Any) -> Union[str, None]:
        """Analyzes an argument of a method (separate argument or an element of typing.get_args())
        and returns full name of class that the argument belongs to, if it can be resolved
        to a telegram or telegram.ext class.
        """

        origin = typing.get_origin(arg)

        if (
            origin in (collections.Callable, typing.IO)
            or arg is None
            # no other check available (by type or origin) for these:
            or str(type(arg)) in ("<class 'typing._SpecialForm'>", "<class 'ellipsis'>")
        ):
            pass

        # RECURSIVE CALLS
        # for cases like Union[Sequence....
        elif typing.get_origin(arg) in (
            dict,
            tuple,
            Union,
            collections.Coroutine,
            collections.Sequence,
            typing.Sequence,
        ):
            for sub_arg in typing.get_args(arg):
                return self._resolve_arg(sub_arg)

        elif isinstance(arg, list):
            for item in arg:
                return self._resolve_arg(item)

        elif isinstance(arg, typing.TypeVar):
            # gets access to the "bound=..." parameter
            return self._resolve_arg(arg.__bound__)

        # END RECURSIVE CALLS

        elif isinstance(arg, type):
            if "telegram" in str(arg):
                return str(arg)

        elif isinstance(arg, typing.ForwardRef):
            m = self.FORWARD_REF_PATTERN.match(str(arg))
            # We're sure it's a ForwardRef, so, unless it belongs to known exceptions,
            # the class name must be resolved.
            # If it isn't resolved, we'll have the program throw an exception to be sure.
            try:
                class_name = self._resolve_full_class_name(m.group("class_name"))
            except AttributeError:
                if str(arg) == "ForwardRef('DefaultValue[DVType]')":
                    # this is a known ForwardRef that needs not be resolved to a Telegram class
                    return
                else:
                    raise NotImplementedError(f"Could not process ForwardRef: {arg}")
            return class_name

        # For some reason "InlineQueryResult" and "InputMedia" are currently not recognized
        # as ForwardRefs and are identified as plain strings.
        elif isinstance(arg, str):
            class_name = self._resolve_full_class_name(arg)
            # Here we don't want an exception to be thrown since we're not sure it's ForwardRef
            if class_name is not None:
                return class_name

        else:
            raise NotImplementedError(
                f"Cannot process argument {arg} of type {type(arg)} (origin {origin})"
            )

    @staticmethod
    def _resolve_full_class_name(name: str) -> Union[str, None]:
        """The keys in the admonitions dictionary are not the likes of "telegram.StickerSet"
        but the likes of "<class 'telegram._files.sticker.StickerSet'>".

        This method attempts to produce a full class name from a name that does or does not
        contain the word 'telegram', e.g.
        "<class 'telegram._files.sticker.StickerSet'>" from "telegram.StickerSet" or "StickerSet".

        Returns :obj:`str` on success, :obj:`None` if nothing could be resolved.
        """

        for option in (name, f"telegram.{name}", f"telegram.ext.{name}"):
            try:
                return str(eval(option))
            # NameError will be raised if trying to eval just name and it doesn't work, e.g.
            # "Name 'ApplicationBuilder' is not defined".
            # AttributeError will be raised if trying to e.g. eval f"telegram.{name}" when the
            # class denoted by `name` actually belongs to `telegram.ext`:
            # "module 'telegram' has no attribute 'ApplicationBuilder'".
            # If neither option works, this is not a PTB class.
            except (NameError, AttributeError):
                continue


def autodoc_process_docstring(
    app: Sphinx, what, name: str, obj: object, options, lines: List[str]
):
    """We do the following things:
    1) Use this method to automatically insert the Keyword Args for the Bot methods.

    2) Use this method to automatically insert "Returned in" admonition into classes
       that are returned from the Bot methods

    3) Use this method to automatically insert "Available in" admonition into classes
       whose instances are available as attributes of other classes

    4) Use this method to automatically insert "Use in" admonition into classes
       whose instances can be used as arguments of the Bot methods

    5) Misuse this autodoc hook to get the file names & line numbers because we have access
       to the actual object here.
    """

    # 1) Insert the Keyword Args for the Bot methods
    method_name = name.split(".")[-1]
    if (
        name.startswith("telegram.Bot.")
        and what == "method"
        and method_name.islower()
        and check_timeout_and_api_kwargs_presence(obj)
    ):
        insert_index = find_insert_pos_for_kwargs(lines)
        if not insert_index:
            raise ValueError(
                f"Couldn't find the correct position to insert the keyword args for {obj}."
            )

        long_write_timeout = is_write_timeout_20(obj)
        get_updates_sub = 1 if (method_name == "get_updates") else 0
        # The below can be done in 1 line with itertools.chain, but this must be modified in-place
        for i in range(insert_index, insert_index + len(keyword_args)):
            lines.insert(
                i,
                keyword_args[i - insert_index].format(
                    method=method_name,
                    write_timeout=write_timeout_sub[long_write_timeout],
                    read_timeout=read_timeout_sub[get_updates_sub],
                    read_timeout_type=read_timeout_type[get_updates_sub],
                ),
            )

    # 2-4) Insert "Returned in", "Available in", "Use in" admonitions into classes
    # (where applicable)
    if what == "class":
        AdmonitionInserter().insert_admonitions_for_class(
            name=str(obj),
            docstring_lines=lines,
        )

    # 5) Get the file names & line numbers
    # We can't properly handle ordinary attributes.
    # In linkcode_resolve we'll resolve to the `__init__` or module instead
    if what == "attribute":
        return

    # Special casing for properties
    if hasattr(obj, "fget"):
        obj = obj.fget

    # Special casing for filters
    if isinstance(obj, telegram.ext.filters.BaseFilter):
        obj = obj.__class__

    try:
        source_lines, start_line = inspect.getsourcelines(obj)
        end_line = start_line + len(source_lines)
        file = Path(inspect.getsourcefile(obj)).relative_to(file_root)
        line_numbers[name] = (file, start_line, end_line)
    except Exception:
        pass

    # Since we don't document the `__init__`, we call this manually to have it available for
    # attributes -- see the note above
    if what == "class":
        autodoc_process_docstring(app, "method", f"{name}.__init__", obj.__init__, options, lines)


def _git_branch() -> str:
    """Get's the current git sha if available or fall back to `master`"""
    try:
        output = subprocess.check_output(  # skipcq: BAN-B607
            ["git", "describe", "--tags", "--always"], stderr=subprocess.STDOUT
        )
        return output.decode().strip()
    except Exception as exc:
        sphinx_logger.exception(
            "Failed to get a description of the current commit. Falling back to `master`.",
            exc_info=exc,
        )
        return "master"


git_branch = _git_branch()
base_url = "https://github.com/python-telegram-bot/python-telegram-bot/blob/"


def linkcode_resolve(_, info):
    """See www.sphinx-doc.org/en/master/usage/extensions/linkcode.html"""
    combined = ".".join((info["module"], info["fullname"]))
    # special casing for ExtBot which is due to the special structure of extbot.rst
    combined = combined.replace("ExtBot.ExtBot", "ExtBot")

    line_info = line_numbers.get(combined)

    if not line_info:
        # Try the __init__
        line_info = line_numbers.get(f"{combined.rsplit('.', 1)[0]}.__init__")
    if not line_info:
        # Try the class
        line_info = line_numbers.get(f"{combined.rsplit('.', 1)[0]}")
    if not line_info:
        # Try the module
        line_info = line_numbers.get(info["module"])

    if not line_info:
        return

    file, start_line, end_line = line_info
    return f"{base_url}{git_branch}/{file}#L{start_line}-L{end_line}"


# End of logic for the [source] links
# ------------------------------------------------------------------------------------------------


# Some base classes are implementation detail
# We want to instead show *their* base class
PRIVATE_BASE_CLASSES = {
    "_ChatUserBaseFilter": "MessageFilter",
    "_Dice": "MessageFilter",
    "_BaseThumbedMedium": "TelegramObject",
    "_BaseMedium": "TelegramObject",
    "_CredentialsBase": "TelegramObject",
}


def autodoc_process_bases(app, name, obj, option, bases: list):
    """Here we fine tune how the base class's classes are displayed."""
    for idx, base in enumerate(bases):
        # let's use a string representation of the object
        base = str(base)

        # Special case because base classes are in std lib:
        if "StringEnum" in base == "<enum 'StringEnum'>":
            bases[idx] = ":class:`enum.Enum`"
            bases.insert(0, ":class:`str`")
            continue

        if "IntEnum" in base:
            bases[idx] = ":class:`enum.IntEnum`"
            continue

        # Drop generics (at least for now)
        if base.endswith("]"):
            base = base.split("[", maxsplit=1)[0]
            bases[idx] = f":class:`{base}`"

        # Now convert `telegram._message.Message` to `telegram.Message` etc
        match = re.search(pattern=r"(telegram(\.ext|))\.[_\w\.]+", string=base)
        if not match or "_utils" in base:
            continue

        parts = match.group(0).split(".")

        # Remove private paths
        for index, part in enumerate(parts):
            if part.startswith("_"):
                parts = parts[:index] + parts[-1:]
                break

        # Replace private base classes with their respective parent
        parts = [PRIVATE_BASE_CLASSES.get(part, part) for part in parts]

        base = ".".join(parts)

        bases[idx] = f":class:`{base}`"


def setup(app: Sphinx):
    app.connect("autodoc-skip-member", autodoc_skip_member)
    app.connect("autodoc-process-bases", autodoc_process_bases)
    app.connect("autodoc-process-docstring", autodoc_process_docstring)
    app.add_role_to_domain("py", CONSTANTS_ROLE, TGConstXRefRole())
