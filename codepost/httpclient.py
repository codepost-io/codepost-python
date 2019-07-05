# =============================================================================
# codePost v2.0 SDK
#
# HTTP CLIENT SUB-MODULE
# =============================================================================

from __future__ import print_function # Python 2

# Python stdlib imports
import copy as _copy
import functools as _functools
import inspect as _inspect
import json as _json
import logging as _logging
import os as _os
import threading as _threading
import time as _time
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
from .util import config as _config
from .util import logging as _logging

from .util.misc import _make_f

# =============================================================================

# Replacement f"..." compatible with Python 2 and 3
_f = _make_f(globals=lambda: globals(), locals=lambda: locals())

# =============================================================================

# Global submodule constants
_LOG_SCOPE = "{}".format(__name__)

# Global submodule protected attributes
_logger = _logging.get_logger(name=_LOG_SCOPE)

# =============================================================================

class HTTPResponse(dict):

    def __init__(self, data=None):
        if data:
            try:
                self.update(data)
            except:
                pass
    
    @property
    def status_code(self):
        return self.get("status_code", 200)

    @property
    def content(self):
        return self.get("content", None)
    
    @property
    def json(self):
        content_str = self.get("content", None)
        if content_str:
            try:
                content_json = _json.loads(content_str)
                return content_json
            except:
                return None
    
    @property
    def headers(self):
        return _copy.deepcopy(self.get("headers", None))

class HTTPClient(object):

    def __init__(
        self,
        proxy=None,
        session=None,
        timeout=80,
        verify_ssl=True,
        **kwargs
    ):
        # type: (str, str, str or dict, _requests.Session, int, bool) -> HTTPClient
        self._proxy = None
        self._session = session
        self._timeout = timeout
        self._verify_ssl = verify_ssl
        self._kwargs = _copy.deepcopy(kwargs)

        if proxy:

            if isinstance(proxy, str):
                proxy = { "http": proxy, "https": proxy }

            if not isinstance(proxy, dict):
                raise ValueError(
                    """
                    The `proxy` parameter must either be `None`, a string
                    representing the URL of a proxy for both HTTP + HTTPS,
                    or a dictionary with a different URL for `"http"` and
                    `"https"`.
                    """
                )
            
            self._proxy = _copy.deepcopy(proxy)

        self._local_thread = _threading.local()
    
    def _get_session(self):
        # type: None -> _threading.local
        """
        Return or establish the session associated with the current thread.
        """
        # Store whatever session we use in the local thread storage
        if getattr(self._local_thread, "session", None) is None:
            self._local_thread.session = self._session or _requests.Session()

        return self._local_thread.session
    
    @_logging.log_call
    def request(self, url, method="GET", headers=None, data=None, **kwargs):
        
        extra_kwargs = {}

        # Calculate extra keyword arguments
        kwargs["verify"] = self._verify_ssl
        kwargs["proxies"] = self._proxy

        # Provided arguments override the calculated ones
        extra_kwargs.update(self._kwargs)
        extra_kwargs.update(kwargs)

        session = self._get_session()
        resp_dict = {}

        try:
            
            ret = None
            try:
                ret = session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    **extra_kwargs,
                )
            except TypeError as e:
                raise TypeError(
                    """
                    The `requests` library is not functioning as expected.
                    This could be that the version that is available is not
                    updated. You can try updating your version:
                        pip install --user --upgrade --force-reinstall requests
                    or, if you are using `pipenv`:
                        pipenv update requests
                    The original error was:
                        {e}
                    """.format(e=e)
                )

            content = ret.content
            if content:
                if type(content) is bytes:
                    content = content.decode("utf8")

            resp_dict["content"] = content
            resp_dict["status_code"] = ret.status_code
            resp_dict["headers"] = _copy.deepcopy(dict(ret.headers))

        except Exception as e:

            self._handle_request_error(e)

        return HTTPResponse(data=resp_dict)

    def _handle_request_error(self, e):
        raise e

    def close(self):
        # type: None -> None
        session = self._get_session()
        if session:
            session.close()
            s = _requests.Session()
