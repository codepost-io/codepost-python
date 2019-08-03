import codepost

def test():
    assert True

import unittest
try:
    # python 3
    from unittest.mock import Mock, patch
except ImportError:
    # python 2, requires dependency
    from mock import Mock, patch

@patch('codepost.http_client._requests.get')
def test_get_course_roster_by_id(mock_get):
    return True
