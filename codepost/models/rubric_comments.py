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

# =============================================================================

@_six.add_metaclass(_abstract.APIResourceMetaclass)
class RubricComments(
    _abstract.APIResource,
    _abstract.CreatableAPIResource,
    _abstract.ReadableAPIResource,
    _abstract.UpdatableAPIResource,
    _abstract.DeletableAPIResource,
):
    _OBJECT_NAME = "rubricComments"
    _FIELD_ID = "id"
    _FIELDS = {
        'text': (str,
        'The text of the rubric category, visible to Course Admins, Graders, and any Students who receive a Comment linked to this rubric comment.'),
        'pointDelta': (int,
        'The amount deducted from submission.grade when this rubric comment is linked to a Comment (subject to category.pointLimit).'),
        'category': (int,
        'ID of the Rubric Category which this rubric comment is a part of.'),
        'sortKey': (int,
        'The key which determines how rubric comments are sorted within a Rubric Category in the codePost UI. Low keys are shown first.'),
        'explanation': (str,
        'Text (markdown) that, when defined, will be shown in place of rubricComment.text to students from the Code Console.'),
        'instructionText': (str, 'Text (markdown) that, when a grader applies this comment, will be shown in the customization bubble.'),
        'templateTextOn': (bool, 'Flag that indicates whether the instruction should be used as a template.'),
        'name': (str, 'Internal name, for instance to track occurrences of comments across assignments.'),
    }
    _FIELDS_READ_ONLY = [ "comments" ]
    _FIELDS_REQUIRED = [ "text", "pointDelta", "category" ]

# =============================================================================
