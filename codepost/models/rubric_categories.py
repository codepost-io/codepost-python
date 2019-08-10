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

#from . import assignments as _assignments
from . import rubric_comments as _rubric_comments

# =============================================================================

@_six.add_metaclass(_abstract.APIResourceMetaclass)
class RubricCategories(
    _abstract.APIResource,
    _abstract.CreatableAPIResource,
    _abstract.ReadableAPIResource,
    _abstract.UpdatableAPIResource,
    _abstract.DeletableAPIResource,
):
    _OBJECT_NAME = "rubricCategories"
    _FIELD_ID = "id"
    _FIELDS = {
        'name': (str, 'The name of the rubric category.'),
        'assignment': (int,
        'ID of the Assignment to which this Rubric Category belongs.'),
        'pointLimit': (int,
        'The maximum number of points which can be deducted by Comments linked to Rubric Comments from this Rubric Category, per Submission. A negative number indicates a maximum number of points which can be added. A pointLimit of 0 indicates that no points can be added or deducted; a pointLimit of null indicates no cap.'),
        'rubricComments': (_typing.List[_rubric_comments.RubricComments],
        'The Rubric Comments that belong to this rubric category.'),
        'sortKey': (int,
        'The key which determines the order in which all rubric categories are presented in the codePost UI. Low keys are shown first.'),
        'helpText': (str,
        'Text shown next to this rubric category to users in the Code Review Console. Use this space to provide additional instructions to graders.')
    }
    _FIELDS_READ_ONLY = [ "rubricComments" ]
    _FIELDS_REQUIRED = [ "name", "assignment" ]

# =============================================================================
