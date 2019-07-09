# =============================================================================
# codePost v2.0 SDK
#
# ASSIGNMENT MODEL SUB-MODULE
# =============================================================================

from __future__ import print_function # Python 2

# Python stdlib imports
import typing as _typing

# Local imports
from . import abstract as _abstract

# =============================================================================

class Assignments(
    _abstract.APIResource,
    _abstract.CreatableAPIResource,
    _abstract.ReadableAPIResource,
    _abstract.UpdatableAPIResource,
    _abstract.DeletableAPIResource,
    metaclass=_abstract.APIResourceMetaclass
):
    _OBJECT_NAME = "assignments"
    _FIELD_ID = "id"
    _FIELDS = {
        "name":             (str, "The name of the assignment."),
        "course":           (int, "The `Course` object which this assignment is a part of."),
        "points":           (int, "The total number of points possible in this assignment."),
        "isReleased":       (bool, ("If True, finalized submissions will be viewable by students. " +
                                    "See Who can view a submission? for more details.")),
        "rubricCategories": (object, "A list of RubricCategories, which constitute this assignment's rubric."),
        "sortKey":          (int, "Key that defines how Assignments are sorted within the codePost UI."),
        "hideGrades":       (bool, ("An Assignment setting. " +
                                    "If True, students won't be able to view their submission grades for " +
                                    "this assignment.")),
        "anonymousGrading": (bool, ("An Assignment setting. " +
                                    "If True, Anonymous Grading Mode will be enabled for this assignment.")),
        "mean":             (int, ("The mean grade calculated over finalized submissions for this assignment. " +
                                   "null if no submissions have been finalized.")),
        "median":           (int, ("The median grade calculated over finalized submissions for this assignment. " +
                                   "null if no submissions have been finalized.")),
    }
    _FIELDS_READ_ONLY = [ "rubricCategories", "mean", "median" ]
    _FIELDS_REQUIRED = [ "name", "points", "course" ]

# =============================================================================
