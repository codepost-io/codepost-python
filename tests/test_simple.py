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

codepost.util.config.configure_api_key(api_key="TESTAPI")

@patch('codepost.http_client._requests.get')
def test_get_course_roster_by_id(mock_get):
    roster = {'id': 1}

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = roster

    obj = codepost.assignment.retrieve(id=1)
    print(obj)
