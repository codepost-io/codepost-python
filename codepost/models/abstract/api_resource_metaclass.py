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

# External dependencies
import better_exceptions as _better_exceptions

# Local imports
import codepost.util.logging as _logging
import codepost.api_requestor as _api_requestor

# =============================================================================

# Global submodule constants
_LOG_SCOPE = "{}".format(__name__)

# Global submodule protected attributes
_logger = _logging.get_logger(name=_LOG_SCOPE)

# =============================================================================

class APIResourceMetaclass(type):
    
    def __getid(cls):
        id_field_name = getattr(cls, "_FIELD_ID", "id")
        data = getattr(cls, "_data", dict())
        id = data.get(id_field_name, None)
        
        # If no identifier, raise exception
        if id == None:
            raise AttributeError("No identifier, as resource is not instantiated.")
            
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
        
        if field_type == None:
            field_tuple = getattr(cls, "_FIELDS", dict()).get(field_name, None)
            if isinstance(field_tuple, tuple) and len(field_tuple) >= 1:
                field_type = field_tuple[0]
        
        if field_type == None:
            field_type = str
        
        if field_doc == None:
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

# =============================================================================
