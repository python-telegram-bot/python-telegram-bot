import inspect

"""
Reflects on a function or method to retrieve all positional and keyword arguments available.
"""
try:
    def inspect_arguments(func):
        args, _, _, _ = inspect.getargspec(func)
        return args
except Warning:  # `getargspec()` is deprecated in Python3
    def inspect_arguments(func):
        args, _, _, _, _, _, _ = inspect.getfullargspec(func)
        return args
