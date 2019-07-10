# =============================================================================
# codePost v2.0 SDK
#
# CRUD ABSTRACT API RESOURCE VERBS SUB-MODULE
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

from . import api_resource as _api_resource

# =============================================================================

# Global submodule constants
_LOG_SCOPE = "{}".format(__name__)

# Global submodule protected attributes
_logger = _logging.get_logger(name=_LOG_SCOPE)

# =============================================================================

class CreatableAPIResource(_api_resource.AbstractAPIResource):
    
    def create(self, **kwargs):
        _class_type = type(self)
        
        # FIXME: do kwargs validation
        data = self._get_extended_data(**kwargs)
        
        ret = self._requestor._request(
            endpoint=self.class_endpoint,
            method="POST",
            data=data,
        )
        if ret.status_code == 201:
            return _class_type(**ret.json)
    
    def saveInstanceAsNew(self, **kwargs):
        obj = self.create(**kwargs)

        # Sanity check
        assert (
            getattr(self, "_OBJECT_NAME", "") == 
            getattr(obj, "_OBJECT_NAME", ""))

        self._data = obj._data

        return self

        


# =============================================================================

class ReadableAPIResource(_api_resource.AbstractAPIResource):
    
    def retrieve(self, id):
        _class_type = type(self)
        ret = self._requestor._request(
            endpoint=self.instance_endpoint_by_id(id=id),
            method="GET",
        )
        if ret.status_code == 200:
            return _class_type(**ret.json)
    
    def refreshInstance(self):
        id = self._get_id()
        
        obj = self.retrieve(id=id)

        # Sanity check
        assert (
            getattr(self, "_OBJECT_NAME", "") == 
            getattr(obj, "_OBJECT_NAME", ""))

        self._data = obj._data

        return self



# =============================================================================

class UpdatableAPIResource(_api_resource.AbstractAPIResource):
    
    def update(self, id, **kwargs):
        _class_type = type(self)

        # FIXME: do kwargs validation
        data = self._get_extended_data(**kwargs)

        ret = self._requestor._request(
            endpoint=self.instance_endpoint_by_id(id=id),
            method="PATCH",
            data=data,
        )
        if ret.status_code == 200:
            return _class_type(**ret.json)
    
    def saveInstance(self, **kwargs):
        id = self._get_id()
        obj = self.update(id=id, **kwargs)

        # Sanity check
        assert (
            getattr(self, "_OBJECT_NAME", "") == 
            getattr(obj, "_OBJECT_NAME", ""))

        self._data = obj._data

        return self

# =============================================================================

class DeletableAPIResource(_api_resource.AbstractAPIResource):
    
    def delete(self, id):
        ret = self._requestor._request(
            endpoint=self.instance_endpoint_by_id(id=id),
            method="DELETE",
        )
        return (ret.status_code == 204)
    
    def deleteInstance(self):
        id = self._get_id()
        return self.delete(id=id)

# =============================================================================



