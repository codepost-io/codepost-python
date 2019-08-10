# =============================================================================
# codePost v2.0 SDK
#
# FILE MODEL SUB-MODULE
# =============================================================================

from __future__ import print_function # Python 2

# Python stdlib imports
import typing as _typing

# External dependencies
import six as _six

# Local imports
from . import abstract as _abstract

from . import comments as _comments
#from . import submissions as _submissions

# =============================================================================

@_six.add_metaclass(_abstract.APIResourceMetaclass)
class Files(
    _abstract.APIResource,
    _abstract.CreatableAPIResource,
    _abstract.ReadableAPIResource,
    _abstract.UpdatableAPIResource,
    _abstract.DeletableAPIResource,
):
    _OBJECT_NAME = "files"
    _FIELD_ID = "id"
    _FIELDS = {
        'name': (str, 'The name of the file.'),
        'code': (str,
        'The contents of the file. Accepts unicode-encoded strings, and will render newlines.'),
        'extension': (str,
        "The file extension. This field determines how the File's code will be syntax-highlighted."),
        'submission': (int, "The ID of the file's parent Submission."),
        'comments': (_typing.List[_comments.Comments], 'The IDs of all comments applied to this file.')
    }
    _FIELDS_READ_ONLY = [ "dateEdited", "grade", "files" ]
    _FIELDS_REQUIRED = [ "name", "code", "extension", "submission" ]

# =============================================================================
