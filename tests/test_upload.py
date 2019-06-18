# Standard library imports...
import inspect
import itertools
import unittest
import sys
try:
    # python 3
    from unittest.mock import Mock, patch
except ImportError:
    # python 2, requires dependency
    from mock import Mock, patch

# Third-party imports...
#import pytest

# codePost_api imports...
# codePost_api imports...
from codePost_api import helpers
from codePost_api import errors
from codePost_api import upload

# test constants
TEST_API_KEY = 'TEST_KEY'

class _AssertHelper(unittest.TestCase):
    def runTest(self):
        pass

_assert = _AssertHelper()

def is_exception(obj):
    result = False
    try:
        if isinstance(obj, Exception):
            result = True
    except:
        pass
    try:
        # NOTE: Will only work for exception that can be instantiated
        # without additional parameters
        if isinstance(obj(), Exception):
            result = True
    except TypeError:
        # This would be thrown if the constructor wanted additional
        # parameters, so result = Maybe
        pass
    except:
        pass
    return result

#########################################################################

@patch('codePost_api.upload._post_submission')
@patch('codePost_api.upload._get_assignment_submissions')
def test_upload_submission_with_no_conflicts(mock_get_submissions, mock_post_submission):

    # create mock data
    assignment = {
      'id' : 111,
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
    response = upload.upload_submission(TEST_API_KEY, assignment, ['student1@codepost.io'], [file1])
    answer = {
      'assignment' : 111,
      'students' : ['student1@codepost.io'],
      'files' : [file1]
    }
    _assert.assertEqual(answer, response)



@patch('codePost_api.upload._post_submission')
@patch('codePost_api.upload._get_assignment_submissions')
def test_upload_submission_with_no_conflictsm(mock_get_submissions, mock_post_submission):

    # create mock data
    assignment = {
      'id' : 111,
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
    response = upload.upload_submission(TEST_API_KEY, assignment, ['student1@codepost.io'], [file1])
    answer = {
      'assignment' : 111,
      'students' : ['student1@codepost.io'],
      'files' : [file1]
    }
    _assert.assertEqual(answer, response)

#########################################################################


class AbstractManyMocksTestCase(unittest.TestCase):

    @classmethod
    def _configure_mock_to_outcome(cls, mock, outcome, name=None):

        # Reset the mock
        mock.return_value = None
        mock.side_effect = None

        # Determine whether it should return a value, or throw an
        # exception

        if is_exception(outcome):
            def _raise_helper(*args, **kwargs):
                raise outcome(message=name)
            mock.side_effect = _raise_helper
        
        else:
            mock.return_value = outcome
        
        return mock

    @classmethod
    def _configure_mocks_to_outcomes(cls, outcome_tuple):
        for (method, outcome) in outcome_tuple.items():
            if method in cls._mocks:
                cls._mocks[method] = cls._configure_mock_to_outcome(
                    mock=cls._mocks[method],
                    outcome=outcome,
                    name=method)

    @classmethod
    def setUpClass(cls):

        cls._patchers = {}
        cls._mocks = {}
        cls._outcomes = {}
        
        # Setup mocks for submethods with no impact on the control flow
        # of the method we are trying to test, thus which should simply
        # not be executed.

        for method in cls._methods_without_impact:
            method_full_name = cls._methods_prefix.format(method)

            # Create the mock and apply it
            cls._patchers[method] = patch(method_full_name)
            cls._mocks[method] = cls._patchers[method].start()

            # Value for returned by all methods without impact
            cls._mocks[method].return_value = True
        
        # Setup mocks for more important submethods, which have some
        # impact on the control flow of the program; these methods
        # are provided with all of their finite number of return
        # values. These will result in subtests.

        for method_dict in cls._methods_with_impact:
            method = method_dict["name"]
            method_full_name = cls._methods_prefix.format(method)

            # Create the mock and apply it
            cls._patchers[method] = patch(method_full_name)
            cls._mocks[method] = cls._patchers[method].start()

            # Store all the outcomes
            cls._outcomes[method] = method_dict.get(
                "outcomes",
                list([True]))

    @classmethod
    def tearDownClass(cls):
        for _method, mock_obj in cls._mocks.items():
            mock_obj.stop()
    
    @classmethod
    def _make_outcome_aux_generator(cls):
        if hasattr(cls, "_outcomes") and hasattr(cls, "_mocks"):
            items = cls._outcomes.items()
            keys = list(map(lambda item: item[0], items))
            values = map(lambda item: item[1], items)
            values_product = itertools.product(*values)
            return { "keys": keys, "generator": values_product }
    
    @classmethod
    def reset_mock_outcomes(cls):
        cls._generator = cls._make_outcome_aux_generator()
    
    @classmethod
    def _next_mock_outcome_tuple(cls):
        if not hasattr(cls, "_generator"):
            cls.reset_mock_outcomes()
        
        if cls._generator:
            next_tuple = None
            try:
                next_tuple = cls._generator["generator"].__next__()
            except StopIteration:
                return None
            
            if next_tuple:
                return dict(zip(cls._generator["keys"], next_tuple))

    @classmethod
    def next_mock_outcome(cls):

        # Compute the next outcome tuple
        outcome_tuple = cls._next_mock_outcome_tuple()
        if outcome_tuple == None:
            return None

        # Configure the environment
        cls._configure_mocks_to_outcomes(outcome_tuple)
        return outcome_tuple
    
    @classmethod
    def mock_outcome_generator(cls):
        
        # Generator class
        def _generator():
            generator_dict = cls._make_outcome_aux_generator()

            keys = generator_dict["keys"]
            generator = generator_dict["generator"]

            while True:
                current = None
                try:
                    current = generator.__next__()
                except StopIteration:
                    break
                
                outcome_tuple = dict(zip(keys, current))

                yield outcome_tuple
        
        return _generator()




class AbstractUploadTestCase(AbstractManyMocksTestCase):
    _methods_prefix = "codePost_api.upload._{}"

    _methods_without_impact = [
        "delete_submission",
        "set_submission_students",
        "remove_comments",
        "unclaim_submission",
        "get_submission_by_id",
    ]
    _methods_with_impact = [
        {
            "name": "remove_students_from_submission",
            "outcomes": [ { "id": 1 } ]
        },
        {
            "name": "post_submission",
            "outcomes": [ True, errors.UploadError ]
        },
        {
            "name": "submission_list_is_unclaimed",
            "outcomes": [ True, False ]
        },
        {
            "name": "upload_submission_filediff",
            "outcomes": [ True, False, errors.UploadError ]
        },
    ]

class UploadTestCase(AbstractUploadTestCase):

    # CASE 1: No existing submission => create a new submission
    @patch("codePost_api.upload._get_assignment_submissions")
    def test_with_no_existing_submissions(self, mock_gas):
        # create mock data
        assignment1 = { "id" : 1, }

        file1 = { "code": "t1", "name": "t1.txt", "extension": "txt", }
        file2 = { "code": "t2", "name": "t2.txt", "extension": "txt", }

        student1 = "student1@test.codepost.io"

        # Setup mock for "get_assignment_submissions" to return nothing
        # (thus there are no "existing submissions" in the following
        # scenarios)
        mock_gas.return_value = []

        # For each of the multiple paths:
        for outcome_tuple in self.mock_outcome_generator():
            
            # For all possible upload modes
            for mode in list(upload.UploadModes.__members__.values()):

                # Create a subtest
                with self.subTest(outcome=outcome_tuple, mode=mode):

                    # Configure the mocks
                    self._configure_mocks_to_outcomes(
                        outcome_tuple=outcome_tuple)

                    # The method that will run this test
                    def _run_test():
                        return upload.upload_submission(
                            api_key=TEST_API_KEY,
                            assignment=assignment1,
                            students=[student1],
                            files=[file1, file2],
                            mode=mode
                        )
                    
                    # Running the test with correct outcome
                    ps_outcome = outcome_tuple["post_submission"]
                    if is_exception(ps_outcome):
                        self.assertRaises(ps_outcome, _run_test)
                    else:
                        self.assertEqual(ps_outcome, _run_test())
    
    # CASE 3a: One existing submission with no student conflicts
    @patch("codePost_api.upload._get_assignment_submissions")
    def test_with_one_existing_submissions_no_conflicts(self, mock_gas):
        # create mock data
        assignment1 = { "id" : 1, }

        file1 = { "code": "t1", "name": "t1.txt", "extension": "txt", }
        file2 = { "code": "t2", "name": "t2.txt", "extension": "txt", }

        student1 = "student1@test.codepost.io"

        submission_id1 =  7701

        # Setup mock for "get_assignment_submissions" to return the same
        # submission, with the same ID.
        mock_gas.return_value = [{
            "id": submission_id1,
            "students": [student1]
        }]

        # For each of the multiple paths:
        for outcome_tuple in self.mock_outcome_generator():
            
            # For all possible upload modes
            for mode in list(upload.UploadModes.__members__.values()):

                # Create a subtest
                with self.subTest(outcome=outcome_tuple, mode=mode):
                    # Configure the mocks
                    self._configure_mocks_to_outcomes(
                        outcome_tuple=outcome_tuple)

                    # The method that will run this test
                    def _run_test():
                        return upload.upload_submission(
                            api_key=TEST_API_KEY,
                            assignment=assignment1,
                            students=[student1],
                            files=[file1, file2],
                            mode=mode
                        )
                    
                    # Running the test with correct outcome
                    if not mode.value["updateIfExists"]:
                        self.assertRaises(errors.UploadError, _run_test)

                    elif not mode.value["updateIfClaimed"] \
                        and outcome_tuple["submission_list_is_unclaimed"]:
                        self.assertRaises(errors.UploadError, _run_test) 

                    else:
                        usf_outcome = outcome_tuple[
                            "upload_submission_filediff"]
                        if is_exception(usf_outcome):
                            self.assertRaises(usf_outcome, _run_test)
                        else:
                            # Since the submission exists, there will be
                            # no call to "post_submission"; instead all
                            # the branches which end here, will return the
                            # value of the "get_submission_by_id" method
                            self.assertTrue(_run_test())

    # CASE 3b: One existing submission with student conflicts
    @patch("codePost_api.upload._get_assignment_submissions")
    def test_with_one_existing_submissions_with_conflicts(self, mock_gas):
        # create mock data
        assignment1 = { "id" : 1, }

        file1 = { "code": "t1", "name": "t1.txt", "extension": "txt", }
        file2 = { "code": "t2", "name": "t1.txt", "extension": "txt", }

        submission_id1 =  7701

        student1 = "student1@test.codepost.io"
        student2 = "student2@test.codepost.io"

        # Setup mock for "get_assignment_submissions" to return the same
        # submission, with the same ID.
        mock_gas.return_value = [{
            "id": submission_id1,
            "students": [student2]
        }]

        # For each of the multiple paths:
        for outcome_tuple in self.mock_outcome_generator():
            
            # For all possible upload modes
            for mode in list(upload.UploadModes.__members__.values()):

                # Create a subtest
                with self.subTest(outcome=outcome_tuple, mode=mode):
                    # Configure the mocks
                    self._configure_mocks_to_outcomes(
                        outcome_tuple=outcome_tuple)

                    # The method that will run this test
                    def _run_test():
                        return upload.upload_submission(
                            api_key=TEST_API_KEY,
                            assignment=assignment1,
                            students=[student1],
                            files=[file1, file2],
                            mode=mode
                        )
                    
                    # Running the test with correct outcome
                    if not mode.value["updateIfExists"]:
                        self.assertRaises(errors.UploadError, _run_test)

                    elif not mode.value["updateIfClaimed"] \
                        and outcome_tuple["submission_list_is_unclaimed"]:
                        self.assertRaises(errors.UploadError, _run_test) 

                    else:
                        usf_outcome = outcome_tuple[
                            "upload_submission_filediff"]
                        if is_exception(usf_outcome):
                            self.assertRaises(usf_outcome, _run_test)
                        else:
                            # Since the submission exists, there will be
                            # no call to "post_submission"; instead all
                            # the branches which end here, will return the
                            # value of the "get_submission_by_id" method
                            self.assertTrue(_run_test())
    
    # CASE 2a: Several existing submission with no student conflicts
    @patch("codePost_api.upload._get_assignment_submissions")
    def test_with_many_existing_submissions_no_conflicts(self, mock_gas):
        # create mock data
        assignment1 = { "id" : 1, }

        file1 = { "code": "t1", "name": "t1.txt", "extension": "txt", }
        file2 = { "code": "t2", "name": "t2.txt", "extension": "txt", }

        submission_id1 = 7701
        submission_id2 = 7702

        student1 = "student1@test.codepost.io"
        student2 = "student2@test.codepost.io"

        # Setup mock for "get_assignment_submissions" to provide
        # different submissions depending on the student
        def _mock_gas_method(student, *args, **kwargs):
            if student == student1:
                return [{ "id": submission_id1, "students": [student1] }]
            elif student == student2:
                return [{ "id": submission_id2, "students": [student2] }]
            return []
        mock_gas.side_effect = _mock_gas_method

        # For each of the multiple paths:
        for outcome_tuple in self.mock_outcome_generator():
            
            # For all possible upload modes
            for mode in list(upload.UploadModes.__members__.values()):

                # Create a subtest
                with self.subTest(outcome=outcome_tuple, mode=mode):
                    # Configure the mocks
                    self._configure_mocks_to_outcomes(
                        outcome_tuple=outcome_tuple)

                    # The method that will run this test
                    def _run_test():
                        return upload.upload_submission(
                            api_key=TEST_API_KEY,
                            assignment=assignment1,
                            students=[student1, student2],
                            files=[file1, file2],
                            mode=mode
                        )
                    
                    # Running the test with correct outcome
                    if not mode.value["updateIfExists"]:
                        self.assertRaises(errors.UploadError, _run_test)

                    elif not mode.value["updateIfClaimed"] \
                        and outcome_tuple["submission_list_is_unclaimed"]:
                        self.assertRaises(errors.UploadError, _run_test)
                    
                    elif not mode.value["resolveStudents"]:
                        self.assertRaises(errors.UploadError, _run_test)

                    else:
                        ps_outcome = outcome_tuple["post_submission"]
                        if is_exception(ps_outcome):
                            self.assertRaises(ps_outcome, _run_test)
                        else:
                            self.assertEqual(ps_outcome, _run_test())




class AbstractFilediffTestCase(AbstractManyMocksTestCase):
    _methods_prefix = "codePost_api.upload._{}"

    _methods_without_impact = []
    _methods_with_impact = [
        {
            "name": "delete_file",
            "outcomes": [ True, ]#errors.UploadError ]
        },
        {
            "name": "post_file",
            "outcomes": [ { "id": 0 }, ]# errors.UploadError ]
        },
    ]


class FilediffTestCase(AbstractFilediffTestCase):
    # CASE 1: No existing submission => create a new submission
    @patch("codePost_api.upload._get_file")
    def tast_with_no_existing_submissions(self, mock_gf):
        # create mock data
        file_id1 = 7709

        submission1 = { "id" : 1, "files": [file_id1] }

        file1  = { "code": "t1", "name": "t1.txt", "extension": "txt", }
        file1m = { "code": "t1m", "name": "t1.txt", "extension": "txt", }
        file2  = { "code": "t2", "name": "t2.txt", "extension": "txt", }

        def _mock_gf_method(file_id, *args, **kwargs):
            if file_id == file_id1:
                return file1
            return file2
        mock_gf.side_effect = _mock_gf_method

        # For each of the multiple paths:
        for outcome_tuple in self.mock_outcome_generator():
            
            # For all possible upload modes
            for mode in list(upload.UploadModes.__members__.values()):

                # Create a subtest
                with self.subTest(outcome=outcome_tuple, mode=mode):

                    # Configure the mocks
                    self._configure_mocks_to_outcomes(
                        outcome_tuple=outcome_tuple)

                    # The method that will run this test
                    def _run_test():
                        return upload._upload_submission_filediff(
                            api_key=TEST_API_KEY,
                            submission_info=submission1,
                            newest_files=[file1m],
                            mode=mode
                        )
                    
                    # Running the test with correct outcome
                    df_outcome = outcome_tuple["delete_file"]
                    pf_outcome = outcome_tuple["post_file"]
                    if is_exception(pf_outcome):
                        self.assertRaises(pf_outcome, _run_test)
                    elif is_exception(df_outcome):
                        self.assertRaises(df_outcome, _run_test)
                    else:
                        #if mode.value["updateExistingFiles"]:
                        if mode.value["updateExistingFiles"]:
                            self.assertTrue(_run_test())
                        pass #self.assertTrue(_run_test())
