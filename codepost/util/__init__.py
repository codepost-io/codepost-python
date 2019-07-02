# =============================================================================
# codePost v2.0 SDK
#
# UTILITY SUB-MODULES
# =============================================================================

from __future__ import print_function # Python 2

# Python stdlib imports
import inspect as _inspect
import sys as _sys

# External dependencies
try:
    # Python 3
    from enum import Enum as _Enum
except ImportError: # pragma: no cover
    no_enum = True

    # Python 2 fallbacks
    try:
        from aenum import Enum as _Enum
        no_enum = False
    except ImportError:
        try:
            from enum34 import Enum as _Enum
            no_enum = False
        except ImportError:
            pass

    if no_enum:
        raise RuntimeError(
            "This package requires an 'Enum' object. These are available "
            "in Python 3.4+, but requires a third-party library, either "
            "'enum34' or 'aenum'. Please install:\n\npip install --user aenum")

# Local import
from . import config
from . import logging

# =============================================================================

def is_stringable(obj):
    # type: str -> bool
    try:
        str(obj)
    except:
        return False
    return True

def robust_str(obj, default="N/A"):
    # type: Any -> str
    obj_str = default
    if is_stringable(obj):
        obj_str = str(obj)
    return obj_str

class DocEnum(_Enum):
    def __init__(self, value, doc):
        # type: (str, str) -> None
        try:
            super().__init__()
        except TypeError: # pragma: no cover
            # Python 2: the super() syntax was only introduced in Python 3.x
            super(DocEnum, self).__init__()
        self._value_ = value
        self.__doc__ = doc

def filter_kwargs_for_function(func, kwargs):
    
    keys_from_func = set()
    if _sys.version_info >= (3, 0):
        # Python 3
        sig = _inspect.signature(func)
        keys_from_func = set(
            param.name
            for param in sig.parameters.values()
            if param.kind == param.POSITIONAL_OR_KEYWORD
        )
    else: # pragma: no cover
        # Python 2
        keys_from_func = set(_inspect.getargspec(func).args)
    
    keys_from_kwargs = set(kwargs.keys())
    keys = keys_from_kwargs.intersection(keys_from_func)
    
    filtered_kwargs = { key: kwargs[key] for key in keys }
    
    return filtered_kwargs
