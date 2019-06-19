# Standard library imports...
import inspect
import unittest
import sys
try:
    # python 3
    from unittest.mock import Mock, patch
except ImportError:
    # python 2, requires dependency
    from mock import Mock, patch

# codePost_api imports...
import codePost_api.helpers as helpers
import codePost_api.errors as errors

# test constants
TEST_API_KEY = 'TEST_KEY'

##############################################################################################

#############################################################################
# Unit test class to ensure that all helpers methods gracefully react to
# server errors by throwing a voluntary RuntimeError.
#############################################################################

class TestServerRuntimeErrors(unittest.TestCase):

    @classmethod
    def _make_mock_request(cls):
        mock_fr = Mock()
        mock_fr.status_code = 500
        mock_fr.json.return_value = None
        return mock_fr

    @classmethod
    def _make_mock_params(cls, callable):

        param_names = []

        if (sys.version_info > (3, 0)):
            sig = inspect.signature(callable)
            param_names = [ p.name for p in sig.parameters.values() ]
        
        else:
            param_names = inspect.getargspec(callable).args

        params = {}
        for p_name in param_names:
            
            if p_name in ["self", "cls"]:
                continue
            
            if p_name in cls.kwargs:
                continue
            
            if "ids" in p_name.lower():
                params[p_name] = []
                continue
            
            elif "id" in p_name.lower():
                params[p_name] = 1
                continue
            
            params[p_name] = None
            
        return params
    
    @classmethod
    def _make_runtime_error_test(cls, callable):

        def test(self):
            _extraparams = cls._make_mock_params(callable)
            
            # Compatible with Python 2 (otherwise would have just passed
            # as a second keyword args dict in function call below).
            _extraparams.update(self.kwargs)

            return self.assertRaises(
                RuntimeError,
                callable,
                **_extraparams
            )
        
        return test

    @classmethod
    def setUpClass(cls):

        httpverbs = [ "get", "post", "patch", "delete" ]

        cls._patchers = {}
        cls._mocks = {}

        for verb in httpverbs:
            methodname = "codePost_api.helpers._requests.{}".format(verb)
            cls._patchers[verb] = patch(methodname)
            cls._mocks[verb] = cls._patchers[verb].start()
            cls._mocks[verb].return_value = cls._make_mock_request()

        cls.kwargs = { "api_key": TEST_API_KEY  }

    @classmethod
    def tearDownClass(cls):
        for _verb, mockobj in cls._mocks.items():
            mockobj.stop()

    def test_all_helper_methods(self):

        # FIXME: As a temporary fix, these methods are ignored. They should
        # follow the convention of throwing a RuntimeError if the codePost
        # API is not responsive.

        ignore_methods = [
            "remove_comments", 
            "remove_students_from_submission",
            "set_submission_students"
            ]
        
        # Use introspection to get list of methods to test
        methods = [
            obj[1]
            for obj in inspect.getmembers(helpers)
            if inspect.isfunction(obj[1])
            if inspect.getmodule(obj[1]).__name__.startswith("codePost_api.")
            if not obj[0].startswith("_")
            if not obj[0] in ignore_methods
        ]
        
        for method in methods:
            if (sys.version_info > (3, 4)):
                # Cleaner, as this is labeled as a subtest
                with self.subTest(msg=method.__name__):
                    self._make_runtime_error_test(method)(self)
            else:
                self._make_runtime_error_test(method)(self)

#############################################################################
# Function tested: helpers.get_available_courses
# Notes:
#
#############################################################################

@patch("codePost_api.helpers.delete_file")
@patch("codePost_api.helpers.delete_submission")
def test_upload_error_with_successful_api_calls(mock_delete_submission, mock_delete_file):
    mock_delete_submission.return_value = None
    mock_delete_file.return_value = None

    obj = errors.UploadError(
        message="Upload error message.",
        api_key=TEST_API_KEY,
        assignment_id=1,
        submission_id=1,
        file_ids=[1])
    
    obj.force_cleanup()

@patch("codePost_api.helpers.delete_file")
@patch("codePost_api.helpers.delete_submission")
def test_upload_error_with_failed_api_calls(mock_delete_submission, mock_delete_file):
    mock_delete_submission.side_effect = lambda: 1/0 # throw an(y) exception
    mock_delete_file.side_effect = lambda: 1/0 # throw an(y) exception

    obj = errors.UploadError(
        message="Upload error message.",
        api_key=TEST_API_KEY,
        assignment_id=1,
        submission_id=1,
        file_ids=[1])
    
    obj.force_cleanup()
