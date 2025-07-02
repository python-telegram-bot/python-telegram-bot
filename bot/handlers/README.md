

# handlers

this folder serves as the placeholder for all function handlers:

`bot` &raquo; `handlers` &raquo; 
```
handlers
|___ ...
|___ index.py
|___ ...
|___ start.py
|___  echo.py
```

## `index.py`
this file registers all command handler inside this directory:

`bot` &raquo; `handlers` &raquo; [`index.py`](index.py)
```

from .start import start
from .echo import echo
from .help import help
from .whoami import whoami


```
and maps the command handlers name to each function:
```python
command_map = {
    'start': start,
    'echo' : echo,
    # ....
    # one-to-one correspondence mapping 
    # map command to function here
    # ....
    'whoami' : whoami,
    'hello' : hello,
    'help' : help_command
    }
```

by virtue of this registration, we will have a convenient way for `main.py` in the parent folder to import all function handlers in one call: 

`bot` &raquo; [`main.py`](..//./main.py)
```

from handlers.index import index

```

## `start.py`
this is a sample function file which handles the `/start` command

`bot` &raquo; `handlers` &raquo; [`start.py`](start.py)

```
    /start: 
    a start function that replies some simple word

```

## `echo.py`
this is a sample function file which handles the `/echo` command

`bot` &raquo; `handlers` &raquo; [`echo.py`](echo.py)

```
    /echo:
    a simple echo function that replies the same text
    
```

## `hello.py`
this is a sample function file which handles the `/hello` command

`bot` &raquo; `handlers` &raquo; [`hello.py`](hello.py)

```
    /hello:
    just say hello and reply
    
```

## `whoami.py`
this is a sample function file which handles the `/whoami` command

`bot` &raquo; `handlers` &raquo; [`whoami.py`](whoami.py)
```
    /whoami:
    who am i?
    
```

# `help.py`
this is a sample function file which handles the `/help` command

`bot` &raquo; `handlers` &raquo; [`help.py`](help.py)
```
    /help:
    return this help
    
```
