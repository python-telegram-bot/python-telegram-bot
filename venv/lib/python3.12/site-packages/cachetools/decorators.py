import functools

from .keys import hashkey


def cached(cache, key=hashkey, lock=None):
    """Decorator to wrap a function with a memoizing callable that saves
    results in a cache.

    """

    def decorator(func):
        if cache is None:

            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

        elif lock is None:

            def wrapper(*args, **kwargs):
                k = key(*args, **kwargs)
                try:
                    return cache[k]
                except KeyError:
                    pass  # key not found
                v = func(*args, **kwargs)
                try:
                    cache[k] = v
                except ValueError:
                    pass  # value too large
                return v

        else:

            def wrapper(*args, **kwargs):
                k = key(*args, **kwargs)
                try:
                    with lock:
                        return cache[k]
                except KeyError:
                    pass  # key not found
                v = func(*args, **kwargs)
                # in case of a race, prefer the item already in the cache
                try:
                    with lock:
                        return cache.setdefault(k, v)
                except ValueError:
                    return v  # value too large

        return functools.update_wrapper(wrapper, func)

    return decorator


def cachedmethod(cache, key=hashkey, lock=None):
    """Decorator to wrap a class or instance method with a memoizing
    callable that saves results in a cache.

    """

    def decorator(method):
        if lock is None:

            def wrapper(self, *args, **kwargs):
                c = cache(self)
                if c is None:
                    return method(self, *args, **kwargs)
                k = key(*args, **kwargs)
                try:
                    return c[k]
                except KeyError:
                    pass  # key not found
                v = method(self, *args, **kwargs)
                try:
                    c[k] = v
                except ValueError:
                    pass  # value too large
                return v

        else:

            def wrapper(self, *args, **kwargs):
                c = cache(self)
                if c is None:
                    return method(self, *args, **kwargs)
                k = key(*args, **kwargs)
                try:
                    with lock(self):
                        return c[k]
                except KeyError:
                    pass  # key not found
                v = method(self, *args, **kwargs)
                # in case of a race, prefer the item already in the cache
                try:
                    with lock(self):
                        return c.setdefault(k, v)
                except ValueError:
                    return v  # value too large

        return functools.update_wrapper(wrapper, method)

    return decorator
