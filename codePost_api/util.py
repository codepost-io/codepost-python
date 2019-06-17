#!/usr/bin/env python3
##########################################################################
# Utility library
#
# DATE:    2019-06-16
# AUTHOR:  codePost (team@codepost.io)
# COMMENT: This was originally written for the Heatmap visualization tool.
#
# Following PEP8 guidelines for naming conventions, i.e.:
# - https://www.python.org/dev/peps/pep-0008/#class-names
# - https://www.python.org/dev/peps/pep-0008/#function-and-variable-names
# - https://www.python.org/dev/peps/pep-0484/#suggested-syntax-for-python-2-7-and-straddling-code
##########################################################################

from __future__ import print_function # Python 2

#####################
# Python dependencies
#
import copy as _copy
import functools as _functools
import json as _json
import logging as _logging
import os as _os
import time as _time
#
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

#######################
# External dependencies
#
import requests as _requests
from yaml import load as _load_yaml
try:
    from yaml import CLoader as _YamlLoader
except ImportError: # pragma: no cover
    from yaml import Loader as _YamlLoader
#
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

#########################################################################


API_KEY = None
_API_KEY_OVERRIDE = None

SETTINGS_URL = "https://codepost.io/settings"

BASE_URL = "https://api.codepost.io/"
DEFAULT_API_KEY_VARNAME = "CP_API_KEY"
DEFAULT_CONFIG_PATHS = [
    "codepost-config.yaml",
    ".codepost-config.yaml",
    "~/codepost-config.yaml",
    "~/.codepost-config.yaml",
    "../codepost-config.yaml",
    "../.codepost-config.yaml",
]

#########################################################################

# Will contain a list of all the loggers we have configured
# (to avoid configuring them multiple times, which will result in
# echoed statements in the logger)
_configured_loggers = []

class _Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class SimpleColorFormatter(_logging.Formatter):
    _title = {
        "DEBUG": "{END}[{BOLD}DBUG{END}]{END}".format(**_Color.__dict__),
        "INFO": "{END}[{BOLD}{GREEN}INFO{END}]{END}".format(**_Color.__dict__),
        "ERROR": "{END}[{BOLD}{RED}ERR {END}]{END}".format(**_Color.__dict__),
        "WARNING": "{END}[{BOLD}{BLUE}WARN{END}]{END}".format(**_Color.__dict__)
    }

    def normalizePath(self, path):
        abs_path = _os.path.abspath(path)
        pwd_path = _os.getcwd()
        return abs_path.replace(pwd_path, ".", 1)

    def formatMessage(self, msg):
        # type: (_logging.LogRecord) -> str
        header = self._title.get(msg.levelname, self._title.get("INFO"))
        return("{} {} (\"{}\", line {}): {}".format(
            header,
            msg.module,
            self.normalizePath(msg.filename),
            msg.lineno,
            msg.message
        ))

def _setup_logging(name=None, level="INFO"):
    # type: (str, str) -> Logger

    logger = _logging.getLogger(name)

    # Check if we have already configured this logger.
    if not name in _configured_loggers:

        # Add the color handler to the terminal output
        handler = _logging.StreamHandler()
        formatter = SimpleColorFormatter()
        handler.setFormatter(formatter)

        # Add the color handler to the logger
        logger.addHandler(handler)

        # Set logging level
        logger.setLevel(_os.environ.get("LOGLEVEL", level))

        # Remember we configured this logger
        _configured_loggers.append(name)

    return logger

_logger = _setup_logging("codePost-api.util")

def get_logger(name=None):
    # type: (str) -> None
    if name == None or name == "":
        return _logger
    else:
        return _setup_logging(name)

#########################################################################


def _is_stringable(obj):
    try:
        str(obj)
    except:
        return False
    return True

