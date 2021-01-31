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
import sys as _sys

# External dependencies
# import better_exceptions as _better_exceptions
try:
    # FIXME: URGENT LINE TO FIX
    # (there is a problem with forge and .tests)
    _forge = None #import forge as _forge
except ImportError: # pragma: no cover
    _forge = None
finally:
    _FORGE_VOID = _forge.void if _forge else "<void>"

# Local imports
import codepost.errors as _errors
import codepost.util.custom_logging as _logging
import codepost.api_requestor as _api_requestor

from . import api_crud as _crud
from . import api_resource as _api_resource
from . import linked_lists as _linked_lists

# =============================================================================

# Global submodule constants
_LOG_SCOPE = "{}".format(__name__)

# Global submodule protected attributes
_logger = _logging.get_logger(name=_LOG_SCOPE)


# =============================================================================

def detect_list_type(typ):
    """
    Internal method to detect whether an abstract type is a List-type, and if so
    returns the type of the list elements. Returns `None` otherwise.

    :param field_type:  The abstract type to be analyzed.
    :return: The type of the list elements, or `None`.
    """

    # Read more about this issue here:
    # https://github.com/swagger-api/swagger-codegen/issues/8921

    if _sys.version_info >= (3, 7):
        if type(typ) is _typing._GenericAlias and typ._name == "List":
            return typ.__args__[0]

    elif _sys.version_info >= (3, 0):
        try:
            if (type(typ) is _typing.GenericMeta and
                    (hasattr(typ, "__extra__") and typ.__extra__ is list)):
                return typ.__args__[0]
        except AttributeError:
            pass

        if hasattr(typ, "__origin__") and typ.__origin__ is _typing.List:
            return typ.__args__[0]


def is_type_variable(typ):
    """
    Determines whether an object is a type variable.

    :param typ:  The variable to be analyzed.
    :return: `True` if variable is either an elementary type or an abstract type.
    """

    # All elementary types are simple
    if type(typ) is type:
        return True

    # Now we must handle "abstract" types (i.e., List[int] for instance)

    # NOTE: Since our framework only uses List[xxx] we can limit to this subcase
    # for the moment (avoid unpredictability).
    _only_allow_list_generic_objects = True

    if _sys.version_info >= (3, 7):
        return type(typ) is _typing._GenericAlias and (
                not _only_allow_list_generic_objects or
                typ._name == "List")

    elif _sys.version_info >= (3, 0):
        try:
            return type(typ) is _typing.GenericMeta and (
                not _only_allow_list_generic_objects or
                (hasattr(typ, "__extra__") and typ.__extra__ is list)
            )
        except AttributeError:
            pass

        return hasattr(typ, "__origin__") and (
            not _only_allow_list_generic_objects or
            typ.__origin__ is _typing.List
        )

    # default case is that `typ` is probably not a type reference
    return False

# =============================================================================


class APIResourceMetaclass(type):
    """
    Metaclass to configure abstract codePost model classes.
    """

    def __getid(cls):
        id_field_name = getattr(cls, "_FIELD_ID", "id")
        data = getattr(cls, "_data", dict())
        _id = data.get(id_field_name, None)

        # If no identifier, raise exception
        if _id == None:
            raise _errors.StaticObjectError()
            #raise AttributeError("No identifier, as resource is not instantiated.")

        return _id

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

        if cls._cache and field_name in cls._cache:
            cls._cache[field_name] = value

    def __pre_save_hook(cls):
        if cls._cache is not None:
            for (field_name, value) in cls._cache.items():
                cls._data[field_name] = value._to_serializable_list()
                value.save()

    def __bound_getitem(cls, field_name=None, field_type=None):

        # Initialize cache if need be
        cls._cache = getattr(cls, "_cache", None)
        if cls._cache is None:
            cls._cache = dict()

        data = cls._data.__getitem__(field_name)

        if field_type is not None:

            # Handle the case where the attribute of the model is a list
            # of related instances.

            list_type = detect_list_type(field_type)

            if list_type is not None:

                # OneToMany relations between objects
                if issubclass(list_type, _api_resource.APIResource):
                    cls._cache[field_name] = cls._cache.get(
                        field_name,
                        _linked_lists.LazyAPILinkedList(
                            iterable=data,
                            cls=list_type,
                            parent_cls=type(cls),
                            parent_id=cls.id,
                            parent_attribute=field_name,
                            query_attribute="name",
                            query_uniqueness=True,
                        ))
                    return cls._cache[field_name]

                # ManyToMany relations with user objects
                elif issubclass(list_type, str):
                    cls._cache[field_name] = cls._cache.get(
                        field_name,
                        _linked_lists.APILinkedList(
                            iterable=data,
                            cls=None,
                            parent_cls=type(cls),
                            parent_id=cls.id,
                            parent_attribute=field_name,
                            query_attribute=None,
                            query_uniqueness=True,
                        ))
                    return cls._cache[field_name]


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
                                    field_name=field_name,
                                    field_type=field_type),

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
                # The default format is (type, default_value).
                # This code tries to expand 'type' -> (type, "")
                # Since some of the type hints can be abstract, like typing.List[int], it has
                # to use the GenericAlias/GenericMeta code
                # see code in:
                # https://github.com/codepost-io/codepost-python/commit/2b0ae00d160ddae0b6540b32bfb2778f428dccd7#diff-b7cc0946b625e77d99cb9a61818cd773R44-R71

                # There are two possibilities:
                # 1) (typ, default_value): a default value is provided -> use it
                # 2) typ: no default value is provided -> use "" instead

                fields = {
                    key: (val, "") if is_type_variable(val)
                    else val
                    for (key, val) in fields.items()
                }

            # Create forge parameters

            for (key, val) in fields.items():
                if key in obj._FIELDS_READ_ONLY:
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

        setattr(cls, "_pre_save_hook",
                lambda self: self._cache and map(
                    lambda obj: obj.save(),
                    self._cache.values()))

        setattr(cls, "_pre_save_hook",
                lambda self: APIResourceMetaclass.__pre_save_hook(self))

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
                        with_id=False))(cls.duplicate)

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
                        with_id=False))(cls.save)

# =============================================================================
