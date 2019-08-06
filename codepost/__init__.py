"""
codePost v2.0 SDK.

Provides a convenient Python interface to the codePost API. Start scripting!

   Name: codepost
 Author: codePost Team
  Email: team@codepost.io
    URL: github.com/codepost-io/codepost-python
License: Copyright (c) 2019 codePost, licensed under the MIT license
"""

# Documentation

__version__ = "0.1.1"

# Import sub-modules

from . import util
from .util.config import configure_api_key

# Configure credentials

util.config.configure_api_key(log_outcome=False)

# Configuration module variables

app_info = None

# Sets some basic information about the running application that's sent along
# with API requests. Useful for plugin authors to identify their plugin when
# communicating with Stripe.
#
# Takes a name and optional version and plugin URL.

def set_app_info(name, url=None, version=None):
    """
    Configure the library with information about the running application,
    which will be sent along with API requests. This is useful for developers
    to identify their scripts and plugins when communicating with the codePost
    team.
    """
    global app_info

    app_info = dict()
    
    app_info["name"] = name
    if url:
        app_info["url"] = url
    if version:
        app_info["version"] = version

# Reimport all instantiated helper static classes
from .instantiated import *
