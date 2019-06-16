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
import codePost_api.helpers as helpers

# test constants
TEST_API_KEY = 'TEST_KEY'

##############################################################################################

#############################################################################
# Function tested: helpers.get_available_courses
# Notes:
#
#############################################################################
class TestGetAvailableCourses(object):
    @classmethod
    def setup_class(cls):
        cls.mock_get_patcher = patch('codePost_api.helpers._requests.get')
        cls.mock_get = cls.mock_get_patcher.start()

    @classmethod
    def teardown_class(cls):
        cls.mock_get.stop()

    def test_get_available_courses_on_success_without_filter(self):
        mockObj = [
            {'id' : 1, 'name' : 'COS126', 'period' : 'S2019'}
            ]

        self.mock_get.return_value = Mock()
        self.mock_get.return_value.status_code = 200
        self.mock_get.return_value.json.return_value = mockObj

        courses = helpers.get_available_courses(TEST_API_KEY)

        assert_equal(mockObj, courses)

    def test_get_available_courses_on_success_with_filter_results(self):
        course1 = {'id' : 1, 'name' : 'COS126', 'period' : 'S2019'}
        course2 = {'id' : 2, 'name' : 'COS226', 'period' : 'S2020'}

        mockObj = [course1, course2]

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
        mockObj = [course1, course2]

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

#############################################################################
# Function tested: helpers.get_course_roster_by_id
# Notes:
#
#############################################################################
@patch('codePost_api.helpers._requests.get')
def test_get_course_roster_by_id(mock_get):
    roster = {'id': 1}

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = roster

    response = helpers.get_course_roster_by_id(TEST_API_KEY, roster['id'])
    assert_equal(roster, response)

#############################################################################
# Function tested: helpers.get_course_roster_by_name
# Notes:
#
#############################################################################
@patch('codePost_api.helpers.get_course_roster_by_id')
@patch('codePost_api.helpers.get_available_courses')
def test_get_course_roster_by_name(mock_get_available_courses, mock_get_course_roster_by_id):
    course1 = {'id' : 1, 'name' : 'COS126', 'period' : 'S2019'}
    roster = {'id': 1, 'students': ['someEmail@princeton.edu']}

    # note that get_course_roster_by_name combines the course object and roster object in its return value
    output = {'id' : 1, 'name' : 'COS126', 'period' : 'S2019', 'students': ['someEmail@princeton.edu']}

    mock_get_available_courses.return_value = [course1]
    mock_get_course_roster_by_id.return_value = roster

    response = helpers.get_course_roster_by_name(TEST_API_KEY, 'COS126', 'S2019')
    assert_equal(output, response)

#############################################################################
# Function tested: helpers.get_assignment_info_by_id
# Notes:
#
#############################################################################
@patch('codePost_api.helpers._requests.get')
def test_get_assignment_info_by_id(mock_get):
    assignment = {'id': 1}

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = assignment

    response = helpers.get_course_roster_by_id(TEST_API_KEY, assignment['id'])
    assert_equal(assignment, response)

#############################################################################
# Function tested: helpers.get_assignment_info_by_name
# Notes:
#
#############################################################################
@patch('codePost_api.helpers.get_assignment_info_by_id')
@patch('codePost_api.helpers.get_available_courses')
def test_get_assignment_info_by_name(mock_get_available_courses, mock_get_assignment_info_by_id):

    # mock get_available_courses
    course2 = {'id' : 2, 'name' : 'COS226', 'period' : 'S2019', 'assignments': [3,4,5]}
    mock_get_available_courses.return_value = [course2]

    # mock get_assignment_info_by_id
    def side_effect(api_key, assignment_id):
        return {
          'id': assignment_id,
          'name': 'assignment-%d' % assignment_id,
        }

    mock_get_assignment_info_by_id.side_effect = side_effect
    response = helpers.get_assignment_info_by_name(TEST_API_KEY, 'COS226', 'S2019', 'assignment-4')

    assert_equal({'id': 4, 'name' : 'assignment-4'}, response)

#############################################################################
# Function tested: helpers.get_assignment_submissions
# Notes:
#
#############################################################################
@patch('codePost_api.helpers._requests.get')
def test_get_assignment_submissions(mock_get):
    # Configure the mock to return a response with an OK status code.
    submission1 = {
      'id' : 1,
      'students' : ['student1@codepost.io'],
      'assignment' : 1,
    }
    submission2 = {
      'id' : 2,
      'students' : ['student2@codepost.io'],
      'assignment' : 1,
    }


    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [submission1,submission2]

    response = helpers.get_assignment_submissions(TEST_API_KEY, 1)
    assert_equal([submission1,submission2], response)

#############################################################################
# Function tested: helpers.get_file
# Notes:
#
#############################################################################
@patch('codePost_api.helpers._requests.get')
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

#############################################################################
# Function tested: helpers.set_submission_grader
# Notes:
# - should we return the uploaded submission here instead of a boolean
#
#############################################################################
@patch('codePost_api.helpers._requests.patch')
def test_set_submission_grader(mock_patch):
    submission1 = {
      'id' : 1,
      'students' : ['student1@codepost.io'],
      'assignment' : 1,
    }

    mock_patch.return_value.status_code = 200
    mock_patch.return_value.json.return_value = submission1

    response = helpers.set_submission_grader(TEST_API_KEY, submission1['id'], None)
    assert_equal(True, response)

