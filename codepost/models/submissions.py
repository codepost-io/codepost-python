# =============================================================================
# codePost v2.0 SDK
#
# SUBMISSION MODEL SUB-MODULE
# =============================================================================

from __future__ import print_function # Python 2

# Python stdlib imports
import typing as _typing
try:
    # Python 3
    from urllib.parse import urljoin as _urljoin
    from urllib.parse import urlencode as _urlencode
except ImportError: # pragma: no cover
    # Python 2
    from urlparse import urljoin as _urljoin
    from urllib import urlencode as _urlencode

# External dependencies
import six as _six

# Local imports
from . import abstract as _abstract

#from . import assignments as _assignments
from . import files as _files
from . import submission_tests as _submission_tests

# =============================================================================

@_six.add_metaclass(_abstract.APIResourceMetaclass)
class Submissions(
    _abstract.APIResource,
    _abstract.CreatableAPIResource,
    _abstract.ReadableAPIResource,
    _abstract.UpdatableAPIResource,
    _abstract.DeletableAPIResource,
):
    _OBJECT_NAME = "submissions"
    _FIELD_ID = "id"

    # FIXME: automate the "created" and "modified" attributes
    # NOTE: when adding fields to this list make sure that the REQUIRED fields are first listed
    _FIELDS = {
        'assignment': (int, 'The assignment this submission corresponds to.'),
        'students': (_typing.List[str],
        "A list of the students who worked on this submission. A student can have at most one submission per assignment. These users must also be active students in the submission's course. Every submission must have at least 1 student."),
        'grader': (str,
        "The grader assigned to grade this submission, specified by email. This user must be an active grader in the submission's course. If submission.isFinalized == True, then this field cannot be null"),
        'isFinalized': (bool,
        'If True, the submission will be visible by students if the associated assignment is published. For more information, see Who can view a submission?.'),
        'queueOrderKey': (int,
        'Index used to order the queue from which graders draw submissions. Low keys will be drawn from the queue first.'),
        'dateEdited': (str,
        "The time when this object was last edited. Edits include changes to the submission's fields and any updates or additions to child objects (such as a File or Comment)."),
        'dateUploaded': (str, "The timestamp of when this submission was uploaded. This can be modified programmatically and is the basis for late day calculations."),
        'grade': (int,
        'Integer value specifying the number of points earned by the submission, accounting for all linked Comments and Rubric Comments. This field is calculated by the codePost API whenever the submission is finalized.'),
        'files': (_typing.List[_files.Files], "A list of the submission's Files."),
        'tests': (_typing.List[_submission_tests.SubmissionTests], "A list of the submission's Submission Tests."),

        'created': (str, "Automatic timestamp for creation of database object."),
        'modified': (str, "Automatic timestamp for modification of database object."),
    }
    _FIELDS_READ_ONLY = [ "dateEdited", "grade", "files", 'tests' ]
    _FIELDS_REQUIRED = [ "assignment", "students" ]

    def list_view_history(self, id=None, return_all=False):
        """
        Returns the list of view histories associated with the submission.
        """
        _class_type = type(self)

        id = self._get_id(id=id)

        endpoint = "/submissions/{}/history".format(id)
        endpoint_params = {}

        if len(endpoint_params) > 0:
            endpoint += "?{}".format(_urlencode(endpoint_params))

        ret = self._requestor._request(
            endpoint=endpoint,
            method="GET",
        )
        if ret.status_code == 200:
            # Returns a list of all submission histories
            lst = ret.json

            # This list tends to only contain one history (bug!)
            if return_all:
                return lst

            if len(lst) > 0:
                # FIXME: sort to guarantee most recent view
                return lst[0]

        return dict()

# =============================================================================
