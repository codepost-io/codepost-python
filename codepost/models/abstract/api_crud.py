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
import importlib as _importlib

# External dependencies
import better_exceptions as _better_exceptions

# Local imports
import codepost.util.custom_logging as _logging
import codepost.api_requestor as _api_requestor

from . import api_resource as _api_resource

# =============================================================================

# Global submodule constants
_LOG_SCOPE = "{}".format(__name__)

# Global submodule protected attributes
_logger = _logging.get_logger(name=_LOG_SCOPE)

# =============================================================================

class CreatableAPIResource(_api_resource.AbstractAPIResource):
    """
    Abstract class for API resources which can be created (Crud).
    """

    def create(self, **kwargs):
        """
        Create an API resource with the provided field parameters, and return
        it as an object.
        """
        _class_type = type(self)

        # FIXME: do kwargs validation
        data = self._get_data_and_extend(**kwargs)

        ret = self._requestor._request(
            endpoint=self.class_endpoint,
            method="POST",
            data=data,
        )
        if ret.status_code == 201:
            return _class_type(**ret.json)

    def saveInstanceAsNew(self, **kwargs):
        """
        Create a duplicate of the instantiated API resource. If allowed, this
        will make a call to create a new API resource with identical fields but
        a new ID, and it will update the internal state of the object as well
        as return the new object.
        """
        obj = self.create(**kwargs)

        # Sanity check
        assert (
            getattr(self, "_OBJECT_NAME", "") ==
            getattr(obj, "_OBJECT_NAME", ""))

        self._data = obj._data

        return self

# =============================================================================

class ReadableAPIResource(_api_resource.AbstractAPIResource):
    """
    Abstract class for API resources which can be read (cRud).
    """

    def retrieve(self, id):
        """
        Retrieve an API resource with the provided `id`.
        """
        _class_type = type(self)

        ret = self._requestor._request(
            endpoint=self.instance_endpoint_by_id(id=id),
            method="GET",
        )
        if ret.status_code == 200:
            return _class_type(**ret.json)

    def refreshInstance(self):
        """
        Refresh the existing instantiated API resource. This will make a call
        to retrieve the API resource with the same ID as the current instance
        and it will update the internal state of the object.
        """
        id = self._get_id()

        obj = self.retrieve(id=id)

        # Sanity check
        assert (
            getattr(self, "_OBJECT_NAME", "") ==
            getattr(obj, "_OBJECT_NAME", ""))

        self._data = obj._data

        return self

    def _retrieve_related_objects(self, related_field):
        """
        Retrieve a related object (or objects) given the fieldname corresponding
        to its id (or list of ids)
        """

        related_objects = getattr(self, "_FIELDS_RELATED_OBJECTS", {}   )

        if related_field in related_objects.keys():
            data = self._data.get(related_field)

            # Make sure the retrieved field is a valid object type (int or int list)
            is_single_object = isinstance(data, int)
            is_object_list = isinstance(data, list) and all(isinstance(n, int) for n in data)

            # If this fails, FIELD_RELATED_OBJECTS contains a key it shouldn't
            assert(is_single_object or is_object_list)

            # detect type of child
            object_module = _importlib.import_module('.instantiated', package="codepost")
            class_module = getattr(object_module, related_objects[related_field])

            # retrieve child or children
            if is_single_object:
                return class_module.retrieve(id=data)
            else:
                return list(map(lambda x: class_module.retrieve(id=x), data))
        else:
            assert(False) # FIXME: raise proper exception here


# =============================================================================

class UpdatableAPIResource(_api_resource.AbstractAPIResource):
    """
    Abstract class for API resources which can be updated (crUd).
    """

    def update(self, id, **kwargs):
        """
        Update an API resource provided its `id` and fields to modify.
        """
        _class_type = type(self)

        # FIXME: do kwargs validation
        data = self._get_data_and_extend(**kwargs)

        ret = self._requestor._request(
            endpoint=self.instance_endpoint_by_id(id=id),
            method="PATCH",
            data=data,
        )
        if ret.status_code == 200:
            return _class_type(**ret.json)

    def saveInstance(self, **kwargs):
        """
        Update the instance of the API resource so as to save all recently
        modified fields.
        """
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
    """
    Abstract class for API resources which can be deleted (cruD).
    """

    def delete(self, id):
        """
        Delete an API resource provided its `id`.
        """
        ret = self._requestor._request(
            endpoint=self.instance_endpoint_by_id(id=id),
            method="DELETE",
        )
        return (ret.status_code == 204)

    def deleteInstance(self):
        """
        Delete the API resource of which this object is an instance.
        """
        id = self._get_id()
        return self.delete(id=id)

# =============================================================================



