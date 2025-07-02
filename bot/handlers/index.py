"""
index.py
---------
index all function handlers
"""

# imports here -----------------------
from .start import start
from .echo import echo
from .help import help_command
from .hello import hello
from .whoami import whoami
from .notadoi import notadoi

command_map = {
    'start': start,
    'echo': echo,
    'whoami': whoami,
    'hello': hello,
    'help': help_command,
    'notadoi': notadoi,
}

# --------------------------------------
def index():
    """
    Return the map of all command handlers
    """
    return command_map
