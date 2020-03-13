# =============================================================================
# codePost v2.0 SDK
#
# TEST CASE MODEL SUB-MODULE
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
class TestCases(
    _abstract.APIResource,
    _abstract.CreatableAPIResource,
    _abstract.ReadableAPIResource,
    _abstract.UpdatableAPIResource,
    _abstract.DeletableAPIResource,
):
    # Avoid class being mistaken as a test by pytest
    # (see: https://github.com/pytest-dev/pytest/issues/1879)
    __test__ = False

    _OBJECT_NAME = "testCases"
    _FIELD_ID = "id"
    _FIELDS = {
        'testCategory': (int, 'The test category this Test Case corresponds to.'),
        'type': (str,"An enum describing the type of test defined in this Test Case. 'external' is used for Test Cases run somewhere other than codePost"),
        'description': (str,"A test description of the Test Case used as a title."),
        "sortKey": (int, "Key that defines how Test Cases are sorted within the codePost UI."),
        "pointsFail": (int, "Points added to a submission that fails this Test Case. Use a negative value to take off points."),
        "pointsPass": (int, "Points added to a submission that passes this Test Case."),
        "explanation": (str, "Text (accepts Markdown) shown to students when exposed tests are run in the Student Console, and from the Code Console"),
    }
    _FIELDS_READ_ONLY = [ ]
    _FIELDS_REQUIRED = [ "testCategory", "type", "description"]

# =============================================================================