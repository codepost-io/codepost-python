#!/usr/bin/env python3
##########################################################################
# codePost upload methods and classes
#
# DATE:    2019-02-12
# AUTHOR:  codePost (team@codepost.io)
#
##########################################################################

from __future__ import print_function # Python 2

#####################
# Python dependencies
#
import sys as _sys

#######################
# External dependencies
#
import requests as _requests

####################
# Local dependencies
#
from . import util as _util

from .util import DocEnum as _DocEnum
from .util import urlencode as _urlencode
from .util import urlquote as _urlquote

from .util import BASE_URL

from . import errors as _errors

from . import helpers as _helpers

from .helpers import get_file as _get_file
from .helpers import post_file as _post_file
from .helpers import delete_file as _delete_file

from .helpers import get_submission_by_id as _get_submission_by_id
from .helpers import post_submission as _post_submission
from .helpers import delete_submission as _delete_submission
from .helpers import unclaim_submission as _unclaim_submission

from .helpers import remove_students_from_submission as _remove_students_from_submission
from .helpers import get_assignment_submissions as _get_assignment_submissions
from .helpers import set_submission_students as _set_submission_students
from .helpers import _submission_list_is_unclaimed as _submission_list_is_unclaimed

from .helpers import remove_comments as _remove_comments

##########################################################################


_logger = _util.get_logger(__name__)

##########################################################################


class UploadModes(_DocEnum):
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


DEFAULT_UPLOAD_MODE = UploadModes.CAUTIOUS

##########################################################################


def _upload_submission_filediff(api_key, submission_info, newest_files, mode=DEFAULT_UPLOAD_MODE):

    # Retrieve a submission's existing files
    existing_files = {
        file["name"]: file
        for file in [
            _get_file(api_key=api_key, file_id=file_id)
            for file_id in submission_info["files"]
        ]
    }

    # Compute files that were added
    added_file_ids = []

    # Flag to determine whether to do the post-modification actions
    submission_was_modified = False

    for file in newest_files:

        # Check if file matches existing ones (by matching name and extension)
        if file["name"] in existing_files and existing_files[file["name"]]["extension"] == file["extension"]:

            if mode.value["updateExistingFiles"]:

                # FIXME: use hashing/robust method of comparing files

                # Ignore newlines when comparing files, to avoid a trailing newline
                # registering as a difference

                data_existing = existing_files[file["name"]]["code"].replace(
                    "\n", "")
                data_new = file["code"].replace("\n", "")

                if data_existing != data_new:

                    submission_was_modified = True

                    _logger.info(
                        "Replacing contents of {} (note: all comments will be deleted)")

                    try:
                        _delete_file(api_key=api_key,
                                    file_id=existing_files[file["name"]]["id"])

                        file_obj = _post_file(
                            api_key=api_key,
                            submission_id=submission_info["id"],
                            filename=file["name"],
                            content=file["code"],
                            extension=file["extension"]
                        )
                    except:
                        raise _errors.UploadError(
                            message="Unexpected error while replacing a file.",
                            # Additional fields
                            api_key=api_key,
                            assignment_id=submission_info.get("assignment"),
                            submission_id=submission_info.get("id"),
                            file_ids=added_file_ids,
                        )

                    if file_obj != None and file_obj.get("id", None) != None:
                        added_file_ids.append(file_obj["id"])

        else:

            if mode.value["addFiles"]:

                submission_was_modified = True
                _logger.info("Adding file {}.".format(file["name"]))

                try:
                    file_obj = _post_file(
                        api_key=api_key,
                        submission_id=submission_info["id"],
                        filename=file["name"],
                        content=file["code"],
                        extension=file["extension"]
                    )
                except:
                    raise _errors.UploadError(
                        message="Unexpected error while adding a file.",
                        # Additional fields
                        api_key=api_key,
                        assignment_id=submission_info.get("assignment"),
                        submission_id=submission_info.get("id"),
                        file_ids=added_file_ids,
                    )

                if file_obj != None and file_obj.get("id", None) != None:
                    added_file_ids.append(file_obj["id"])

    # Delete files in existing_files but not in newest_files, if instructed to do so
    if mode.value["deleteUnspecifiedFiles"]:
        newest_files_names = [x["name"] for x in newest_files]
        for file in existing_files:
            if file not in newest_files_names:
                _logger.info(
                        ("Deleting file {}, since it was not specified in the " +
                         "upload and deleteUnspecifiedFiles is True.").format(file))
                _delete_file(
                    api_key=api_key,
                    file_id=existing_files[file]["id"]
                )
                submission_was_modified = True

    if not submission_was_modified:
        _logger.info("Nothing to add or update, submission was left unchanged.")

    return submission_was_modified

