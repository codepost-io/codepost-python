# =============================================================================
# codePost v2.0 SDK
#
# TEST CATEGORY MODEL SUB-MODULE
# =============================================================================

from __future__ import print_function # Python 2

# Python stdlib imports
import typing as _typing

# External dependencies
import six as _six

# Local imports
from . import abstract as _abstract

#from . import assignments as _assignments
from . import test_cases as _test_cases

# =============================================================================

@_six.add_metaclass(_abstract.APIResourceMetaclass)
class TestCategories(
    _abstract.APIResource,
    _abstract.CreatableAPIResource,
    _abstract.ReadableAPIResource,
    _abstract.UpdatableAPIResource,
    _abstract.DeletableAPIResource,
):
    # Avoid class being mistaken as a test by pytest
    # (see: https://github.com/pytest-dev/pytest/issues/1879)
    __test__ = False

    _OBJECT_NAME = "testCategories"
    _FIELD_ID = "id"
    _FIELDS = {
        'assignment': (int, 'The assignment this Test Category corresponds to.'),
        'name': (str, "The name of the Test Category"),
        'testCases': (_typing.List[_test_cases.TestCases],'The Test Cases that belong to this Test Category.'),
    }
    _FIELDS_READ_ONLY = [ "testCases" ]
    _FIELDS_REQUIRED = [ "assignment", "name" ]

# =============================================================================