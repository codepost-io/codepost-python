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

class Courses(
    _abstract.APIResource,
    _abstract.ReadableAPIResource,
    _abstract.UpdatableAPIResource,
    metaclass=_abstract.APIResourceMetaclass
):
    _OBJECT_NAME = "courses"
    _FIELD_ID = "id"
    _FIELDS = {
        "name":                         (str, "The course's name (e.g. 'CS 101')."),
        "period":                       (str, "The course's period (e.g. 'Fall 2019'). This field allows you to create multiple objects which represent instances of the same course over different periods (e.g. every semester)."),
        "assignments":                  (_typing.List, "IDs of the Assignments in this course."),
        "sections":                     (_typing.List, "IDs of the Sections in this course."),
        "sendReleasedSubmissionsToBack":(bool, "A course setting. If True, submissions released by graders will be sent to the back of the grading queue. This ensures that released submissions will be re-claimed only after all other Submissions have been claimed."),
        "showStudentsStatistics":       (bool, "A course setting. If True, students will be able to view the Mean and Median of this Course's published Assignments."),
        "timezone":                     (str, "A course setting. Must be a valid pytz timezone."),
        "emailNewUsers":                (bool, "A course setting. If True, users of any role added to this Course's roster will be sent a notification email."),
        "anonymousGradingDefault":      (bool, "A course setting. If True, newly created assignments will automatically be set to Anonymous Grading Mode."),
        "allowGradersToEditRubric":     (bool, "A course setting. If True, graders and course admins will be able to edit an Assignment's directly rubric from the Code Review console."),
    }
    _FIELDS_READ_ONLY = [ ]
    _FIELDS_REQUIRED = [ "name", "period" ]

# =============================================================================
