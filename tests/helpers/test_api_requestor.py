import pytest

import codepost.api_requestor as _ar

TARGET_MODULE = _ar.__name__

class TestAPIRequestor:

    FAKE_API_KEY = "a"*40
    FAKE_API_KEY_2 = "b"*40
    FAKE_APP_INFO = {
        "name":    "FakeProg",
        "url":     "https://fakeprog.io",
        "version": "3.0",
    }

    def test_api_key_from_init(self, mocker):
        mocker.patch("{}._config.validate_api_key".format(TARGET_MODULE))
        obj = _ar.APIRequestor(api_key=self.FAKE_API_KEY)
        assert obj.api_key == self.FAKE_API_KEY

    def test_api_key_from_configcall(self, mocker):
        mocker.patch("{}._config.configure_api_key".format(TARGET_MODULE),
                     return_value=self.FAKE_API_KEY)
        obj = _ar.APIRequestor()
        assert obj.api_key == self.FAKE_API_KEY

    def test_api_key_setter(self, mocker):
        mocker.patch("{}._config.validate_api_key".format(TARGET_MODULE))
        obj = _ar.APIRequestor()
        obj.api_key = self.FAKE_API_KEY
        assert obj.api_key == self.FAKE_API_KEY

    def test_api_key_del(self, mocker):
        mocker.patch("{}._config.validate_api_key".format(TARGET_MODULE))
        mocker.patch("{}._config.configure_api_key".format(TARGET_MODULE),
                     return_value=self.FAKE_API_KEY_2)

        obj = _ar.APIRequestor(self.FAKE_API_KEY)
        assert obj.api_key == self.FAKE_API_KEY
        assert obj._api_key == self.FAKE_API_KEY

        del obj.api_key
        assert obj.api_key == self.FAKE_API_KEY_2
        assert obj._api_key is None

    def test_app_info(self):
        assert (
            _ar.APIRequestor._format_app_info(**self.FAKE_APP_INFO) ==
            "{name}/v{version} ({url})".format(**self.FAKE_APP_INFO)
        )

    def test_build_headers(self, mocker):
        mocker.patch("{}.codepost".format(TARGET_MODULE), app_info=self.FAKE_APP_INFO)
        headers = _ar.APIRequestor._build_headers(
            api_key=self.FAKE_API_KEY,
            method="POST"
        )
        assert "Authorization" in headers
        assert "Content-Type" in headers
        assert headers.get("Authorization") == "Token {}".format(self.FAKE_API_KEY)
        assert headers.get("Content-Type") == "application/json"

    def test_request(self, mocker):
        obj = _ar.APIRequestor()
        obj._client = mocker.Mock(
            request=mocker.Mock(return_value=mocker.Mock(status_code=200)))
        assert obj._request(endpoint="", method="POST")

    def test_request_error(self, mocker):
        obj = _ar.APIRequestor()
        obj._client = mocker.Mock(
            request=mocker.Mock(return_value=mocker.Mock(status_code=404)))
        obj._handle_request_error = mocker.Mock()
        obj._request(endpoint="", method="POST", data=dict(), api_key=self.FAKE_API_KEY)
        obj._handle_request_error.assert_called()

