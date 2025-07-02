"""Extensible memoizing collections and decorators."""

from .cache import Cache
from .decorators import cached, cachedmethod
from .fifo import FIFOCache
from .lfu import LFUCache
from .lru import LRUCache
from .mru import MRUCache
from .rr import RRCache
from .ttl import TTLCache

__all__ = (
    "Cache",
    "FIFOCache",
    "LFUCache",
    "LRUCache",
    "MRUCache",
    "RRCache",
    "TTLCache",
    "cached",
    "cachedmethod",
)

__version__ = "4.2.2"
