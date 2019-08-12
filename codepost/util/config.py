# =============================================================================
# codePost v2.0 SDK
#
# CONFIG SUB-MODULE
# =============================================================================

from __future__ import print_function # Python 2

# Python stdlib imports
import copy as _copy
import functools as _functools
import inspect as _inspect
import json as _json
import logging as _logging
import os as _os
import time as _time
import typing as _typing
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
from yaml import load as _load_yaml
try:
    from yaml import CLoader as _YamlLoader
except ImportError: # pragma: no cover
    from yaml import Loader as _YamlLoader
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

# Local imports
from . import helpers as _util

from . import custom_logging as _logging

from .misc import _make_f

# =============================================================================

# Global submodule constants
_LOG_SCOPE = "{}".format(__name__)

SETTINGS_URL = "https://codepost.io/settings"
BASE_URL = "https://api.codepost.io/"
DEFAULT_API_KEY_ENV = "CP_API_KEY"
DEFAULT_CONFIG_PATHS = [
    "codepost-config.yaml",
    ".codepost-config.yaml",
    "~/codepost-config.yaml",
    "~/.codepost-config.yaml",
    "../codepost-config.yaml",
    "../.codepost-config.yaml",
]

# Global submodule protected attributes
_logger = _logging.get_logger(name=_LOG_SCOPE)
_api_key = None
_api_key_override = None
_checked_api_keys = {}

# =============================================================================

# Replacement f"..." compatible with Python 2 and 3
_f = _make_f(globals=lambda: globals(), locals=lambda: locals())

_MSG_API_KEY_HELP = _f("""
=> Without a valid API key, codePost API calls are expected to fail.

=> The codePost SDK searches for a valid API key in the following:
    1. provided as a parameter of methods, through `api_key`;
    2. previously detected or (for testing purposes) hard-coded in the SDK;
    3. as an environment variable (typically `CP_API_KEY`);
    4. within a YAML configuration file (typically `.codepost-config.yaml`).

=> You can obtain your API key by accessing your Settings page while logged
   into codePost:
        {SETTINGS_URL}
   and manually call `codePost_api.configure_api_key(api_key=...)` from your
   Python code.

Feel free to contact api@codepost.io for more assistance.
""")

_MSG_API_KEY_INVALID = _f("""
API key "{{api_key}}"{{caption}} seems invalid.
{_MSG_API_KEY_HELP}
""")

_MSG_API_KEY_NOT_FOUND = _f("""
API key could not be detected.
{_MSG_API_KEY_HELP}
""")

# =============================================================================

def find_config_file(search_paths=None):
    # type: (_typing.List[str]) -> _typing.Optional[str]
    """
    Searches through the provided `search_paths` for the first existing file
    that is found. Typical names for the configuration file include:
    `codepost-config.yml` and `.codepost-config.yml` in the working directory.

    :param search_paths: The search paths. If not provided, the function will
        use the `DEFAULT_CONFIG_PATHS` constant.

    :return: The path of a configuration file if one is found; `None` otherwise
    """

    location = None

    # By default, use DEFAULT_CONFIG_PATHS
    if search_paths is None:
        search_paths = DEFAULT_CONFIG_PATHS

    _logger.debug(
        "Search for configuration file among: {}".format(search_paths))

    for config_path in search_paths:

        # Expand home directory ~ and make path absolute if relative
        config_path = _os.path.abspath(_os.path.expanduser(config_path))

        # Check whether there is a file at that location
        if _os.path.exists(config_path) and _os.path.isfile(config_path):

            location = config_path
            _logger.debug("Configuration found: {}".format(config_path))
            break

        else:
            _logger.debug("No config file here: {}".format(config_path))

    return location

def read_config_file(search_paths=None):
    # type: (_typing.List[str]) -> _typing.Optional[dict]
    """
    Loads and returns a configuration file if a valid one can be found; `None`
    otherwise.

    :param search_paths: The search paths. If not provided, the function will
        use the `DEFAULT_CONFIG_PATHS` constant.

    :return: A dictionary containing the configuration settings, if a valid
        configuration has been found; `None` otherwise.
    """
    config_path = find_config_file(search_paths=search_paths)

    if config_path is not None:

        config = None
        try:
            config = _load_yaml(open(config_path), Loader=_YamlLoader)
        except:
            _logger.debug(
                "Error reading configuration file: {}".format(config_path))

            config = None

        return config

