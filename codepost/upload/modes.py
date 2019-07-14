# =============================================================================
# codePost v2.0 SDK
#
# ERRORS SUB-MODULE
# =============================================================================

# Local imports
from ..util import misc as _misc

# =============================================================================

class UploadModes(_misc.DocEnum):
    """
    Describes all possible predefined upload modes for codePost's upload
    methods.
    """

    CAUTIOUS = {
        "allowPartial": False,
        "updateIfExists": False,
        "updateIfClaimed": False,
        "resolveStudents": False,

        "addFiles": False,
        "updateExistingFiles": False,
        "deleteUnspecifiedFiles" : False,

        "removeComments": False,
        "doUnclaim": False,
        "deleteAffectedSubmissions": False
    }, """
    With the 'Cautious' mode: If a submission already exists for this
    (student, assignment) pair (including partners), then cancel the
    upload. If no such submission exists, create it.
    """

    EXTEND = {
        "allowPartial": False,
        "updateIfExists": True,
        "updateIfClaimed": False,
        "resolveStudents": True,

        "addFiles": True,
        "updateExistingFiles": False,
        "deleteUnspecifiedFiles" : False,

        "removeComments": False,
        "doUnclaim": False,
        "deleteAffectedSubmissions": False
    }, """
    With the 'Extend' mode: If a submission already exists for this
    (student, assignment) pair (including partners), then check to
    see if any files (key = name) in the upload request are not
    linked to the existing submission. If so, add these files to the
    submission. This mode does not unclaim a submission upon
    successful extension.
    """

    DIFFSCAN = {
        "allowPartial": False,
        "updateIfExists": True,
        "updateIfClaimed": False,
        "resolveStudents": True,

        "addFiles": True,
        "updateExistingFiles": True,
        "deleteUnspecifiedFiles" : False,

        "removeComments": False,
        "doUnclaim": False,
        "deleteAffectedSubmissions": False
    }, """
    With the 'DiffScan' mode: If a submission already exists for this
    (student, assignment) pair (including partners), compare the
    contents of uploaded files with their equivalent in the request body
    (key = (name, extension), value = code). If any files do not match,
    overwrite the existing files with their equivalent version in the
    request body. If no matching file exists in the submission, add it
    (same behavior as the 'Extend' mode). If any existing files are
    overwritten, clear comments on these files. This mode does not
    unclaim a submission upon successful extension.
    """

    OVERWRITE = {
        "allowPartial": False,
        "updateIfExists": True,
        "updateIfClaimed": True,
        "resolveStudents": True,

        "addFiles": True,
        "updateExistingFiles": True,
        "deleteUnspecifiedFiles" : True,

        "removeComments": True,
        "doUnclaim": True,
        "deleteAffectedSubmissions": True
    }, """
    With the 'Overwrite' mode: If a submission already exists for this
    (student, assignment) pair (including partners), overwrite it with
    the contents of the request. Keep the existing submission linked to
    any partners not included in the request. If at least one file is
    either added or updated, then: Delete any existing comments and
    unclaim the submission (set the `grader` field of the submission to
    `None`).
    """

    PREGRADE = {
        "allowPartial": False,
        "updateIfExists": True,
        "updateIfClaimed": False,
        "resolveStudents": True,

        "addFiles": True,
        "updateExistingFiles": True,
        "deleteUnspecifiedFiles" : True,

        "removeComments": True,
        "doUnclaim": False,
        "deleteAffectedSubmissions": True
    }, """
    If a submission has not been claimed, overwrite it.
    """

# =============================================================================

# Global submodule constants
DEFAULT = UploadModes.CAUTIOUS

# =============================================================================
