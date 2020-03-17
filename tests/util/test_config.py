
import pytest

import codepost.util.config as _config

# @pytest.fixture()
# def fake_requests(mocker, ):
#     for
#     mocker.patch.object(
#         _config._requests,
#         "get",
#         return_value=fake_401_req
#     )

class TestValidateApiKey:

    KEY_LENGTH = 40

    BAD_KEY_EMPTY = ""
    BAD_KEY_TOOSHORT = "a"*4
    BAD_KEY_TOOLONG = "a"*(KEY_LENGTH + 1)
    FAKE_KEY_RIGHTLENGTH = "a"*KEY_LENGTH

    def setup_method(self, method):
        """
        Run before every test.
        """
        _config._checked_api_keys = dict()

    def test_err_empty_string(self, mocker):
        p = mocker.patch("codepost.util.config._logger.warning")
        assert not _config.validate_api_key(self.BAD_KEY_EMPTY, log_outcome=False)
        p.assert_not_called()

    def test_err_empty_string_logged(self, mocker):
        p = mocker.patch("codepost.util.config._logger.warning")
        assert not _config.validate_api_key(self.BAD_KEY_EMPTY, log_outcome=True)
        p.assert_called()

    def test_err_unstringable(self, stringable_err):
        assert not _config.validate_api_key(stringable_err)

    def test_err_tooshort_string(self):
        assert not _config.validate_api_key(self.BAD_KEY_TOOSHORT)

    def test_err_toolong_string(self):
        assert not _config.validate_api_key(self.BAD_KEY_TOOLONG)

    def test_err_bad_request(self, requests_mock):
        api_key = self.FAKE_KEY_RIGHTLENGTH
        requests_mock.get(
            "{}/courses/".format(_config.BASE_URL),
            request_headers={"Authorization": "Token {}".format(api_key)},
            status_code=401)
        assert not _config.validate_api_key(api_key)
        assert requests_mock.called

    def test_success(self, requests_mock):
        api_key = self.FAKE_KEY_RIGHTLENGTH
        requests_mock.get(
            "{}/courses/".format(_config.BASE_URL),
            request_headers={"Authorization": "Token {}".format(api_key)},
            status_code=200)
        assert _config.validate_api_key(api_key)
        assert api_key in _config._checked_api_keys
        assert requests_mock.called

    def test_err_request_fail(self, requests_mock):
        api_key = self.FAKE_KEY_RIGHTLENGTH
        requests_mock.get(
            "{}/courses/".format(_config.BASE_URL),
            exc=Exception)
        assert not _config.validate_api_key(api_key)
        assert requests_mock.called

    def test_cached_true(self, mocker):
        api_key = self.FAKE_KEY_RIGHTLENGTH
        _config._checked_api_keys[api_key] = True
        p = mocker.patch("codepost.util.config._logger.debug")
        assert _config.validate_api_key(api_key, log_outcome=True)
        p.assert_called()

    def test_cached_false(self, mocker):
        api_key = self.FAKE_KEY_RIGHTLENGTH
        _config._checked_api_keys[api_key] = False
        assert not _config.validate_api_key(api_key)

    def test_cached_refresh_true(self, mocker):
        api_key = self.FAKE_KEY_RIGHTLENGTH
        _config._checked_api_keys[api_key] = True
        p = mocker.patch("codepost.util.config._logger.debug")
        assert not _config.validate_api_key(api_key, refresh=True, log_outcome=True)
        p.assert_called()