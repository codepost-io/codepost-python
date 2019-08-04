# =============================================================================
# codePost v2.0 SDK
#
# SUBMISSION MODEL SUB-MODULE
# =============================================================================

from __future__ import print_function # Python 2

# Python stdlib imports
import typing as _typing

# Local imports
from . import abstract as _abstract

# =============================================================================

class Submissions(
    _abstract.APIResource,
    _abstract.CreatableAPIResource,
    _abstract.ReadableAPIResource,
    _abstract.UpdatableAPIResource,
    _abstract.DeletableAPIResource,
):
    __metaclass__ = _abstract.APIResourceMetaclass
    _OBJECT_NAME = "submissions"
    _FIELD_ID = "id"
    _FIELDS = {
        'assignment': (int, 'The assignment this submission corresponds to.'),
        'students': (_typing.List,
        "A list of the students who worked on this submission. A student can have at most one submission per assignment. These users must also be active students in the submission's course. Every submission must have at least 1 student."),
        'grader': (str,
        "The grader assigned to grade this submission, specified by email. This user must be an active grader in the submission's course. If submission.isFinalized == True, then this field cannot be null"),
        'isFinalized': (bool,
        'If True, the submission will be visible by students if the associated assignment is published. For more information, see Who can view a submission?.'),
        'queueOrderKey': (int,
        'Index used to order the queue from which graders draw submissions. Low keys will be drawn from the queue first.'),
        'dateEdited': (str,
        "The time when this object was last edited. Edits include changes to the submission's fields and any updates or additions to child objects (such as a File or Comment)."),
        'grade': (int,
        'Integer value specifying the number of points earned by the submission, accounting for all linked Comments and Rubric Comments. This field is calculated by the codePost API whenever the submission is finalized.'),
        'files': (_typing.List, "A list of the submission's file IDs.")
    }
    _FIELDS_READ_ONLY = [ "dateEdited", "grade", "files" ]
    _FIELDS_REQUIRED = [ "assignment", "students" ]
    _FIELDS_RELATED_OBJECTS ={ "files" : "file" }

    def get_files(self):
        return self._retrieve_related_objects('files')

    def get_file_by_name(self, file_name):
        return filter(lambda s: s.name == file_name, self.get_files())

# =============================================================================