def validate_api_key(api_key, log_outcome=False, caption=""):
    # type: (str) -> bool
    """
    Checks whether a provided codePost API key is valid.
    """
    
    # Used for reporting
    api_key_str = "N/A"
    if _is_stringable(api_key):
        api_key_str = str(api_key)

    def invalid_api_key():
        """
        Helper method to return `False` and possibly log a warning.
        """
        if log_outcome:

            _logger.warning(
                "API_KEY '{:.5}...' {}seems invalid.".format(
                    api_key_str,
                    caption
                ))
        return False
    
    ######################################################################
    # HEURISTICS:
    # Trying to reject the candidate key without making an HTTP request.
    ######################################################################

    # Some guesses can easily be rejected
    if api_key == None or api_key == "":
        return invalid_api_key()
    
    # If it's not a string...
    try:
        api_key = str(api_key)
    except:
        return invalid_api_key()
    
    # If it's too short...
    if len(api_key) < 5:
        return invalid_api_key()

    # Actually, in our current implementation, we use tokens generated by
    # the DRF (https://github.com/encode/django-rest-framework/blob/809a6acd36b53017a8a41a1d46c816f0480cb20b/rest_framework/authtoken/models.py#L9)
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
        
        return True

    except:
        _logger.debug(
            "Unexpected error while validating an API_KEY '{:.5}...'.".format(
                api_key_str
            ))
    
    return invalid_api_key()

def configure_api_key(api_key=None, override=True):
    # type: (str, bool) -> str
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
    global API_KEY, _API_KEY_OVERRIDE
    
    # Used for reporting
    api_key_str = "N/A"
    if _is_stringable(api_key):
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
            caption="provided as override ")

        _API_KEY_OVERRIDE = api_key
        return _API_KEY_OVERRIDE

    if _API_KEY_OVERRIDE != None and _API_KEY_OVERRIDE != "":

        _logger.debug(
            "API_KEY '{:.5}...' was provided previously as an override.".format(
                _API_KEY_OVERRIDE
            ))
        
        # Check validity of stored override key  
        validate_api_key(
            api_key=_API_KEY_OVERRIDE,
            log_outcome=True,
            caption="stored as override ")

        return _API_KEY_OVERRIDE

    # Hard-coded (or reconfigured) API_KEY

    if API_KEY != None and API_KEY != "":

        _logger.debug(
            "API_KEY detected in source code. Not overriding it.")
        
        # Check validity of hard-coded key  
        validate_api_key(
            api_key=API_KEY,
            log_outcome=True,
            caption="previously detected or hard-coded in the library ")

        return API_KEY
    
    # Environment variable API_KEY

    if _os.environ.get(DEFAULT_API_KEY_VARNAME, None) != None:

        API_KEY = _os.environ.get(DEFAULT_API_KEY_VARNAME)

        _logger.debug(
            ("API_KEY detected in environment " +
            "variable ({}): '{:.5}...'").format(
                DEFAULT_API_KEY_VARNAME,
                API_KEY
            ))
        
        # Check validity of environment provided key  
        validate_api_key(
            api_key=API_KEY,
            log_outcome=True,
            caption="obtained from environment variables ")
        
        return API_KEY

    # YAML configuration API_KEY

    location = None

    for config_path in DEFAULT_CONFIG_PATHS:
        config_path = _os.path.abspath(_os.path.expanduser(config_path))
        if _os.path.exists(config_path) and _os.path.isfile(config_path):
            location = config_path
            break
        else:
            _logger.debug(
                "No config file here: {}".format(
                    config_path))
    
    if location != None:
        _logger.debug("Configuration file detected: {}".format(location))

        config = None
        try:
            config = _load_yaml(open(location), Loader=_YamlLoader)
        except:
            config = None

        if config == None:
            _logger.debug(
                "Configuration file detected: "
                "Loading failed, no valid API_KEY.")
            return None
        
        if config.get("api_key", "") == "":
            _logger.debug(
                "Configuration file detected: "
                "Loading successful, but no valid API_KEY.")
            return None
        
        API_KEY = config.get("api_key")

        API_KEY_STR = "N/A"
        if _is_stringable(API_KEY):
            API_KEY_STR = str(API_KEY)

        _logger.debug(
            ("API_KEY detected in configuration file ({}): " +
            "'{:.5}...'").format(
                DEFAULT_API_KEY_VARNAME,
                API_KEY_STR
            ))
        
        # Check validity of environment provided key  
        validate_api_key(
            api_key=API_KEY,
            log_outcome=True,
            caption="obtained configuration file '{}' ".format(location))
        
        return API_KEY
    
    _logger.warning(
        ("API_KEY could not be detected. "
         "codePost API calls are expected to fail. "
         "You may retrieve your API key from {} "
         "and manually call `codePost_api.configure_api_key(api_key=...)`."
        ).format(SETTINGS_URL))
        
    return None
    
#########################################################################


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

#########################################################################
