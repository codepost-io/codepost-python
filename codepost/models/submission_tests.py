# =============================================================================
# codePost v2.0 SDK
#
# SUBMISSION TEST MODEL SUB-MODULE
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
class SubmissionTests(
    _abstract.APIResource,
    _abstract.CreatableAPIResource,
    _abstract.ReadableAPIResource,
    _abstract.UpdatableAPIResource,
    _abstract.DeletableAPIResource,
):
    _OBJECT_NAME = "submissionTests"
    _FIELD_ID = "id"
    _FIELDS = {
        'submission': (int, 'The Submission this Submission Test corresponds to.'),
        'testCase': (int, 'The Test Case this Submission Test corresponds to.'),
        'logs': (str, "Any logs associated with this Submission Test."),
        "passed": (bool, ("Whether the test run represented by this Submission Test passed.")),
        "isError": (bool, ("Whether the test run represented by this Submission Test produced an error. Defaults to False.")),
    }
    _FIELDS_READ_ONLY = [ ]
    _FIELDS_REQUIRED = [ "submission", "testCase", "logs", "passed" ]

# =============================================================================