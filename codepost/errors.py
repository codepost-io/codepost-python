# =============================================================================
# codePost v2.0 SDK
#
# ERRORS SUB-MODULE
# =============================================================================

from __future__ import print_function # Python 2

# Python stdlib imports


# Local imports
from .util import misc as _misc

from .util.misc import _make_f
from .util.config import SETTINGS_URL

# =============================================================================

# Replacement f"..." compatible with Python 2 and 3
_f = _make_f(globals=lambda: globals(), locals=lambda: locals())

# =============================================================================

# Global submodule constants
SUPPORT_EMAIL = "team@codepost.io"

SUPPORT_MESSAGE = _f(
    "Please write us at {SUPPORT_EMAIL} if you have any questions.")

RESPONSE_TEMPLATE = (
    """
    ===========================================================================
    URL:     {response.url}
    Status:  {response.status_code}
    Content: {response.content:.80}
    ===========================================================================
    """)

_ERROR_NONFIELD = "non_field_errors"

# =============================================================================

class TemplatedRuntimeError(RuntimeError):
    """
    Generic unspecified run-time error within the codePost SDK, of which the
    default message is specified by the class attribute `DEFAULT_MESSAGE`.
    """

    DEFAULT_MESSAGE = "codePost Runtime Error."

    def __init__(self, message=None, **kwargs):
        """
        Initialize the run-time error, optionally with a specific message.
        """
        if message == None:
            message = _f(
                s=self.DEFAULT_MESSAGE,
                **kwargs
            )

        super(TemplatedRuntimeError, self).__init__(message)

# =============================================================================

class APIError(TemplatedRuntimeError):
    """
    Unspecified run-time error with the codePost API, as reported by an HTTP
    status code.
    """

    STATUS_CODE = None

    DEFAULT_MESSAGE = "codePost API Runtime Error."

    def __init__(self, message=None, response=None, **kwargs):
        super(APIError, self).__init__(
            message=message,
            response=response,
            **kwargs
        )

        self._response = response

    @property
    def response(self):
        return self._response

    @property
    def status_code(self):
        if self._response:
            return self._response.status_code

# =============================================================================

class UnknownAPIError(APIError):
    """
    Unknown server-side API run-time error.
    """

    STATUS_CODE = [500]

    DEFAULT_MESSAGE = """
        UNKNOWN SERVER ERROR (API-level codePost Error).
        {RESPONSE_TEMPLATE}
        A call to the codePost API failed unexpectedly with an HTTP 500
        server error. The causes of this error are unknown: Please try
        again, and if the problem persists, you may have found a bug,
        and we invite you to contact us at:
            {SUPPORT_EMAIL}

        Thank you!
        """

class NotFoundAPIError(APIError):
    """
    API run-time error due to an attempt to access a resource (course,
    assignment, submission, etc.) that does not exist.
    """

    STATUS_CODE = [404]

    DEFAULT_MESSAGE = """
        API RESOURCE DOES NOT EXIST (API-level codePost Error).
        {RESPONSE_TEMPLATE}
        A call to the codePost API failed unexpectedly with an HTTP 404
        error. It seems you are trying to access a resource that does
        not exist (or does not yet exist).

        {SUPPORT_MESSAGE}
        """

class AuthenticationAPIError(APIError):
    """
    API run-time error due to a missing, expired or invalid API key.
    """

    STATUS_CODE = [401]

    DEFAULT_MESSAGE = """
        INVALID TOKEN, AUTHENTICATION ERROR (API-level codePost Error).
        {RESPONSE_TEMPLATE}
        A call to the codePost API failed unexpectedly with an HTTP 401
        error. There are three likely causes to this:

        1) You did not provide an authorization header to authenticate
            your API request. In the Python SDK, you may do so in the
            following way:
            ```
            import codepost
            codepost.configure_api_key(<your API key>)
            ```

        2) You did provide an API key, but it was incorrect. If you are
            a registered codePost user, you can retrieve a key, allowing
            you to manipulate all courses you are an administrator of,
            by going in your Settings page, as a logged in user:
                {SETTINGS_URL}

        3) You did provide an API key, but it has expired or been
            replaced by a more recent key. If that is the case, check
            your Settings page to make sure you have the most recent
            version.

        {SUPPORT_MESSAGE}
        """

class AuthorizationAPIError(APIError):
    """
    API run-time error due to a valid API key which does not have the required
    permissions to access/alter the specified resource (course, assignment,
    submission, etc.).
    """

    STATUS_CODE = [403]

    DEFAULT_MESSAGE = """
        AUTHORIZATION ERROR (API-level codePost Error).
        {RESPONSE_TEMPLATE}
        While you seem to have authenticated properly using the method
        of your choice, the identity you have authenticated as does not
        have access to the resource you are trying to access. Please
        check to make sure the account you are using to make the codePost
        API calls has administrative access to the resources you are
        trying to access or manipulate.

        {SUPPORT_MESSAGE}
        """

class BadRequestAPIError(APIError):
    """
    API run-time error due to a bad request. This can have a variety of causes,
    including but not limited to:

    - missing fields (for each API resource, some fields are required);

    - unexpected fields (additional fields provided which do not belong to the
      resource being accessed);

    - duplicate object (attempting to create an object which already exists).
    """

    STATUS_CODE = [400]

    DEFAULT_MESSAGE = """
        BAD REQUEST ERROR (API-level codePost Error).
        {RESPONSE_TEMPLATE}
        The codePost API request you have made is incorrect. The response
        attempts to narrow down the reason for this error:

            {detailed_reason}

        {SUPPORT_MESSAGE}
        """

    def __init__(self, message=None, response=None, **kwargs):

        # compute error message
        detailed_reason = ""
        if response:
            response_dict = response.json
            missing_keys = list(response_dict.keys())
            if _ERROR_NONFIELD in missing_keys:
                detailed_reason = (
                    "The parameter(s) you have provided " +
                    "describe an existing resource.")
            else:
                detailed_reason = (
                    "Missing fields: {}.".format(missing_keys))

        super(BadRequestAPIError, self).__init__(
            message=message,
            response=response,
            detailed_reason=detailed_reason,
            **kwargs)

# =============================================================================

API_ERRORS = [
    BadRequestAPIError,     # 400
    AuthenticationAPIError, # 401
    AuthorizationAPIError,  # 403
    NotFoundAPIError,       # 404
    UnknownAPIError,        # 500
]

def handle_api_error(status_code, response, message=None, **kwargs):
    # Look for most appropriate exception
    for exception in API_ERRORS:
        handled_status_codes = getattr(exception, "STATUS_CODE", None)
        if handled_status_codes and status_code in handled_status_codes:
            raise exception(message=message, response=response, **kwargs)

    # Default API error
    if status_code >= 400:
        raise APIError(message=message, response=response, **kwargs)

# =============================================================================

class StaticObjectError(TemplatedRuntimeError):
    """
    Run-time error due to a static API object being used as an instantiated API
    object. Only use the `create`, `retrieve`, `update` and `delete` methods on
    top-level `codepost.*` objects.
    """

    DEFAULT_MESSAGE = """
        STATIC OBJECT ERROR.
        You are trying to use a static API object as though it were an instance
        object. Please either create or retrieve an instance object, or only
        use static API method calls (that is the `create`, `retrieve`, `update`
        and `delete` methods on top-level `codepost.*` objects.)

        {SUPPORT_MESSAGE}
        """

# =============================================================================

class UploadError(TemplatedRuntimeError):
    """
    Run-time error related to the upload of a submission.
    """

    DEFAULT_MESSAGE = """
        UPLOAD ERROR.
        """

# =============================================================================