#############################################################################
# Function tested: helpers.set_submission_grader
# Notes:
#
#############################################################################
@patch('codePost_api.helpers._requests.patch')
def test_unclaim_submission(mock_patch):
    submission1 = {
      'id' : 1,
      'students' : ['student1@codepost.io'],
      'assignment' : 1,
    }

    mock_patch.return_value.status_code = 200
    mock_patch.return_value.json.return_value = submission1

    response = helpers.unclaim_submission(TEST_API_KEY, submission1['id'])
    assert_equal(True, response)

#############################################################################
# Function tested: helpers.remove_comments
# Notes:
#
#############################################################################
@patch('codePost_api.helpers._requests.delete')
@patch('codePost_api.helpers._requests.get')
def test_remove_comments(mock_get, mock_delete):
    file1 = {
      'id' : 1,
      'submission' : 1,
      'comments' : [1,2,3],
    }

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = file1

    mock_delete.return_value.status_code = 204

    response = helpers.remove_comments(TEST_API_KEY, file_id=file1['id'])
    assert_equal(True, response)

#############################################################################
# Function tested: helpers.delete_submission
# Notes:
#
#############################################################################
@patch('codePost_api.helpers._requests.delete')
def test_delete_submission(mock_delete):
    mock_delete.return_value.status_code = 204
    response = helpers.delete_submission(TEST_API_KEY, 1)
    assert_is_not_none(response)

#############################################################################
# Function tested: helpers.delete_file
# Notes:
#
#############################################################################
@patch('codePost_api.helpers._requests.delete')
def test_delete_file(mock_delete):
    mock_delete.return_value.status_code = 204
    response = helpers.delete_file(TEST_API_KEY, 1)
    assert_is_not_none(response)

#############################################################################
# Function tested: helpers.post_file
# Notes:
#
#############################################################################
@patch('codePost_api.helpers._requests.post')
def test_post_file(mock_post):
    mock_post.return_value.status_code = 201
    response = helpers.post_file(TEST_API_KEY, 1, 'test.txt', 'hello', 'txt')
    assert_is_not_none(response)

#############################################################################
# Function tested: helpers.post_submission
# Notes:
#
#############################################################################
@patch('codePost_api.helpers._requests.post')
def test_post_submission(mock_post):
    file = {'name' : 'test.txt', 'code' : 'hello', 'extension' : 'txt'}
    mock_post.return_value.status_code = 201
    response = helpers.post_submission(TEST_API_KEY, 1, ['test.txt'], [file])
    assert_is_not_none(response)

#############################################################################
# Function tested: helpers.post_comment
# Notes:
#
#############################################################################
@patch('codePost_api.helpers._requests.post')
def test_post_comment(mock_post):
    file = {'name' : 'test.txt', 'code' : 'hello', 'extension' : 'txt', 'id' : 1}
    mock_post.return_value.status_code = 201
    response = helpers.post_comment(TEST_API_KEY, file, 'test', 1, 0, 1, 0, 0)
    assert_is_not_none(response)

#############################################################################
# Function tested: helpers.set_submission_students
# Notes:
#
#############################################################################
@patch('codePost_api.helpers._requests.patch')
def test_set_submission_students(mock_patch):
    mock_patch.return_value.status_code = 200
    response = helpers.set_submission_students(TEST_API_KEY, 1, ['student1@codepost.io'])
    assert_is_not_none(response)

#############################################################################
# Function tested: helpers.remove_students_from_submission
# Notes:
#
#############################################################################
@patch('codePost_api.helpers._requests.delete')
@patch('codePost_api.helpers._requests.patch')
def test_remove_students_from_submission(mock_patch, mock_delete):
    submission1 = {
      'id' : 1,
      'students' : ['student1@codepost.io', 'student2@codepost.io'],
      'assignment' : 1,
    }

    submission2 = {
      'id' : 1,
      'students' : ['student2@codepost.io'],
      'assignment' : 1,
    }

    mock_patch.return_value.status_code = 200
    mock_patch.return_value.json.return_value = submission2
    mock_delete.return_value.status_code = 204
    mock_delete.return_value.json.return_value = None

    # remove one student from the submission
    response = helpers.remove_students_from_submission(TEST_API_KEY, submission1, ['student1@codepost.io'])
    assert_is_not_none(response)

    # remove the last remaining student from submission => should trigger a delete
    response = helpers.remove_students_from_submission(TEST_API_KEY, submission2, ['student2@codepost.io'])
    assert_equal(response, None) # response from mock_delete

#############################################################################
# Function tested: helpers.get_course_grades
# Notes:
#
#############################################################################
@patch('codePost_api.helpers.get_assignment_submissions')
@patch('codePost_api.helpers.get_assignment_info_by_id')
@patch('codePost_api.helpers.get_course_roster_by_name')
def test_get_course_grades(mock_roster, mock_assignment, mock_submissions):
    roster = {
      'name' : 'COS126',
      'period' : 'S2019',
      'students' : ['student1@codepost.io', 'student2@codepost.io'],
      'assignments' : [1,2,3]
    }

    mock_roster.return_value.status_code = 200
    mock_roster.return_value = roster

    # mock get_assignment_info_by_id
    def side_effect(api_key, assignment_id):
        return {
          'id': assignment_id,
          'name': 'assignment-%d' % assignment_id,
        }

    mock_assignment.side_effect = side_effect

    submission1 = {
      'id' : 1,
      'grade' : 10,
      'grader' : 'james@codepost.io',
      'isFinalized' : True,
      'students' : ['student1@codepost.io']
    }

    mock_submissions.return_value = [submission1]
    response = helpers.get_course_grades(TEST_API_KEY, 'COS126', 'S2019')

    # expected response
    answer = {
      'student1@codepost.io' : {
        'assignment-1' : 10,
        'assignment-2' : 10,
        'assignment-3' : 10,
      }
    }

    assert_equal(answer, response)
