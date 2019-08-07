# =============================================================================
# codePost v2.0 SDK
#
# ASSIGNMENT MODEL SUB-MODULE
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

from . import submissions as _submissions

# =============================================================================

@_six.add_metaclass(_abstract.APIResourceMetaclass)
class Assignments(
    _abstract.APIResource,
    _abstract.CreatableAPIResource,
    _abstract.ReadableAPIResource,
    _abstract.UpdatableAPIResource,
    _abstract.DeletableAPIResource,
):
    _OBJECT_NAME = "assignments"
    _FIELD_ID = "id"
    _FIELDS = {
        "name":             (str, "The name of the assignment."),
        "course":           (int, "The `Course` object which this assignment is a part of."),
        "points":           (int, "The total number of points possible in this assignment."),
        "isReleased":       (bool, ("If True, finalized submissions will be viewable by students. " +
                                    "See Who can view a submission? for more details.")),
        "rubricCategories": (_typing.List, "A list of RubricCategories, which constitute this assignment's rubric."),
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

    def list_submissions(self, id=None, student=None, grader=None):
        """
        Returns the list of submissions associated with an assignment, which
        optionally can be filtered according to a specific submitting `student`
        or a `grader`.
        """
        _class_type = type(self)

        id = self._get_id(id=id)

        endpoint = "{}/submissions".format(self.instance_endpoint_by_id(id=id))
        endpoint_params = {}

        if student != None:
            # Filter according to a specific student (will be URL-quoted later)
            endpoint_params["student"] = student

        if grader != None:
            # Filter according to a specific grader (will be URL-quoted later)
            endpoint_params["grader"] = grader

        if len(endpoint_params) > 0:
            endpoint += "?{}".format(_urlencode(endpoint_params))

        ret = self._requestor._request(
            endpoint=endpoint,
            method="GET",
        )
        if ret.status_code == 200:
            # Returns a list of all submissions
            return list(map(
                lambda kwargs: _submissions.Submissions(**kwargs),
                ret.json))

# =============================================================================
