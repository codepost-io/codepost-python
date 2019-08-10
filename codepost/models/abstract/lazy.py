# =============================================================================
# codePost v2.0 SDK
#
# LAZY API RESOURCE WRAPPER SUB-MODULE
# =============================================================================

from __future__ import print_function # Python 2

# Python stdlib imports
import copy as _copy
import functools as _functools
import inspect as _inspect
import json as _json
import logging as _logging
import os as _os
import platform as _platform
import threading as _threading
import time as _time
import uuid as _uuid
import sys as _sys
try:
    # Python 3
    from urllib.parse import urljoin
    from urllib.parse import quote as urlquote
    from urllib.parse import urlencode as urlencode
except ImportError: # pragma: no cover
    # Python 2
    from urlparse import urljoin
    from urllib import quote as urlquote
    from urllib import urlencode as urlencode

# External dependencies
import better_exceptions as _better_exceptions
import requests as _requests

# Local imports
import codepost
import codepost.errors as _errors
import codepost.models.abstract.api_resource as _api_resource

# =============================================================================

_LAZY_REPR = "<Lazy[{cls.__name__}] loaded={_loaded}: {_inner}>"

# =============================================================================

def create_lazy_resource(cls, id):
    # type: (_api_resource.AbstractAPIResource, int) -> _api_resource.APIResource
    """
    Create a lazy API resource instance of a given type, with a provisional
    identifier `id`. An API call to fetch the object is only made if fields
    from the object are accessed.

    :param cls: The `APIResource` child class
    :param id: The identifier of the resource
    :return: A wrapper object that can be used like the `APIResource` would
    """

    class LazyAPIResource(_api_resource.APIResource):

        # Actual internal object which is
        _inner = None
        _null = False

        def __getattribute__(self, attr):

            # All protected and private attributes should be handled directly
            # by the base class (using __getattribute__ because object does
            # not have a __getattr__).

            if attr is not None and len(attr) > 0 and attr[0:1] == "_":
                return super(LazyAPIResource, self).__getattribute__(attr)

            if self._null:
                return None

            # ===============================================================

            # OBJECT HAS BEEN FETCHED:
            #   If we've already fetched the object, redirect to attributes
            #   of the `_inner` internal object.

            if self._inner is not None:
                return getattr(self._inner, attr, None)

            # ===============================================================

            # OBJECT IS LAZY
            #   Handle any attribute used to extract the identifier manually
            #   and prepare to fetch the object if any other attribute is
            #   accessed.

            if attr == "_data":
                id_field_name = getattr(self, "_FIELD_ID", "id")
                return {
                    id_field_name: id
                }
            elif attr == "id":
                return id
            else:
                # Fetch object and cache
                try:
                    self._inner = cls().retrieve(id=id)
                except _errors.NotFoundAPIError:
                    self._null = True
                except _errors.AuthorizationAPIError:
                    # NOTE: Should this really silently fail? Maybe should
                    # at least log the event
                    self._null = True

                # NOTE: Recall this method so the "fetched" case only has to
                # be handled in one code branch.
                return self.__getattribute__(attr)

        def __setattr__(self, attr, value):

            # Since this object is only a lazy wrapper, all __setattr_ calls
            # are rerouted to the internal object, except modifications to
            # `_inner`.

            if attr == "_inner" or attr == "_null":
                return super(LazyAPIResource, self).__setattr__(attr, value)

            # If internal object has been fetched, reroute calls to it.

            if self._inner is not None:
                return self._inner.__setattr__(attr, value)

        def __repr__(self):

            _loaded = (self._inner is not None)
            return _LAZY_REPR.format(
                cls=cls,
                _loaded=_loaded,
                _inner=self._inner,
            )

    return LazyAPIResource()

# =============================================================================

