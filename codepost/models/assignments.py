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

#from . import courses as _courses
from . import rubric_categories as _rubric_categories
from . import file_templates as _file_templates
from . import test_categories as _test_categories
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
        "rubricCategories": (_typing.List[_rubric_categories.RubricCategories], "A list of RubricCategories, which constitute this assignment's rubric."),
        "fileTemplates": (_typing.List[_file_templates.FileTemplates], "A list of FileTemplates belonging to this assignment."),
        "sortKey":          (int, "Key that defines how Assignments are sorted within the codePost UI."),
        "mean":             (int, ("The mean grade calculated over finalized submissions for this assignment. " +
                                   "null if no submissions have been finalized.")),
        "median":           (int, ("The median grade calculated over finalized submissions for this assignment. " +
                                   "null if no submissions have been finalized.")),

        ###################################################################################################
        # Autograder
        ###################################################################################################
        "testCategories":   (_typing.List[_test_categories.TestCategories], "A list of Test Categories belonging to this assignment."),
        "environment":      (int, ("The `Environment` object which this assignment is tied to, if the "
                                   "autograder has been enabled for this assignment.")),


        ###################################################################################################
        # Settings
        ###################################################################################################

        # Upload settings
        "allowStudentUpload": (bool, ("An Assignment setting. " +
                                    "If True, students will be able to submit submissions directly to codePost.")),
        "uploadDueDate": (str, ("A datetime representing the time at which students will no longer be able to submit submissions through codePost.")),
        "liveFeedbackMode": (bool, ("An Assignment setting. " +
                                    "If True, students will be able to view any uploaded submission (and all associated data).")),
        "allowLateUploads": (bool, ("An Assignment setting. " +
                                    "If True, students will be allowed to submit submissions to codePost after assignment.uploadDueDate has passed.")),

        # Grading settings
        "anonymousGrading": (bool, ("An Assignment setting. " +
                                    "If True, Anonymous Grading Mode will be enabled for this assignment.")),
        "additiveGrading": (bool, ("An Assignment setting. " +
                                    "If True, submission grades will start at 0 instead of assignment.points.")),
        "forcedRubricMode": (bool, ("An Assignment setting. " +
                                    "If True, graders will be prevented from saving comments which do not link to rubric comments.")),
        "collaborativeRubricMode": (bool, ("An Assignment setting. " +
                                    "If True, graders will be allowed to edit the assignment's rubric.")),
        "showFrequentlyUsedRubricComments": (bool, ("An Assignment setting. " +
                                    "If True, frequently used rubric comments will be shown in a special category in the Code Console.")),
        "templateMode": (bool, ("A boolean field. If True, admins will be able upload template code files. Those template files will be " +
                                "used to de-emphasize provided versus student-written code in submissions.")),

        # Publishing settings
        "allowRegradeRequests": (bool, ("An Assignment setting. " +
                                    "If True, students will be able to request regrades from codePost.")),
        "regradeDeadline": (str, ("A datetime representing the time at which students will no longer be able to submit regrade requests through codePost.")),
        "hideGrades":       (bool, ("An Assignment setting. " +
                                    "If True, students won't be able to view their submission grades for " +
                                    "this assignment.")),
        "hideGradersFromStudents": (bool, ("An Assignment setting. " +
                                    "If True, grader emails won't be revleaed to students.")),
        "commentFeedback": (bool, ("An Assignment setting. " +
                                    "If True, students will be able to provide feedback on rubric comments.")),
        ###################################################################################################
    }
    _FIELDS_READ_ONLY = [ "rubricCategories", "fileTemplates", "testCategories", "mean", "median", ]
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
