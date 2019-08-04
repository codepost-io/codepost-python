# =============================================================================
# codePost v2.0 SDK
#
# API RESOURCE SUB-MODULE
# =============================================================================

from __future__ import print_function # Python 2

# Python stdlib imports
import copy as _copy
import functools as _functools
import textwrap as _textwrap
import typing as _typing

# External dependencies
import better_exceptions as _better_exceptions
try:
    import forge as _forge
except ImportError: # pragma: no cover
    _forge = None
finally:
    _FORGE_VOID = _forge.void if _forge else "<void>"

# Local imports
import codepost.errors as _errors
import codepost.util.custom_logging as _logging
import codepost.api_requestor as _api_requestor

from . import api_crud as _crud

# =============================================================================

# Global submodule constants
_LOG_SCOPE = "{}".format(__name__)

# Global submodule protected attributes
_logger = _logging.get_logger(name=_LOG_SCOPE)

# =============================================================================

class APIResourceMetaclass(type):
    """
    Metaclass to configure abstract codePost model classes.
    """

    def __getid(cls):
        id_field_name = getattr(cls, "_FIELD_ID", "id")
        data = getattr(cls, "_data", dict())
        id = data.get(id_field_name, None)

        # If no identifier, raise exception
        if id == None:
            raise _errors.StaticObjectError()
            #raise AttributeError("No identifier, as resource is not instantiated.")

        return id

    def __setitem(cls, name, value):
        s = super(type(cls), cls)
        _data = getattr(s, "_data", None)
        if _data:
            _data.__setitem__(name, value)
        #super(type(cls), cls)._data.__setitem__(name, value)

    def __bound_setitem(cls, value, field_name=None, field_type=None):
        # Keep track of changing items
        old_value = getattr(cls, field_name, None)
        if old_value != value:
            changed_fields = getattr(cls, "_changed", list())
            changed_fields.append(field_name)
            setattr(cls, "_changed", changed_fields)

        cls._data.__setitem__(field_name, value)

    def __bound_getitem(cls, field_name=None):
        return cls._data.__getitem__(field_name)

    def __mk_property(cls, field_name=None, field_type=None, field_doc=None):

        if field_type is None:
            field_tuple = getattr(cls, "_FIELDS", dict()).get(field_name, None)
            if isinstance(field_tuple, tuple) and len(field_tuple) >= 1:
                field_type = field_tuple[0]

        if field_type is None:
            field_type = str

        if field_doc is None:
            field_tuple = getattr(cls, "_FIELDS", dict()).get(field_name, None)
            if isinstance(field_tuple, tuple) and len(field_tuple) >= 2:
                field_type = field_tuple[1]

        return property(

            fget=_functools.partial(APIResourceMetaclass.__bound_getitem,
                                    field_name=field_name),

            fset=_functools.partial(APIResourceMetaclass.__bound_setitem,
                                    field_name=field_name,
                                    field_type=field_type),

            doc="\n".join(_textwrap.wrap(field_doc))
        )

    @classmethod
    def _build_signature(
        cls,
        obj,
        with_fields=True,
        with_id=True,
        with_self=True,
        all_optional=False):

        parameters = []

        if with_self:
            parameters.append(_forge.arg("self"))

        if with_id:
            parameters.append(_forge.arg(obj._FIELD_ID, type=int))

        if with_fields:

            # Recompute FIELDS object

            fields = obj._FIELDS

            if isinstance(fields, list):
                fields = { key: str for key in fields }

            if isinstance(fields, dict):
                # FIXME: Not sure what the line about _typing.GenericAlias was about
                fields = {
                    key: (val, "") if (isinstance(val, type))# or
                                    #isinstance(val, _typing._GenericAlias))
                    else val
                    for (key, val) in fields.items()
                }

            # Create forge parameters

            for (key, val) in fields.items():
                if key  in obj._FIELDS_READ_ONLY:
                    continue

                if all_optional or not key in obj._FIELDS_REQUIRED:
                    parameters.append(
                        _forge.arg(key, type=val[0], default=_FORGE_VOID))
                else:
                    parameters.append(
                        _forge.arg(key, type=val[0]))

        return _forge.FSignature(parameters=parameters)

    def __init__(cls, name, bases, attrs):
        # Initialize the data store of the class, if necessary
        cls._data = getattr(cls, "_data", dict())

        # Retrieve and process attribute names
        fields = getattr(cls, "_FIELDS", dict())
        _fields_read_only = getattr(cls, "_FIELDS_READ_ONLY", list())
        _fields_required = getattr(cls, "_FIELDS_REQUIRED", list())

        # Post-process _FIELDS list/dictionary
        if isinstance(fields, list):
            fields = { key: (str, None) for key in fields }

        # Define special getter for the ID field
        setattr(cls,
                "id",
                property(
                    fget=APIResourceMetaclass.__getid,
                    doc="The API-provided ID of the instantiated resource."))

        for field_name in fields:
            field_type = fields[field_name][0]
            field_doc = fields[field_name][1]
            setattr(cls,
                    field_name,
                    APIResourceMetaclass.__mk_property(
                        cls,
                        field_name=field_name,
                        field_type=field_type,
                        field_doc=field_doc))

        if _forge:
            # Only works in Python 3.5+ which has
            # the python-forge package

            if _crud.CreatableAPIResource in bases:
                cls.create = _forge.sign(
                    *APIResourceMetaclass._build_signature(
                        obj=cls,
                        all_optional=False,
                        with_id=False))(cls.create)
                cls.saveInstanceAsNew = _forge.sign(
                    *APIResourceMetaclass._build_signature(
                        obj=cls,
                        all_optional=True,
                        with_id=False))(cls.saveInstanceAsNew)

            if _crud.UpdatableAPIResource in bases:
                cls.update = _forge.sign(
                    *APIResourceMetaclass._build_signature(
                        obj=cls,
                        all_optional=True,
                        with_id=True))(cls.update)
                cls.saveInstance = _forge.sign(
                    *APIResourceMetaclass._build_signature(
                        obj=cls,
                        all_optional=True,
                        with_id=False))(cls.saveInstance)

# =============================================================================
