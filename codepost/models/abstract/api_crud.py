# =============================================================================
# codePost v2.0 SDK
#
# CRUD ABSTRACT API RESOURCE VERBS SUB-MODULE
# =============================================================================

from __future__ import print_function # Python 2

# External dependencies
import better_exceptions as _better_exceptions

# Local imports
import codepost.errors as _errors
import codepost.util.custom_logging as _logging

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

        # Cannot take an ID
        if self._FIELD_ID in kwargs:
            raise _errors.CannotChooseIDError()

        # FIXME: do kwargs validation
        data = self._get_data_and_extend(static=True, **kwargs)

        ret = self._requestor._request(
            endpoint=self.class_endpoint,
            method="POST",
            data=data,
        )
        if ret.status_code == 201:
            return _class_type(**ret.json)

    def duplicate(self, in_place=False, **kwargs):
        """
        Return a duplicate of the instantiated API resource. If allowed, this
        will make a call to create a new API resource with identical fields but
        a new ID. If the parameter `in_place` is `True`, it will also update
        the internal state of the instance, in addition to returning the new
        object.
        """
        
        data = self._get_data_and_extend(**kwargs)
        obj = self.create(**data)

        # Sanity check
        assert (
            getattr(self, "_OBJECT_NAME", "") ==
            getattr(obj, "_OBJECT_NAME", ""))

        if in_place:
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
        _id = id
        _class_type = type(self)

        if not self._validate_id(id=_id):
            raise _errors.InvalidIDError()

        ret = self._requestor._request(
            endpoint=self.instance_endpoint_by_id(id=_id),
            method="GET",
        )
        if ret.status_code == 200:
            return _class_type(**ret.json)

    def refresh(self):
        """
        Refresh the existing instantiated API resource. This will make a call
        to retrieve the API resource with the same ID as the current instance
        and it will update the internal state of the object.
        """

        # Will throw an exception if this is a "static" object
        _id = self._get_id()
        obj = self.retrieve(id=_id)

        # Sanity check
        assert (
            getattr(self, "_OBJECT_NAME", "") ==
            getattr(obj, "_OBJECT_NAME", ""))

        self._data = obj._data

        return self

# =============================================================================

class UpdatableAPIResource(_api_resource.AbstractAPIResource):
    """
    Abstract class for API resources which can be updated (crUd).
    """

    def update(self, id, **kwargs):
        """
        Update an API resource provided its `id` and fields to modify.
        """
        _id = id
        _class_type = type(self)

        if not self._validate_id(id=_id):
            raise _errors.InvalidIDError()
        
        # FIXME: do kwargs validation
        data = self._get_data_and_extend(static=True, **kwargs)

        ret = self._requestor._request(
            endpoint=self.instance_endpoint_by_id(id=_id),
            method="PATCH",
            data=data,
        )
        if ret.status_code == 200:
            return _class_type(**ret.json)

    def save(self, **kwargs):
        """
        Update the instance of the API resource so as to save all recently
        modified fields.
        """
        
        # FIXME: do kwargs validation
        # NOTE: "id" is contained in the self._data which is extended
        data = self._get_data_and_extend(**kwargs)
        obj = self.update(**data)

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

    def delete(self, id=None):
        """
        Delete an API resource provided its `id` when called statically and
        deletes the instantiated API resource it has been called on otherwise.
        """
        _id = self._get_id(id=id)

        if not self._validate_id(id=_id):
            raise _errors.InvalidIDError()

        ret = self._requestor._request(
            endpoint=self.instance_endpoint_by_id(id=_id),
            method="DELETE",
        )
        return (ret.status_code == 204)

# =============================================================================



