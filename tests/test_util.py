# Standard library imports...
import inspect
import os
import unittest
import sys
try:
    # python 3
    from unittest.mock import Mock, patch, mock_open
except ImportError: # pragma: no cover
    # python 2, requires dependency
    from mock import Mock, patch, mock_open

# Third-party imports...
#from nose.tools import assert_equal, assert_is_not_none

# codePost_api imports...
import codePost_api.helpers as helpers
import codePost_api.errors as errors
import codePost_api.util as util

# test constants
TEST_API_KEY = '0'*40 # DRF's auth tokens are currently 40 characters long

class _AssertHelper(unittest.TestCase):
    def runTest(self):
        pass

_assert = _AssertHelper()

##############################################################################################

#############################################################################
# Function tested: util.validate_api_key
# Notes:
#
#############################################################################

@patch("codePost_api.util._requests.get")
def test_validate_api_key_on_server_success(mock_get):

    mock_get.return_value.status_code = 200
    _assert.assertTrue(util.validate_api_key(TEST_API_KEY))

@patch("codePost_api.util._requests.get")
def test_validate_api_key_on_server_success_without_authorization(mock_get):

    mock_get.return_value.status_code = 403
    _assert.assertTrue(util.validate_api_key(TEST_API_KEY))

@patch("codePost_api.util._requests.get")
def test_validate_api_key_on_server_failure(mock_get):

    mock_get.return_value.status_code = 401
    _assert.assertFalse(util.validate_api_key(TEST_API_KEY))

@patch("codePost_api.util._requests.get")
def test_validate_api_key_on_server_crash(mock_get):

    mock_get.side_effect = lambda x: 1/0 # an(y) exception
    _assert.assertFalse(util.validate_api_key(TEST_API_KEY))

def test_validate_api_key_none():
    _assert.assertFalse(util.validate_api_key(None, log_outcome=True))

def test_validate_api_key_not_stringable():

    # This class will crash when an attempt to convert to
    # string is made
    class CrashOnStr(object):
        def __str__(self):
            raise Exception("intentional exception")

    _assert.assertFalse(util.validate_api_key(CrashOnStr(), log_outcome=True))

def test_validate_api_key_smaller_than_5():
    _assert.assertFalse(util.validate_api_key("0"*4))

def test_validate_api_key_smaller_than_40():
    _assert.assertFalse(util.validate_api_key("0"*39))

#############################################################################
# Function tested: util.configure_api_key
# Notes:
#
#############################################################################

def test_configure_api_key_override_parameter():
    _assert.assertEqual(
        TEST_API_KEY,
        util.configure_api_key(
            api_key=TEST_API_KEY,
            override=True))

def test_configure_api_key_override_variable():
    util._API_KEY_OVERRIDE = TEST_API_KEY
    util.API_KEY = None
    _assert.assertEqual(
        TEST_API_KEY,
        util.configure_api_key(
            api_key=TEST_API_KEY,
            override=False))

def test_configure_api_key_stored():
    util._API_KEY_OVERRIDE = None
    util.API_KEY = TEST_API_KEY
    _assert.assertEqual(
        TEST_API_KEY,
        util.configure_api_key(
            api_key=None,
            override=False))


def test_configure_api_key_by_environment_var():
    util._API_KEY_OVERRIDE = None
    util.API_KEY = None
    mock_env = patch.dict(os.environ, {
        util.DEFAULT_API_KEY_VARNAME: TEST_API_KEY })

    mock_env.start()
    _assert.assertEqual(
        TEST_API_KEY,
        util.configure_api_key(
            api_key=None,
            override=False))
    mock_env.stop()

@patch("codePost_api.util._os.path.exists")
@patch("codePost_api.util._os.path.isfile")
@patch("codePost_api.util._load_yaml")
def test_configure_api_key_by_yaml_file(
    mock_load_yaml, mock_isfile, mock_exists):

    util._API_KEY_OVERRIDE = None
    util.API_KEY = None
    mock_env = patch.dict(os.environ, {
        util.DEFAULT_API_KEY_VARNAME: "" })

    # Set up the mocks
    mock_exists.return_value = True
    mock_isfile.return_value = True
    mock_load_yaml.return_value = {
        "api_key": TEST_API_KEY
    }

    mock_env.start()
    del os.environ[util.DEFAULT_API_KEY_VARNAME]

    # Figure out the name of the open builtin
    # https://stackoverflow.com/a/34677735/408734
    builtins_name = "builtins"
    if (sys.version_info < (3, 0)):
        # Python 2
        builtins_name = "__builtin__"
    open_name = "{}.open".format(builtins_name)

    with patch(open_name, mock_open(read_data="")) as mock_file:
        _assert.assertEqual(
            TEST_API_KEY,
            util.configure_api_key(
                api_key=None,
                override=False))
        mock_file.assert_called()
        
    mock_env.stop()

@patch("codePost_api.util._os.path.exists")
@patch("codePost_api.util._os.path.isfile")
@patch("codePost_api.util._load_yaml")
def test_configure_api_key_by_yaml_file_empty(
    mock_load_yaml, mock_isfile, mock_exists):

    util._API_KEY_OVERRIDE = None
    util.API_KEY = None
    mock_env = patch.dict(os.environ, {
        util.DEFAULT_API_KEY_VARNAME: "" })

    # Set up the mocks
    mock_exists.return_value = True
    mock_isfile.return_value = True
    mock_load_yaml.return_value = {
        "api_key": ""
    }

    mock_env.start()
    del os.environ[util.DEFAULT_API_KEY_VARNAME]

    # Figure out the name of the open builtin
    # https://stackoverflow.com/a/34677735/408734
    builtins_name = "builtins"
    if (sys.version_info < (3, 0)):
        # Python 2
        builtins_name = "__builtin__"
    open_name = "{}.open".format(builtins_name)

    with patch(open_name, mock_open(read_data="")) as mock_file:
        _assert.assertIsNone(
            util.configure_api_key(
                api_key=None,
                override=False))
        mock_file.assert_called()
        
    mock_env.stop()

@patch("codePost_api.util._os.path.exists")
@patch("codePost_api.util._os.path.isfile")
@patch("codePost_api.util._load_yaml")
def test_configure_api_key_by_yaml_file_crashes(
    mock_load_yaml, mock_isfile, mock_exists):

    util._API_KEY_OVERRIDE = None
    util.API_KEY = None
    mock_env = patch.dict(os.environ, {
        util.DEFAULT_API_KEY_VARNAME: "" })

    # Set up the mocks
    mock_exists.return_value = True
    mock_isfile.return_value = True
    #mock_load_yaml.return_value = None
    mock_load_yaml.side_effects = lambda x: 1/0 # An(y) exception

    mock_env.start()
    del os.environ[util.DEFAULT_API_KEY_VARNAME]

    _assert.assertIsNone(
        util.configure_api_key(
            api_key=None,
            override=False))
        
    mock_env.stop()


def test_get_logger():
    util.get_logger()
