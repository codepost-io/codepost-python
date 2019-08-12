# =============================================================================
# codePost v2.0 SDK
#
# COMMENT MODEL SUB-MODULE
# =============================================================================

from __future__ import print_function # Python 2

# Python stdlib imports
import typing as _typing

# External dependencies
import six as _six

# Local imports
from . import abstract as _abstract
#from . import files as _files
#from . import rubric_comments as _rubric_comments

# =============================================================================

@_six.add_metaclass(_abstract.APIResourceMetaclass)
class Comments(
    _abstract.APIResource,
    _abstract.CreatableAPIResource,
    _abstract.ReadableAPIResource,
    _abstract.UpdatableAPIResource,
    _abstract.DeletableAPIResource,
):
    _OBJECT_NAME = "comments"
    _FIELD_ID = "id"
    _FIELDS = {
        'text': (str,
        'The text of the comment. This text will be shown to both graders and students.'),
        'startChar': (int,
        "The index of the character on which the comment begins. The index is relative to the beginning of the character's line. Must be greater than or equal to 0. If startLine == endLine, cannot be greater than endChar."),
        'endChar': (int,
        "The index of the character on which the comment ends. The index is relative to the beginning of the character's line. Must be greater than or equal to 0. If startLine == endLine, cannot be less than endChar."),
        'startLine': (int,
        "The line of the parent File's code on which the comment should begin. Must be greater than or equal to 0, and cannot be greater than endLine."),
        'endLine': (int,
        "The line of the parent File's code on which the comment should end. Must be greater than or equal to 0, cannot be less than startLine, and cannot exceed the number of lines in the file."),
        'pointDelta': (int,
        "The delta the comment will apply to its ancestor submission's grade. A positive value indicates a deduction, while a negative value indicates an addition. null indicates a value of 0."),
        'file': (int, 'The ID of the file to which this Comment applies.'),
        'rubricComment': (int,
        "The ID of a linked RubricComment. This field should be null if the comment isn't linked to any RubricComment."),
        'author': (str, 'The user who created this Comment.')
    }
    _FIELDS_READ_ONLY = []
    _FIELDS_REQUIRED = [
        "text",
        "startChar", "endChar",
        "startLine", "endLine"
    ]

# =============================================================================