##########################################################################


def upload_submission(api_key, assignment, students, files, mode=DEFAULT_UPLOAD_MODE):

    assignment_id = assignment.get("id", 0)

    # Retrieve all existing submissions associated with the students

    existing_submissions = {}

    for student in students:
        submissions = _get_assignment_submissions(
            api_key=api_key,
            assignment_id=assignment_id,
            student=student
        )

        for submission in submissions:
            existing_submissions[submission["id"]] = submission

    # Check to see if there is a collision

    if len(existing_submissions) == 0:

        # CASE 1: No existing submission => create a new submission
        try:
            return _post_submission(
                api_key=api_key,
                assignment_id=assignment_id,
                students=students,
                files=files
            )
        except _errors.UploadError as e:
            if not mode.value["allowPartial"]:
                e.force_cleanup()
            raise e
        # END CASE 1

    # There is at least one (maybe more) existing submissions

    # First check the modes to determine whether to proceed.
    if not mode.value["updateIfExists"]:
        raise _errors.UploadError(
            """
            At least one submission already exists, and 'updateIfExists' is false,
            so interrupting upload. {} {} {}
            """.format(assignment_id, len(existing_submissions), existing_submissions))

    # Check whether any of the existing submissions are claimed.
    if not mode.value["updateIfClaimed"] and _submission_list_is_unclaimed(list(existing_submissions.values())):
        raise _errors.UploadError(
            """
            At least one submission has already been claimed by a grader, and
            'updateIfClaimed' is false, so interrupting upload.
            """)

    # Check whether students will need an update.
    if not mode.value["resolveStudents"]: # pragma: no cover
        # NOTE: It turns out that, as of 2019-06-18, with our current
        # 5 different modes, this block is never executed because:
        #     For all mode:
        #         mode["updateIfExists"] === mode["resolveStudents"]
        # This piece of code is left in case future modes are created.
        if len(existing_submissions) > 1 or set(students) != set(existing_submissions[0]["students"]):
            raise _errors.UploadError(
                """
                There are {} existing submission(s) with a different subset of
                students than those requested. Since 'resolveStudents' is false,
                interrupting upload.
                - Requested students: {}
                - Existing students (on first existing submission): {}
                """.format(
                    len(existing_submissions),
                    students,
                    set(existing_submissions[0]["students"])
                ))

    if len(existing_submissions) > 1:

        # CASE 2: Remove the students that we need to assign to the uploaded submission
        # from their existing submissions

        for submission in existing_submissions:
            changed_submission = _remove_students_from_submission(
                api_key=api_key,
                submission_info=submission,
                students_to_remove=students
            )

            if mode.value["deleteAffectedSubmissions"]:
                _delete_submission(
                    api_key=api_key,
                    submission_id=changed_submission["id"]
                )

        try:
            return _post_submission(
                api_key=api_key,
                assignment_id=assignment_id,
                students=students,
                files=files
            )
        except _errors.UploadError as e:
            if not mode.value["allowPartial"]:
                e.force_cleanup()
            raise e

        # END CASE 2

    # CASE 3: There is exactly one submission.
    submission = list(existing_submissions.values())[0]
    submission_id = submission["id"]

    # Update the submission students to make sure it is what was specified (if we needed
    # to make this change, and it was forbidden, this would already have been caught).
    _set_submission_students(
        api_key=api_key,
        submission_id=submission_id,
        students=students
    )

    # Process the change in files
    submission_was_modified = False
    try:
        submission_was_modified = _upload_submission_filediff(
            api_key=api_key,
            submission_info=submission,
            newest_files=files,
            mode=mode
        )
    except _errors.UploadError as e:
        if not mode.value["allowPartial"]:
            e.force_cleanup()
        raise e

    # Depending on the outcome of the file changes, proceed with the finishing actions
    if submission_was_modified:

        if mode.value["removeComments"]:
            _remove_comments(
                api_key=api_key,
                submission_id=submission_id
            )

        if mode.value["doUnclaim"]:
            _unclaim_submission(
                api_key=api_key,
                submission_id=submission_id
            )

    # Return updated submission dictionary (equivalent to what post_submission would
    # return in the above exit paths)
    submission = _get_submission_by_id(api_key=api_key, submission_id=submission_id)
    return submission

##########################################################################
