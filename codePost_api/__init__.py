import codePost_api.util as util

from codePost_api.helpers import *
from codePost_api.upload import *
from codePost_api.errors import *

from codePost_api.util import configure_api_key, validate_api_key

# Try to automatically detect the API key from the environment.
configure_api_key()
