# Standard library imports...
from unittest.mock import Mock, patch

# Third-party imports...
from nose.tools import assert_equal

import codepost_api.helpers as helpers

TEST_API_KEY = 'TEST_KEY'

class TestGetAvailableCourses(object):
    @classmethod
    def setup_class(cls):
      cls.mock_get_patcher = patch('codepost_api.helpers._requests.get')
      cls.mock_get = cls.mock_get_patcher.start()

    @classmethod
    def teardown_class(cls):
      cls.mock_get.stop()

    def test_get_available_courses_on_success_without_filter(self):
      mockObj = {
        'courseadminCourses' : [
          {'id' : 1, 'name' : 'COS126', 'period' : 'S2019'}
        ]
      }

      self.mock_get.return_value = Mock()
      self.mock_get.return_value.status_code = 200
      self.mock_get.return_value.json.return_value = mockObj

      courses = helpers.get_available_courses(TEST_API_KEY)

      assert_equal(mockObj['courseadminCourses'], courses)

    def test_get_available_courses_on_success_with_filter_results(self):
      course1 = {'id' : 1, 'name' : 'COS126', 'period' : 'S2019'}
      course2 = {'id' : 1, 'name' : 'COS226', 'period' : 'S2020'}

      mockObj = {'courseadminCourses' : [course1, course2]}

      self.mock_get.return_value = Mock()
      self.mock_get.return_value.status_code = 200
      self.mock_get.return_value.json.return_value = mockObj

      # test filtering by name
      courses = helpers.get_available_courses(TEST_API_KEY, course_name='COS126')
      assert_equal([course1], courses)

      # test filtering by period
      courses = helpers.get_available_courses(TEST_API_KEY, course_period='S2020')
      assert_equal([course2], courses)

      # test filtering by both name and period
      courses = helpers.get_available_courses(TEST_API_KEY, course_name='COS226', course_period='S2020')
      assert_equal([course2], courses)

    def test_get_available_courses_on_success_with_no_filter_results(self):
      course1 = {'id' : 1, 'name' : 'COS126', 'period' : 'S2019'}
      course2 = {'id' : 1, 'name' : 'COS226', 'period' : 'S2020'}
      mockObj = {'courseadminCourses' : [course1, course2]}

      self.mock_get.return_value = Mock()
      self.mock_get.return_value.status_code = 200
      self.mock_get.return_value.json.return_value = mockObj

      # test filtering by name
      courses = helpers.get_available_courses(TEST_API_KEY, course_name='COS120')
      assert_equal([], courses)

      # test filtering by period
      courses = helpers.get_available_courses(TEST_API_KEY, course_period='S2000')
      assert_equal([], courses)

      # test filtering by both name and period
      courses = helpers.get_available_courses(TEST_API_KEY, course_name='COS326', course_period='S2020')
      assert_equal([], courses)


@patch('codepost_api.helpers._requests.get')
def test_get_course_roster_by_id(mock_get):
  roster = {'id': 1}

  mock_get.return_value.status_code = 200
  mock_get.return_value.json.return_value = roster

  response = helpers.get_course_roster_by_id(TEST_API_KEY, roster['id'])
  assert_equal(roster, response)

@patch('codepost_api.helpers.get_course_roster_by_id')
@patch('codepost_api.helpers.get_available_courses')
def test_get_course_roster_by_name(mock_get_available_courses, mock_get_course_roster_by_id):
  course1 = {'id' : 1, 'name' : 'COS126', 'period' : 'S2019'}
  roster = {'id': 1, 'students': ['someEmail@princeton.edu']}

  # note that get_course_roster_by_name combines the course object and roster object in its return value
  output = {'id' : 1, 'name' : 'COS126', 'period' : 'S2019', 'students': ['someEmail@princeton.edu']}

  mock_get_available_courses.return_value = [course1]
  mock_get_course_roster_by_id.return_value = roster

  response = helpers.get_course_roster_by_name(TEST_API_KEY, 'COS126', 'S2019')
  assert_equal(output, response)

@patch('codepost_api.helpers._requests.get')
def test_get_assignment_info_by_id(mock_get):
  assignment = {'id': 1}

  mock_get.return_value.status_code = 200
  mock_get.return_value.json.return_value = assignment

  response = helpers.get_course_roster_by_id(TEST_API_KEY, assignment['id'])
  assert_equal(assignment, response)

@patch('codepost_api.helpers._requests.get')
def test_get_file(mock_get):
  # Configure the mock to return a response with an OK status code.
  file = {
    'id': 1,
    'name' : 'test.txt',
    'code': 'test',
    'extension': '.txt',
    'submission': 1,
    'comments': []
  }

  mock_get.return_value.status_code = 200
  mock_get.return_value.json.return_value = file

  response = helpers.get_file(TEST_API_KEY, file['id'])
  assert_equal(file, response)

