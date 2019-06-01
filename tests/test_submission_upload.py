# Standard library imports...
try:
  # python 3
  from unittest.mock import Mock, patch
except ImportError:
  # python 2, requires dependency
  from mock import Mock, patch

# Third-party imports...
from nose.tools import assert_equal, assert_is_not_none

# codePost_api imports...
import codePost_api as helpers

# test constants
TEST_API_KEY = 'TEST_KEY'

@patch('codePost_api.helpers.post_submission')
@patch('codePost_api.helpers.get_assignment_submissions')
def test_upload_submission_with_no_conflicts(mock_get_submissions, mock_post_submission):

  # create mock data
  assignment = {
    'id' : 1,
  }

  file1 = {
    'code' : 'test',
    'name' : 'test.txt',
    'extension' : 'txt',
  }

  def side_effect(api_key, assignment_id, students, files):
    return {
      'assignment' : assignment_id,
      'students' : students,
      'files' : files,
    }

  # setup mocks
  mock_get_submissions.return_value = []
  mock_post_submission.side_effect = side_effect

  # run function
  response = helpers.upload_submission(TEST_API_KEY, assignment, ['student1@codepost.io'], [file1])
  answer = {
    'assignment' : 1,
    'students' : ['student1@codepost.io'],
    'files' : [file1]
  }
  assert_equal(answer, response)