# =============================================================================

@_logging.log_call
def validate_api_key(api_key, log_outcome=False, caption="", refresh=False):
    # type: (str, bool, str, bool) -> bool
    """
    Checks whether a provided codePost API key is valid.
    """
    global _checked_api_keys

    def invalid_api_key():
        """
        Helper method to return `False` and possibly log a warning.
        """
        global _checked_api_keys

        # Add to cache as failure
        if not _util.is_stringable(api_key):
            if not api_key in _checked_api_keys:
                _checked_api_keys[api_key] = False

        # Log failure
        if log_outcome:
            _logger.warning(
                _MSG_API_KEY_INVALID.format(
                    api_key=_util.robust_str(obj=api_key),
                    caption=caption,
                ))

        _logging.fail_action(
            "Failed validation of API KEY '{}'{}.".format(
                _util.robust_str(obj=api_key), caption))

        return False

    ######################################################################
    # CACHE:
    # Save previously computed results to avoid going through the same
    # checks multiple time within the execution of the same script.
    ######################################################################

    if api_key in _checked_api_keys:
        if refresh:
            if log_outcome:
                _logger.debug(
                    """
                    API_KEY '{:.5}...'{} found in cache => PURGING
                    """.format(
                    _util.robust_str(obj=api_key),
                    caption
                ))

            del _checked_api_keys[api_key]

        else:
            if log_outcome:
                _logger.debug(
                    """
                    API_KEY '{:.5}...'{} found in cache.
                    """.format(
                    _util.robust_str(obj=api_key),
                    caption
                ))

            if _checked_api_keys[api_key]:
                return True

            else:
                return invalid_api_key()

    ######################################################################
    # HEURISTICS:
    # Trying to reject the candidate key without making an HTTP request.
    ######################################################################

    # Some guesses can easily be rejected

    if api_key == None or api_key == "":
        return invalid_api_key()

    # If it's not a string...

    if not _util.is_stringable(api_key):
        return invalid_api_key()

    # If it's too short...

    if len(api_key) < 5:
        return invalid_api_key()

    # In our current implementation, we use tokens generated by the DRF
    # (see https://git.io/fjKgC)

    if len(api_key) != 40:
        return invalid_api_key()

    ######################################################################
    # HTTP REQUEST
    ######################################################################

    try:
        auth_headers = {"Authorization": "Token {}".format(api_key)}

        r = _requests.get(
            "{}/courses/".format(BASE_URL),
            headers=auth_headers
        )

        # This API endpoint will return HTTP 401 if the authorization
        # token is invalid. Other codes will have other meanings.

        if r.status_code == 401:
            return invalid_api_key()

        # Add to cache as success

        _checked_api_keys[api_key] = True

        return True

    except:
        _logger.debug(
            "Unexpected error while validating an API_KEY '{:.5}...'.".format(
                _util.robust_str(obj=api_key)
            ))

    return invalid_api_key()

# =============================================================================

