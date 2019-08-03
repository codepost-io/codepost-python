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

class CourseRosters(
    _abstract.APIResource,
    _abstract.ReadableAPIResource,
    _abstract.UpdatableAPIResource,
):
    __metaclass__ = _abstract.APIResourceMetaclass
    _OBJECT_NAME = "courses..roster"
    _FIELD_ID = "id"
    _FIELDS = {
        'students': (_typing.List, 'Must specify the entire list of students. This does not represent a list of students to enroll, but rather the entire list of active students in this course. Leaving an existing student out of this list will unenroll the student, placing them in course.inactive_students. Excluding this field will leave the students field unchanged.'),
        'graders': (_typing.List, 'Must specify the entire list of graders. This does not represent a list of graders to enroll, but rather the entire list of active graders in this course. Leaving an existing graders out of this list will unenroll the grader, placing them in course.inactive_graders Excluding this field will leave the graders field unchanged.'),
        'superGraders': (_typing.List, 'Like course.students, course.graders, and course.courseAdmins, this represents the complete list of graders with ViewAll privilege. Excluding this field will leave the superGraders field unchanged.'),
        'courseAdmins': (_typing.List, "Must specify the entire list of admins. This does not represent a list of admins to enroll, but rather the entire list of active admins in this course. Leaving an existing admin out of this list will unenroll the admin, placing them in course.inactive_admins. You cannot remove yourself as a Course Admin via the codePost API. If you'd like to do so, please ask another Course Admin to remove you. If you'd like to delete your course, please email us at team@codepost.io.")
    }
    _FIELDS_READ_ONLY = [ ]
    _FIELDS_REQUIRED = [ ]

# =============================================================================
