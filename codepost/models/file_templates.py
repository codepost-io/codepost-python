# =============================================================================
# codePost v2.0 SDK
#
# FILE TEMPLATE MODEL SUB-MODULE
# =============================================================================

from __future__ import print_function # Python 2

# Python stdlib imports
import typing as _typing

# External dependencies
import six as _six

# Local imports
from . import abstract as _abstract

# =============================================================================

@_six.add_metaclass(_abstract.APIResourceMetaclass)
class FileTemplates(
    _abstract.APIResource,
    _abstract.CreatableAPIResource,
    _abstract.ReadableAPIResource,
    _abstract.UpdatableAPIResource,
    _abstract.DeletableAPIResource,
):
    _OBJECT_NAME = "fileTemplates"
    _FIELD_ID = "id"
    _FIELDS = {
        'assignment': (int, 'The Assignment this File Template Test corresponds to.'),
        'name': (str, 'The name of the File Template.'),
        'extension': (str, 'The extension of the File Template.'),
        'code': (str, 'The code of the File Template. Used to de-emphasize template code in the Code Console.'),
        'path': (str, 'The path to the File Template'),
        "required": (bool, ("Whether a file with this name and path is required to be submitted by students.")),
    }
    _FIELDS_READ_ONLY = [ ]
    _FIELDS_REQUIRED = [ "assignment", "name", "extension" ]

# =============================================================================