@_logging.log_call
def configure_api_key(api_key=None, override=True, log_outcome=True):
    # type: (str, bool, bool) -> str
    """
    Configures the API key to authenticate with the codePost API, by
    looking at the following sources:
    - provided as a parameter, through `api_key`;
    - hard-coded within library (for testing purposes);
    - as an environment variable (typically `CP_API_KEY`);
    - within a YAML configuration file.

    When provided with an override `api_key` parameter, this method will
    store the key in memory for future calls.

    It is also possible to call the method with `override` set to
    `False`, to only use the override API key in case one cannot be
    found in the environment.
    """
    global _api_key, _api_key_override

    # Used for reporting
    api_key_str = "N/A"
    if _util.is_stringable(api_key):
        api_key_str = str(api_key)

    # Override API_KEY by argument

    if override and api_key != None and api_key != "":

        _logger.debug(
            "API_KEY '{:.5}...' provided as override.".format(
                api_key_str
            ))

        # Check validity of provided override key
        validate_api_key(
            api_key=api_key,
            log_outcome=True,
            caption=" provided as override")

        _api_key_override = api_key
        return _api_key_override

    if _api_key_override != None and _api_key_override != "":

        _logger.debug(
            "API_KEY '{:.5}...' was provided previously as an override.".format(
                _api_key_override
            ))

        # Check validity of stored override key
        validate_api_key(
            api_key=_api_key_override,
            log_outcome=True,
            caption=" stored as override")

        return _api_key_override

    # Hard-coded (or reconfigured) API_KEY

    if _api_key != None and _api_key != "":

        _logger.debug(
            """
            API_KEY detected in source code or module memory.
            Not overriding it.
            """)

        # Check validity of hard-coded key
        validate_api_key(
            api_key=_api_key,
            log_outcome=True,
            caption=" previously detected or hard-coded in the library")

        return _api_key

    # Environment variable API_KEY

    if _os.environ.get(DEFAULT_API_KEY_ENV, None) != None:

        _api_key = _os.environ.get(DEFAULT_API_KEY_ENV)

        _logger.debug(
            ("API_KEY detected in environment " +
            "variable ({}): '{:.5}...'").format(
                DEFAULT_API_KEY_ENV,
                _api_key
            ))

        # Check validity of environment provided key
        validate_api_key(
            api_key=_api_key,
            log_outcome=True,
            caption=" obtained from an environment variable")

        return _api_key

    # YAML configuration API_KEY

    location = find_config_file()
    config = read_config_file()

    if config is not None:

        if config.get("api_key", "") == "":
            _logger.debug(
                "Configuration file detected: "
                "Loading successful, but no valid API_KEY.")

            if config.get("api-key", "") != "":
                _logger.debug(
                    "The configuration file may be using the "
                    "key name 'api-key' instead of 'api_key'."
                )

            return None

        _api_key = config.get("api_key")

        _logger.debug(
            ("API_KEY detected in configuration file ({}): " +
            "'{:.5}...'").format(
                DEFAULT_API_KEY_ENV,
                _util.robust_str(_api_key)
            ))

        # Check validity of environment provided key
        validate_api_key(
            api_key=_api_key,
            log_outcome=True,
            caption=" obtained config file '{}'".format(location))

        return _api_key

    if log_outcome:
        _logger.warning(_MSG_API_KEY_NOT_FOUND)
    
    _logging.current_action().finish(exception=RuntimeWarning("No API key"))

    return None

# =============================================================================

class api_key_decorator(object):
    """
    Decorator which injects an API key in calling parameters of methods
    that expect an API key.
    """

    def __init__(self, override_api_key=True):
        self._override_api_key = override_api_key

    def __call__(self, target_function):

        @_functools.wraps(target_function)
        def _wrapper(*args, **kwargs):
            global _checked_api_keys

            api_key = None

            # See what the user has provided, if anything
            candidate_api_key = kwargs.get("api_key", None)

            # Check if this candidate should override any more
            # sophisticated guess that we could make (because the
            # `api_key_override` is unique to the decorator, it is deleted
            # from the `kwargs` before being passed to the `targetfunc`.)

            override_api_key = self._override_api_key
            if "override_api_key" in kwargs:
                override_api_key = kwargs["api_key_override"]
                del kwargs["api_key_override"]

            if override_api_key and candidate_api_key:
                api_key = candidate_api_key

            else:

                # Check whether the user-provided API Key
                if candidate_api_key:

                    if not candidate_api_key in _checked_api_keys:
                        _checked_api_keys[candidate_api_key] = \
                            validate_api_key(api_key=candidate_api_key)

                    if _checked_api_keys[candidate_api_key]:
                        api_key = candidate_api_key

                # Check automatic configuration (only if candidate did not
                # seem to pan out)
                if not api_key:
                    api_key = configure_api_key()
                    if api_key:
                        _checked_api_keys[api_key] = \
                            validate_api_key(api_key=api_key)

                # Override the parameter `api_key` before calling method
                kwargs["api_key"] = api_key

            # Call target function
            filtered_kwargs = _util.filter_kwargs_for_function(
                func=target_function,
                kwargs=kwargs)

            return target_function(*args, **filtered_kwargs)

        return _wrapper

# =============================================================================


