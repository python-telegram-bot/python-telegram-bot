import inspect

try:
    def inspect_arguments(func):
        args, _, _, _ = inspect.getargspec(func)
        return args
except Warning:  # `getargspec()` is deprecated in Python3
    def inspect_arguments(func):
        args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = inspect.getfullargspec(func)
        return args
