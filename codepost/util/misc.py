# =============================================================================
# codePost v2.0 SDK
#
# MISCELLANEOUS UTILITIES SUB-MODULES
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
            """
            This package requires an `Enum` object type. These are available
            as part of the standard library in Python 3.4+, but otherwise
            require a third-party library, either `enum34` or `aenum`.

            => You can install it with `pip` or `pipenv`:
                    pip install --user aenum
               or
                    pipenv install aenum
            """)

# =============================================================================

def is_stringable(obj):
    # type: str -> bool
    try:
        str(obj)
    except:
        return False
    return True

def is_noarg_callable(obj):
    # type: Any -> bool
    try:
        obj()
    except:
        return False
    return True

def robust_str(obj, default="N/A"):
    # type: Any -> str
    obj_str = default
    if is_stringable(obj):
        obj_str = str(obj)
    return obj_str

# =============================================================================

def is_field_set_in_kwargs(field, kwargs):
    # Easy case: The field is not in the dict
    if not field in kwargs:
        return False

    # Easy case: Python 3.5> with forge
    import codepost.models.abstract.api_resource_metaclass as _arm

    if _arm._forge:
        return not (kwargs.get(field) is _arm._FORGE_VOID)

    # Hard case: Python 2.7
    # (Since signature is not coerced by forge, there are no spurious
    # fields in kwargs, and if we've made it this far, the field is in
    # the dict)
    return True

# =============================================================================

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

# =============================================================================

class MissingFormatKey(DocEnum):
    """
    Describes all possible ways that the formatting helper method can address
    the problem of missing format keys.
    """

    ERROR = "missing-keys-error", "Missing format keys throw an error."

    REMAIN = "missing-keys-remain", """
                                    Missing format keys are unaffected, and
                                    can be filled by a later formatting call
                                    """

    REMOVE = "missing-keys-remove", "Missing format keys are removed."

def _make_f(globals, locals):

    def _f(s, missing=MissingFormatKey.REMAIN, **kwargs):
        """
        Formats a string using the local and global symbols available.
        Suppresses any warning that is not related to string formatting.
        """
        # Resolve the arguments (may be dictionaries or callables)
        g = globals
        l = locals
        if is_noarg_callable(g):
            g = g()
        if is_noarg_callable(l):
            l = l()

        # Make the substitution if the string provided is not empty
        if s:
            try:
                # Make two substitutions for patterns who unspool their
                # own substitutions (the missing key will be captured)

                # To avoid a syntax error in Python 2.7
                merged = kwargs.copy()
                merged.update(g)
                merged.update(l)

                temp = s.format(**merged)
                temp = temp.format(**merged)
                return temp
            except KeyError as err:
                missing_key = err.args[0]
                missing_key_val = None

                if missing == MissingFormatKey.ERROR:
                    # Re-raise the error
                    raise

                elif missing == MissingFormatKey.REMAIN:
                    # Replace the missing key by {missing key} so it can
                    # still be substituted by a subsequent call.

                    missing_key_val = "{{{key}}}".format(key=missing_key)

                elif missing == MissingFormatKey.REMOVE:
                    # Remove the pattern for the missing key

                    missing_key_val = ""

                new_kw = { missing_key: missing_key_val }

                # To avoid a syntax error in Python 2.7
                merged = new_kw.copy()
                merged.update(kwargs)

                return _f(
                    s=s,
                    missing=missing,
                    **merged
                )
            except ValueError:
                raise
            #except:
            #    pass

    return _f

# =============================================================================

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

# =============================================================================
