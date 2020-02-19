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

    # FIXME: automate the "created" and "modified" attributes
    # NOTE: when adding fields to this list make sure that the REQUIRED fields are first listed
    _FIELDS = {
        'name': (str, 'The name of the file.'),
        'code': (str,
        'The contents of the file. Accepts unicode-encoded strings, and will render newlines.'),
        'extension': (str,
        "The file extension. This field determines how the File's code will be syntax-highlighted."),
        'submission': (int, "The ID of the file's parent Submission."),
        'comments': (_typing.List[_comments.Comments], 'The IDs of all comments applied to this file.'),
        'path': (str, 'An optional file path to indicate a directory structure within a submission.'),

        'created': (str, "Automatic timestamp for creation of database object."),
        'modified': (str, "Automatic timestamp for modification of database object."),
    }
    _FIELDS_READ_ONLY = [ "comments", ]
    _FIELDS_REQUIRED = [ "name", "code", "extension", "submission" ]

# =============================================================================
