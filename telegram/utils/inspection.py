import inspect

try:
    def get_positional_arguments(func):
        args, _, _, defaults = inspect.getargspec(func)
        # Filter out positional arguments
        kwargs = args[:-len(defaults)]
        return kwargs
except Warning:  # `getargspec()` is deprecated in Python3
    def get_positional_arguments(func):
        _, varargs, _, _, _, _, _ = inspect.getfullargspec(func)
        return varargs
